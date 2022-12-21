#
# Author  - Phil Hall, November 2022
# License - MIT
#

from microbit import display, Image, sleep
import radio
import random
import math
import gc

# Message IDs
# 2 - message from host to client
# 1 - message from client to host
# 0 - global message to all clients

# Messages Received
# 1, -1 (enroll me), machine_id, screen size
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

# Player tuple
# ( screen size, xxx, yyy, last_x, last_y )

class CrashError(Exception):
    pass
# grass, alternate grass, wall, exit, player
MAP_DICT = ".,wXp" 
SCREEN_X = 102
SCREEN_Y = 102
screen = bytearray(SCREEN_X * SCREEN_Y)

ROOT_2_1 = 0.7071067811865475244
snooze = 50
max_players = 20
total_players = 0
player_list = []
max_walls = 200
exit_x = 0
exit_y = 0
winner = -1
loops = 0
index = 0
    
radio.config(channel = 14, queue = int(max_players * 1.5), length = 96)
radio.on()
        
def print_screen():
    loop = 0
    global screen
    for yyy in range(SCREEN_Y):
        for xxx in range(max(SCREEN_X,170)):
            print(MAP_DICT[screen[yyy * SCREEN_X + xxx]], end = "")
        print("")
        if loop > 40:
            a = input('?')
            loop = 0

        loop += 1

def plot(xxx, yyy, item):
    global screen
    screen[yyy * SCREEN_X + xxx] = item
    
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
            
# enroll players for 30 seconds
loops = 0
display.scroll('Two Weeks', wait = False, loop = True)
while loops < 600:
    message = radio.receive()
    if not message is None:
        message = eval("(" + message + ")")
        # enrollment message from a client
        if message[0] == 1 and message[1] == -1:
            if total_players == max_players:
                radio.send("2,-1," + str(message[2]) + ",'Sorry," \
                           " too many players'")
            else:
                radio.send("2," + str(total_players) + "," + str(message[2]))
                total_players += 1
                player_list.append((message[3], 0.0, 0.0, -2000.0, -2000.0))

    sleep(snooze)
    loops += 1
    
