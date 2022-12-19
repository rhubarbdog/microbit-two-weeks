#
# Author  - Phil Hall, November 2022
# License - MIT
#

from microbit import *
import radio
import time
import random
import math

# Message IDs
# 2 - message from xclient to xserver
# 1 - message from xserver to xclient
# 0 - global message to all xservers

# Messages Received
# 1, -1 (enroll me), machine_id
# 1, 1 (button presses), player, buttons pressed

# Messages Sent
#  2, player, machine_id
#  2, -1, machine_id, too many players
#  2, -2, machine_id, game already started 
#  2, player, 1, winner
#  2, player, 2, screen, player x, player y, compass
#
#  0, Ready
#  0, Game Over

wall = ("wwwwwwwwwwwwwwwwwwww" * 5) + "ww"
screen = ["w" + ("..,,..,,..,,..,,..,," * 5) + "w", \
          "w" + ("..,,..,,..,,..,,..,," * 5) + "w", \
          "w" + (",,..,,..,,..,,..,,.." * 5) + "w", \
          "w" + (",,..,,..,,..,,..,,.." * 5) + "w"]
screen = [wall] + (screen * 25) + [wall]

root_2_1 = 0.7071067811865475244
snooze = 50
max_players = 20
total_players = 0
max_walls = 200
exit_x = 0
exit_y = 0

radio.config(channel = 14, queue = int(max_players * 1.5), length = 96)
radio.on()

class CrashError(Exception):
    pass

def print_screen():
    loop = 0
    global screen
    for yyy in range(len(screen)):
        for xxx in range(170):
            print(screen[yyy][xxx], end = "")
        print("")
        if loop > 40:
            a = input('?')
            loop = 0

        loop += 1

def plot(xxx, yyy, item):
    global screen
    screen = screen[:yyy] + \
        [screen[yyy][:xxx] + item + screen[yyy][xxx + 1:]] + screen[yyy + 1:]

def absolute(number):
    if number < 0.0:
        return -number
    return number

def ticker(index):
    clocks = (Image.CLOCK12, Image.CLOCK3, Image.CLOCK6, Image.CLOCK9)
    iii = index + 1
    if iii >= len(clocks):
        iii = 0

    return (clocks[index], iii) 
            
# enroll players for 2 minutes
begin = time.ticks_ms()
display.scroll('Two Weeks', wait = False, loop = True)
while True:
    message = radio.receive()
    if message is None:
        sleep(snooze)
    else:
        message = eval("(" + message + ")")
        # enrollment message from a client
        if message[0] == 1 and message[1] == -1:
            if total_players == max_players:
                radio.send("2,-1," + str(message[2]) + ",'Sorry," \
                           " too many players'")
            else:
                radio.send("2," + str(total_players) + "," + str(message[2]))
                total_players += 1
                
    two_mins = 0.5 * 1000 * 60
    difference = time.ticks_diff(time.ticks_ms(), begin)
    if  difference >= two_mins:
        break

# populate map with some walls
for _ in range(20 + random.randrange(max_walls - 20)):
    length = random.randrange(10) + 1
    xxx = random.randrange(len(screen[0]))
    yyy = random.randrange(len(screen))
    vertical = random.choice((True, False))

    if vertical and yyy + length >= len(screen):
        yyy = len(screen) - length
    elif not vertical and xxx + length >= len(screen[0]):
        xxx = len(screen[0]) - length

    for i in range(length):
        if vertical:
            plot(xxx, yyy + i, 'w')
        else:
            plot(xxx + i, yyy, 'w')
            
# place the exit
size = 30
while True:
    xxx = random.randrange(size)
    yyy = random.randrange(size)

    xxx += (len(screen[0]) - size) // 2
    yyy += (len(screen) - size) //  2

    if screen[yyy][xxx] in '.,':
        plot(xxx, yyy, 'X')
        exit_x = xxx
        exit_y = yyy
        break

# calculate player starting positions
size = 15
player_list = []
for _ in range(total_players):
    while True:
        xxx = random.random() * (size  + 1) * random.choice((1, -1))
        yyy = random.random() * (size  + 1) * random.choice((1, -1))

        if xxx < -size or xxx > size or yyy < -size or yyy > size:
            continue

        if xxx < 0:
            xxx = len(screen[0]) - 1 + xxx
        if yyy < 0:
            yyy = len(screen) - 1 + yyy

        if screen[int(yyy + 0.5)][int(xxx + 0.5)] in '.,':
            player_list.append((xxx, yyy))
            break

# Play the game
if total_players > 0:
    radio.send("0,'Ready'")

winner = -1
loops = 0
index = 0
players_todo = []
for i in range(total_players):
    players_todo.append(i)
    
