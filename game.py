#
# Author  - Phil Hall, November 2022
# License - MIT
#

from microbit import *
import music
import radio
import machine

snooze = 50
max_players = 20
SCREEN = 5
# Message IDs
# 2 - message from host to client
# 1 - message from client to host
# 0 - global message to all clients

# Messages Sent
# 1, -1 (enroll me), machine_id, screen size
# 1, 1 (button presses), player, buttons pressed

# Messages Received
#  2, player, 0, machine_id
#  2, -1, machine_id, too many players
#  2, -2, machine_id, game already started 
#  2, player, 1, winner
#  2, player, 2, screen, player x, player y, compass
#
#  0, Ready
#  0, Game Over



# pallet dictionary
# (other) players, grass colour one , grass colour two
# enemy, wall, the winning spot
map_colors = {'p' : 3, ',' : 1, '.' : 0, 'w' : 9, 'X' : 5}

class CrashError(Exception):
    pass

radio.config(channel = 14, queue = int(max_players * 1.5), length = 96)
radio.on()

def plot(xxx, yyy, ilume):
    display.set_pixel(xxx, yyy, ilume)

display.scroll("Two Weeks")
mach_id = machine.unique_id()
radio.send("1,-1," + str(mach_id) + "," + str(SCREEN))

player = None
die = False

# Enroll a new client
while True:
    message = radio.receive()
    if message is None:
        sleep(snooze)
    else:
        message = eval("(" + message + ")")
        print(player, str(message))

        # global message 
        if message[0] == 0:
            display.scroll(message[1], wait = False)
        # message to a client is it me?
        elif message[0] == 2:
            if str(mach_id) == str(message[2]):
                player = message[1]
                if player == -1 or player == -2:
                    music.play(["c2:2"], pin2, wait = False)
                    display.scroll(message[3])
                    die = True
                    break
                break

if not die:
    display.scroll(" Player " + str(player + 1), wait = False, loop = True)

# monitor the radio for the go message
while not die:
    message = radio.receive()
    if message is None:
        sleep(snooze)
    else:
        message = eval("(" + message + ")")

        #global message
        if message[0] == 0:
            if message[1] == "Ready":
                for i in range(5):
                    music.play(["c4:2"], pin2, False)
                    display.show(str(5 - i))
                    sleep(1000)
                break
            else:
                display.scroll(message[1], wait = False)
        # message to this client not now!!!
        elif message[0] == 2 and message[1] == player:
            raise CrashError("Crash Error, packet out of sequence.")


# play the game - main loop
loops = 0
winner = 0
ilume = 7
delta = -1
flash = True
buttons = ""

while not die:
    if winner == 1:
        winner = 2

    sleep(snooze)
    screen = None
    # get all messages until my screen appears
    while True:
        message = radio.receive()
        if message is None:
            break
        else:
            message = eval("(" + message + ")")

            # global message, this must be game over
            if message[0] == 0:
                radio.off()
                display.scroll(message[1])
                display.show(Image.SAD_FACE)
                while True:
                    sleep(1000)                
            # winner
            elif message[0] == 2 and message[1] == player:
                if message[2] == 1:
                    music.play(music.POWER_UP, pin2, False)
                    display.scroll(message[3], wait = False)
                    winner = 1
                else:
                    player_x = message[4]
                    player_y = message[5]
                    compass = message[6]
                    screen = []
                    for i in range(SCREEN):
                        screen.append(message[3][i * SCREEN: (i + 1) * SCREEN])

                    break

    # draw screen, compass and player
    if winner == 0 and not screen is None and not pin16.read_digital() == 0:
        for xxx in range(SCREEN):
            for yyy in range(SCREEN):
                print(xxx, yyy, screen[yyy][xxx])
                if screen[yyy][xxx] != 'X':
                    plot(xxx, yyy, map_colors[screen[yyy][xxx]])
                else:
                    if flash:
                        plot(xxx, yyy, map_colors[screen[yyy][xxx]])
                    else:
                        plot(xxx, yyy, 0)

        plot(player_x, player_y, ilume)

    if loops % 2 == 0:
        ilume += delta
        if ilume < 3:
            delta = 1
        if ilume > 6:
            delta = -1

    if loops % 5 == 0:
        flash = not flash
    
    if winner == 1:
        sleep(5000)

    if pin16.read_digital() == 0 or winner == 1:
        if compass == -2:
            display.show(Image.HAPPY)
        elif compass == -1:
            display.show(Image.SQUARE)
        else:
            display.show(Image.ALL_CLOCKS[compass])
        
    # game over
    if winner == 2:
        break
    
    # detect buttons, up, down, left, right
    if winner == 0:
        if pin8.read_digital() == 0:
            if not 'u' in buttons:
                buttons += 'u'
        if pin14.read_digital() == 0:
            if not 'd' in buttons:
                buttons += 'd'
        if pin12.read_digital() == 0:
            if not 'l' in buttons:
                buttons += 'l'
        if pin13.read_digital() == 0:
            if not 'r' in buttons:
                buttons += 'r'

    # send buttons to server
    if loops % 15 == 0 and buttons != "":
        radio.send("1,1," + str(player) + ",'" + buttons + "'")
        buttons = ""

    if loops == 30000:
        loops = 0
        
    loops += 1


radio.off()

