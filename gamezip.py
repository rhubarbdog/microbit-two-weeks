#
# Author  - Phil Hall, November 2022
# License - MIT
#

from microbit import *
import neopixel
#import music
import radio
import machine

snooze = 50
max_players = 20
SCREEN = 8
# Message IDs
# 2 - message from host to client
# 1 - message from client to host
# 0 - global message to all clients

# Messages Sent
# 1, -1 (enroll me), machine_id, screen size
# 1, 1 (button presses), player, buttons pressed

# Messages Received
#  2, player, machine_id
#  2, -1, machine_id, too many players
#  2, -2, machine_id, game already started 
#  2, player, 1, winner
#  2, player, 2, screen, player x, player y, compass
#
#  0, Ready
#  0, Game Over

# pallet dictionary
# (other) players, grass colour one , grass colour two
# enemy, wall, This Player
# blank space, the winning spot
map_colors = {'p' : (20, 20, 0), ',' : (1, 4, 1), '.' : (0, 0, 0), \
              'w' : (0, 0, 20), 'P': (15, 0, 0), 'X' : (10, 0, 10)}

class CrashError(Exception):
    pass


radio.config(channel = 14, queue = int(max_players * 1.5), length = 96)
radio.on()
speaker.off()

pin0.write_digital(1)
sleep(20)
pin0.write_digital(0)
zip_leds = neopixel.NeoPixel(pin0, 64)
zip_leds.clear()

def plot(xxx, yyy, color):
    global zip_leds
    zip_leds[xxx + (yyy * SCREEN)] = (color[0], color[1], color[2])

# Begin the game
display.scroll("Two Weeks")
mach_id = machine.unique_id()
radio.send("1,-1," + str(mach_id) + "," + str(SCREEN))

player = None
death = False

# Enroll a new client
while True:
    message = radio.receive()
    if message is None:
        sleep(snooze)
    else:
        message = eval("(" + message + ")")

        # global message 
        if message[0] == 0:
            display.scroll(message[1], wait = False)
        # message to a client is it me?
        elif message[0] == 2:
            if str(mach_id) == str(message[2]):
                player = message[1]
                if player == -1 or player == -2:
                    #music.play(["c2:2"], pin2, wait = False)
                    display.scroll(message[3])
                    death = True
                    break
                break

if not death:
    display.scroll(" Player " + str(player + 1), wait = False, loop = True)

# monitor the radio for the 'Ready' to go message
while not death:
    message = radio.receive()
    if message is None:
        sleep(snooze)
    else:
        message = eval("(" + message + ")")

        #global message
        if message[0] == 0:
            if message[1] == "Ready":
                for i in range(5):
                    #music.play(["c4:2"], pin2, False)
                    display.show(str(5 - i))
                    sleep(1000)
                break
            else:
                display.scroll(message[1], wait = False)
        # message to this client not now!!!
        elif message[0] == 2 and message[1] == player:
            display.scroll("Game server, 'Ready' skipped")
            raise CrashError("CrashError - packet out of sequence.")


# play the game - main loop
loops = 0
winner = 0
buttons = ""

while not death:
    if winner == 1:
        winner = 2

    screen = None
    # get all messages until my screen appears
    while True:
        message = radio.receive()
        if message is None:
            break
        else:
            message = eval("(" + message + ")")
            print(player, str(message))

            # global message, this must be game over
            if message[0] == 0:
                display.scroll(message[1], wait = False, loop = True)
                break
            elif message[0] == 2 and message[1] == player: 
                if message[2] == 1:
                    #music.play(music.POWER_UP, pin2, False)
                    display.scroll(message[3], wait = False)
                    winner = 1
                else:
                    screen = []
                    for i in range(SCREEN):
                        screen.append(message[3][i * SCREEN: (i + 1) * SCREEN])

                    player_x = message[4]
                    player_y = message[5]
                    compass = message[6]
                    break

    # draw screen, compass and player
    if not screen is None:
        for xxx in range(SCREEN):
            for yyy in range(SCREEN):
                plot(xxx, yyy, map_colors[ screen[yyy][xxx] ])

        plot(player_x, player_y, map_colors['P'])
        zip_leds.show()

        if winner == 1:
            sleep(5000)

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
    sleep(snooze)


radio.off()