while total_players > 0:
    if loops % 10 == 0:
        image, index = ticker(index)
    display.show(image)
    sleep(snooze)
    
    if winner != -1:
        winner = -2

     # produce a screen for every player and send it out
    for index in players_todo:
        tmp = player_list[index]
        player_x = int(tmp[0] + 0.5)
        player_y = int(tmp[1] + 0.5)

        begin_x = player_x - 4
        begin_y = player_y - 4
        if begin_x < 0:
            begin_x = 0
        if begin_y < 0:
            begin_y = 0

        end_x = begin_x + 8
        end_y = begin_y + 8
        if end_x >= len(screen[0]):
            end_x = len(screen[0])
            begin_x = end_x - 8
        if end_y >= len(screen):
            end_y = len(screen)
            begin_y = end_y - 8

        message = ""
        added = -1
        for yyy in range(begin_y, end_y):
            line = screen[yyy][begin_x: end_x]
            for being in player_list:
                if yyy == int(being[1] + 0.5) and \
                   begin_x <= int(being[0] + 0.5) and \
                   end_x > int(being[0] + 0.5) and \
                   player_list.index(being) != index:
                    added = index
                    line = line[:int(being[0] + 0.5) - begin_x] + 'p' + \
                        line[int(being[0] + 0.5) + 1 - begin_x:]
            message += line
            
        # calculate compass
        diff_x = exit_x - player_x
        diff_y = exit_y - player_y

        if diff_x == 0 and diff_y == 0:
            clock = -2
            if winner == -1:
                radio.send("2," + str(index) + ",1,'Winner'")
                winner = index
        elif absolute(diff_x) < 4 and absolute(diff_y) < 4:
            clock = -1
        elif diff_x == 0:
            if diff_y < 0:
                clock = 0
            else:
                clock = 6
        elif diff_y == 0:
            if diff_x < 0:
                clock = 9
            else:
                clock = 3
        else:
            ratio = diff_x / diff_y
            if ratio < 0:
                ratio = -ratio
                
            last_ratio = 0
            theta = 0
            for i in range(5, 90, 5):
                theta = i
                tangent = math.tan(math.radians(theta))
                if ratio >= last_ratio and ratio <= tangent:
                    break
                last_ratio = tangent

            if diff_x < 0 and diff_y < 0:
                clock = 12 - int(4 * theta / 90)
                if clock == 12:
                    clock = 0
            elif diff_x < 0:
                clock = 6 + int(4 * theta / 90)
            elif diff_y < 0:
                clock = int(4 * theta / 90)
            else:
                clock = 6 - int(4 * theta / 90)
                        
        radio.send("2," + str(player_list.index(tmp)) + ",2,'" + message + \
                   "'," + str(player_x - begin_x) + "," + \
                   str(player_y - begin_y) + "," + str(clock))

    # game over sent the wining screen to xserver so quit
    if winner == -2:
        radio.send("0, 'Game Over'")
        break
    # collect and process all clients keystrokes
    players_todo = []
    if winner != -1:
        players_todo.append(winner)

    while True:
        message = radio.receive()
        if message is None:
            break
        else:
            message = eval("(" + message + ")")
            
            if message[0] == 1 and message[1] == 1:
                player = player_list[message[2]]
                dx = 0
                dy = 0
                if 'u' in message[3] and 'd' in message[3]:
                    pass
                elif 'u' in message[3]:
                    dy = -1
                elif 'd' in message[3]:
                    dy = 1

                if 'l' in message[3] and 'r' in message[3]:
                    pass
                elif 'l' in message[3]:
                    dx = -1
                elif 'r' in message[3]:
                    dx = 1

                if dy != 0 and dx != 0:
                    dy *= root_2_1
                    dx *= root_2_1

                if int(player[0] + dx + 0.5) < 0 or \
                   int(player[0] + dx + 0.5) > len(screen[0]) - 1:
                    dx = 0
                if int(player[1] + dy + 0.5) < 0 or \
                   int(player[1] + dy + 0.5) > len(screen) - 1:
                    dy = 0

                collide = False
                if not screen[int(player[1] + dy + 0.5)] \
                   [int(player[0] + dx + 0.5)] in ',.X':
                    collide = True

                if not collide:
                    for being in player_list:
                        if int(being[0] + 0.5) == int(player[0] + dx + 0.5) \
                           and int(being[1] + 0.5) == \
                           int(player[1] + dy + 0.5) and \
                           player_list.index(being) != message[2]:
                            collide = True
                            break

                if collide:
                    dx = 0
                    dy = 0
                    
                for i in players_todo:
                    if added ==  i:
                        added = -1
                        break
                    
                i = player_list.index(player)
                if not (winner != -1 and winner == i) or added != -1:
                    players_todo.append(i)
                    player_list = player_list[:i] + \
                        [[player[0] + dx, player[1] + dy]] +\
                        player_list[i + 1:]
            elif message[0] == 1 and message[1] == -1:
                radio.send("2,-2," + str(message[2]) + \
                           ", ' Game already started'")
            else:
                raise CrashError

    if loops == 20000:
        loops = 0

    loops += 1


radio.off()
flipflop = False
while True:
    if flipflop:
        display.show(Image.HEART)
    else:
        display.show(Image.HEART_SMALL)

    flipflop = not flipflop
    sleep(750)