# initialise map - draw the grass
flipflop = 0
for yyy in range(1, SCREEN_Y - 1):
    for xxx in range(1, SCREEN_X - 1):
        if ((xxx // 2)  % 2 == 0 and (yyy // 2) % 2 == 0) or \
           ((xxx // 2)  % 2 != 0 and (yyy // 2) % 2 != 0):
            plot(xxx, yyy, 0)
        else:
            plot(xxx, yyy, 1)


# draw walls round the edge
for i in range(SCREEN_Y):
    plot(0, i, 2)
    plot(SCREEN_X - 1, i, 2)
for i in range(SCREEN_X):
    plot(i, 0, 2)
    plot(i, SCREEN_Y - 1, 2)
    
# and add some random walls
for _ in range(20 + random.randrange(max_walls - 20)):
    length = random.randrange(10) + 1
    xxx = random.randrange(SCREEN_X)
    yyy = random.randrange(SCREEN_Y)
    vertical = random.choice((True, False))

    if vertical and yyy + length >= SCREEN_Y:
        yyy = SCREEN_Y - length
    elif not vertical and xxx + length >= SCREEN_X:
        xxx = SCREEN_X - length

    for i in range(length):
        if vertical:
            plot(xxx, yyy + i, 2)
        else:
            plot(xxx + i, yyy, 2)
            
# place the exit
size = 30
while True:
    xxx = random.randrange(size)
    yyy = random.randrange(size)

    xxx += (SCREEN_X - size) // 2
    yyy += (SCREEN_Y - size) //  2

    if screen[yyy * SCREEN_X + xxx] in (0, 1):
        plot(xxx, yyy, 3)
        exit_x = xxx
        exit_y = yyy
        break

# calculate player starting positions
size = 15
for player in range(total_players):
    while True:
        xxx = random.random() * (size  + 1) * random.choice((1, -1))
        yyy = random.random() * (size  + 1) * random.choice((1, -1))

        if xxx < -size or xxx > size or yyy < -size or yyy > size:
            continue

        if xxx < 0:
            xxx = SCREEN_X - 1 + xxx
    
        if yyy < 0:
            yyy = SCREEN_Y - 1 + yyy

        # ensure all players are on the grass 
        if not screen[int(yyy + 0.5) * SCREEN_X + int(xxx + 0.5)] in (0, 1):
            continue

        # and in different squares
        collide = False
        for i in range(player):
            if int(player_list[i][1] + 0.5) == int(xxx + 0.5) and \
               int(player_list[i][2] + 0.5) == int(yyy + 0.5):
                collide = True
                break

        if collide:
            continue

        player_list = player_list[:player] + \
            [(player_list[player][0], xxx, yyy, \
              player_list[player][3], player_list[player][4])] + \
            player_list[player:]    
        break

# Play the game
gc.collect()
if total_players > 0:
    radio.send("0,'Ready'")

    for i in range(5):
        display.show(str(5 - i))
        sleep(1000)
    sleep(50)

    players_todo = []
    for i in range(total_players):
        players_todo.append(i)

while total_players > 0:
    if loops % 10 == 0:
        image, index = ticker(index)
    display.show(image)
    sleep(snooze)
    gc.collect()
    
    if winner != -1:
        winner = -2

    # produce a screen for every player and send it out
    for index_ in players_todo:
        print(index_, end = ', ')
    
        player_x = int(player_list[index_][1] + 0.5)
        player_y = int(player_list[index_][2] + 0.5)

        begin_x = player_x - player_list[index_][0] // 2
        begin_y = player_y - player_list[index_][0] // 2
    
        if begin_x < 0:
            begin_x = 0
        if begin_y < 0:
            begin_y = 0

        end_x = begin_x + player_list[index_][0]
        end_y = begin_y + player_list[index_][0]
        if end_x > SCREEN_X:
            end_x = SCREEN_X
            begin_x = end_x - player_list[index_][0]
        if end_y > SCREEN_Y:
            end_y = SCREEN_Y
            begin_y = end_y - player_list[index_][0]

        message = ""
        for yyy in range(begin_y, end_y):
            line = ""
            for xxx in range(begin_x, end_x):
                line += MAP_DICT[screen[(yyy * SCREEN_X) + xxx]]
            for being in player_list:
                if player_list[index_] == being:
                    continue
                
                if yyy == int(being[2] + 0.5) and \
                   begin_x <= int(being[1] + 0.5) and \
                   end_x > int(being[1] + 0.5):
                    line = line[:int(being[1] + 0.5) - begin_x] + \
                        MAP_DICT[4] + \
                        line[int(being[1] + 0.5) + 1 - begin_x:]
            message += line

        # calculate compass and detect Winner
        diff_x = exit_x - player_x
        diff_y = exit_y - player_y

        if diff_x == 0 and diff_y == 0:
            clock = -2
            if winner == -1:
                radio.send("2," + str(index_) + ",1,'Winner'")
                winner = index_
        elif absolute(diff_x) < player_list[index_][0] / 2 and \
             absolute(diff_y) < player_list[index_][0] / 2:
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
            for phi in range(5, 90, 5):
                theta = phi
                tangent = math.tan(math.radians(phi))
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

        # send out the screen packet *error*??
        radio.send("2," + str(index_) + ",2,'" + message + \
                   "'," + str(player_x - begin_x) + "," + \
                   str(player_y - begin_y) + "," + str(clock))
        print(index_, end = " | ")

    # game over sent the wining screen to player so quit
    if winner == -2:
        radio.send("0, 'Game Over'")
        break
    
    players_todo = []
    movers = False
    if winner != -1:
        players_todo.append(winner)

    # collect and process all clients keystrokes
    while True:
        message = radio.receive()
        if message is None:
            break
        else:
            message = eval("(" + message + ")")
            
            if message[0] == 1 and message[1] == 1:
            
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
                    dy *= ROOT_2_1
                    dx *= ROOT_2_1

                if int(player_list[message[2]][1] + dx + 0.5) < 0 or \
                   int(player_list[message[2]][1] + dx + 0.5) > SCREEN_X - 1:
                    dx = 0
                if int(player_list[message[2]][2] + dy + 0.5) < 0 or \
                   int(player_list[message[2]][2] + dy + 0.5) > SCREEN_Y - 1:
                    dy = 0

                collide = False
                if not screen[int(player_list[message[2]][2] + dy + 0.5) * \
                              SCREEN_X + \
                              int(player_list[message[2]][1] + dx + 0.5)] in \
                              (0 ,1 , 3):
                    collide = True

                if not collide:
                    for being in player_list:
                        if int(being[1] + 0.5) == \
                           int(player_list[message[2]][1] + dx + 0.5) and \
                           int(being[2] + 0.5) == \
                           int(player_list[message[2]][2] + dy + 0.5) and \
                           player_list.index(being) != message[2]:
                            collide = True
                            break

                if collide:
                    dx = 0
                    dy = 0

                if dy != 0 or dx != 0:
                    movers = True
                    
                if not (winner != -1 and winner == message[2]):
                    players_todo.append(message[2])
                    screen_size = player_list[message[2]][0]
                    xxx = player_list[message[2]][1]
                    yyy = player_list[message[2]][2]
                    last_x = player_list[message[2]][3]
                    last_y = player_list[message[2]][4]
                    if dx != 0 or dy != 0:
                        last_x = xxx
                        last_y = yyy
                        xxx += dx
                        yyy += dy
                    player_list = player_list[:message[2]] + \
                        [(screen_size, xxx, yyy, last_x, last_y)] + \
                        player_list[message[2]:]

            # game started, enrollment too late 
            elif message[0] == 1 and message[1] == -1:
                radio.send("2,-2," + str(message[2]) + \
                           ", ' Game already started'")
            else:
                raise CrashError("Crash Error, packet out of sequence.")

    # make other players appear and disapear from another player's screen
    if movers:
        for index_ in range(total_players):
            if index_ in players_todo:
                continue

            square = player_list[index_][0] * player_list[index_][0]

            for being in player_list[index_:]:
                dx = player_list[index_][1] - being[1]
                dy = player_list[index_][2] - being[2]

                if (dx * dx) + (dy * dy) <= square:
                    players_todo.append(index_)
                    continue

                dx = player_list[index_][3] - being[1]
                dy = player_list[index_][4] - being[2]

                if (dx * dx) + (dy * dy) > square:
                    players_todo.append(index_)
                    continue

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
