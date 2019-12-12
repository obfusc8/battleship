import random
import os
import socket
import time
import winsound
from GameBoard import GameBoard
from Ship import Ship
from PrintText import PrintText

### GAME VARS ###
server_ip = "192.168.86.38"
isPlayer2 = False
animate = True
ccode_view_all = "SATELLITE"
ccode_nuke_all = "NUKE"
ccode_next_hit = "SNIPER"
clearscreen = 'cls'     # uncomment for windows
#clearscreen = 'clear'  # uncomment for linux
# SOUND SETTINGS #
frequency = 500  # Set Frequency To 2500 Hertz
duration = 250  # Set Duration To 1000 ms == 1 second

### HELPER FUCTIONS ###
def autoSet(player):
    for i in range(1,6):
        ship = Ship(i)
        vert = random.randrange(2)
        if vert == 1:
            ship.setDirection("V")
        success = False
        while not success:
            row = random.randrange(10)
            col = random.randrange(10)
            success = player.setShip(row, col, ship)

def makeBool(x):
    if (x == "True"):
        return True
    else:
        return False

def isCorrect(shot):
    if (len(shot) != 2):
        raise Exception()
    if not (shot[0].isalpha() and shot[0].upper() in ['A','B','C','D','E','F','G','H','I','J']):
        raise Exception()
    if not (shot[1].isdigit() and shot[1] in ['0','1','2','3','4','5','6','7','8','9']):
        raise Exception()
    return True

def explosion():
    anime1 = "?<>,.;             "
    anime2 = "     ?<>,.; $%^&*  "
    n = 0
    for i in range(len(anime1)):
        screen = os.system(clearscreen)
        print("\n\n\n\n\n" + str(PrintText(" "*30 +anime1[i])), end="")
        print(PrintText(" "*30 +anime2[i]), end="")
        if i > 12: n = (n+1)%2
        print(PrintText(" "*(30+n) +"  #"), end="")
        print("^"*90)
        time.sleep(.050)
        
### OPENING SCREEN ###
for i in range(0,63,2):
    wipe = os.system(clearscreen)
    temp = "\n" + str(PrintText(" "*i +"#")) + "^"*95
    print(temp)
    time.sleep(.001)

wipe = os.system(clearscreen)
temp = "\n" + str(PrintText("   BATTLESHIP #")) + "^"*95
print(temp)
print()

### SET UP NETWORKING ###           
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = server_ip
port = 9999

# connect to server
try:
    print(" Connecting to the Battleship server... ")
    s.connect((host, port))
    greeting = s.recv(1024).decode('ascii')
    print(" "+ greeting)
    print(" Press ENTER to continue... ")
    input()

    if (greeting.find("PLAYER 1") != -1):
        START = True
    else:
        START = False

    # all good!
    GAMEON = True

    # label connection as the enemy
    enemy = s

except ConnectionResetError:
    print("\n [Connection Reset Error] Try restarting the game...")
    GAMEON = False
except ConnectionAbortedError:
    print("\n [Connection Aborted Error] Try restarting the game...")
    GAMEON = False
except ConnectionRefusedError:
    print("\n [Connection Refused Error] Try restarting the game...")
    print(" If this continues to occur, restart the Battleship server")
    GAMEON = False    
except KeyboardInterrupt:
    print("\n [Keyboard Interrupt] Restart the game...")
    GAMEON = False
    
### BOARD SETUP ###
p = GameBoard()



while GAMEON:
    wipe = os.system(clearscreen)
    print("\n", p)
    print(" How would you like to setup your ships (M=Manual, A=Auto)? ", end="")
    choice = input()
    if (choice.upper() == "A"):
        success = False
        while not success:
            p.reset()
            autoSet(p)
            wipe = os.system(clearscreen)
            print("\n", p)
            print(" Do you like this placement? Y or N: ", end="")
            final = input()
            if (final.lower() == "y"):
                success = True
            if (final.lower() == "n"):
                success = False
        break
    elif (choice.upper() == "M"):
        for i in range(1,6):
            success = False
            while not success:
                temp = p.copy()
                wipe = os.system(clearscreen)
                print("\n", temp)
                ship = Ship(i)
                while (True):
                    print(" Enter position for your "+ str(ship) +" ("+ str(ship.getSize()) +"): ", end="")
                    entry = input()
                    try:
                        row = entry[0]
                        col = int(entry[1])
                        DIR = entry[2]
                        ship.setDirection(DIR)
                        success = temp.setShip(row, col, ship)
                        break
                    except:
                        pass
                    print(" *** ENTRY ERROR - Format: Row + Column + Angle H/V, (ex: A0H) ***")
                if success:
                    wipe = os.system(clearscreen)
                    print("\n", temp)
                    print(" Do you like this placement? Y or N: ", end="")
                    final = input()
                    if (final.lower() == "y"):
                        success = p.setShip(row, col, ship)
                    if (final.lower() == "n"):
                        success = False
        wipe = os.system(clearscreen)
        print("\n", p)
        print()
        print(" Congrats! Hit ENTER to continue...")
        input()
        break
    else:
        print(" *** Answer must be M or A *** Press ENTER to continue")
        input()

### GAME PLAY ###
last = ""
hit = False
while GAMEON:
    if START:
        error = ""
        wipe = os.system(clearscreen)
        print("\n"*10 + str(PrintText(" "*23+ "YOUR TURN")))
        #print('\a')
        winsound.Beep(frequency, duration)
        winsound.Beep(frequency, duration)
        #winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)
        input()
        while (True):
            wipe = os.system(clearscreen)
            print("\n", p)
            print(last)
            print(error)
            print(" YOUR TURN - Enter launch coordinates: ", end="")
            shot = input()
            ### CHEAT CODE ACCESS ###
            if (shot == ccode_view_all or shot == ccode_nuke_all or shot == ccode_next_hit):
                # allow pass
                break
            try:
                if isCorrect(shot):
                    shot = shot[0].upper()+shot[1]
                    break
            except:
                error = " *** ENTRY ERROR: Must be 2 characters, Row & Column (ex: A0) ***"
        # send shot
        enemy.send(shot.encode('ascii'))
        ### CHEAT CODE ACCESS ###
        # VIEW ALL CHEAT #
        if (shot == ccode_view_all):
            # Receive enemy board
            board = enemy.recv(1024).decode('ascii')
            if not board:
                # Server lost...
                print("SORRY! Server connection lost...")
                break
            # falsify shot
            shot = p.findEnemyMiss()
            hit = False
            # Load enemy board
            p.receiveBoard(board)
        # FIND NEXT HIT CHEAT #
        elif (shot == ccode_next_hit):
            # Receive shot info
            shot = enemy.recv(1024).decode('ascii')
            if not shot:
                # Server lost...
                print("SORRY! Server connection lost...")
                break
            hit = True
        # NUKE ALL CHEAT #
        elif (shot == ccode_nuke_all):
            # Receive enemy board
            board = enemy.recv(1024).decode('ascii')
            if not board:
                # Server lost...
                print("SORRY! Server connection lost...")
                break
            # Load enemy board
            p.receiveBoard(board)
            # falsify shot
            shot = p.findEnemyHit()
            hit = True
        else:
            # wait for response
            hit = enemy.recv(1024).decode('ascii')
            if not hit:
                # Server lost...
                print("SORRY! Server connection lost...")
                break
            hit = makeBool(hit)

        # log results           
        p.logShot(shot[0],int(shot[1]), hit)
        if hit:
            if animate:
                afreq = 3000  # Set Frequency To 2500 Hertz
                adur = 100  # Set Duration To 1000 ms == 1 second
                for i in range(3):
                    winsound.Beep(afreq, adur)
                    afreq -=500
                explosion()
            wipe = os.system(clearscreen)
            print("\n", p)
            print(" *** You got a HIT at", shot, "***")
            # check for win
            win = p.isWin()
            if win:
                # WINNER
                board = enemy.recv(1024).decode('ascii')
                if not board:
                    # Server lost...
                    print("SORRY! Server connection lost...")
                    break
                p.receiveBoard(board)
                enemy.send(p.sendBoard().encode('ascii'))
                wipe = os.system(clearscreen)
                print("\n", p)
                print("   *****************************************")
                print("   ** !!! YOU HAVE DEFEATED THE ENEMY !!! **")
                print("   *****************************************")
                print()
                break
        else:
            wipe = os.system(clearscreen)
            print("\n", p)
            print(" *** You MISSED at", shot, "***")


    # wait for return volley
    if not START:
        wipe = os.system(clearscreen)
        print("\n", p)
        START = True
    print("\n Waiting for enemy shot... ", end="")
    shot = enemy.recv(1024).decode('ascii')
    
    if not shot:
        # Server lost...
        print("SORRY! Server connection lost...")
        break
        
    ### CHEAT CODE ACCESS ###
    # VIEW ALL CHEAT #
    if (shot == ccode_view_all):
        # falsify shot
        shot = p.findMiss()
        row = shot[0].upper()
        col = int(shot[1])
        hit = p.receiveShot(row, col)
        # Send board
        enemy.send(p.sendBoard().encode('ascii'))
    # FIND NEXT HIT CHEAT #
    elif (shot == ccode_next_hit):
        # get a new hit
        shot = p.findHit()
        row = shot[0].upper()
        col = int(shot[1])
        hit = p.receiveShot(row, col)
        # Send board
        enemy.send(shot.encode('ascii'))
    # NUKE ALL SHIPS CHEAT #
    elif (shot == ccode_nuke_all):
        # falsify shot
        row = "A"
        col = 1
        hit = p.nuke()
        # Send board
        enemy.send(p.sendBoard().encode('ascii'))
    ### NOT A CHEAT ###
    else:
        row = shot[0].upper()
        col = int(shot[1])
        # enter shot
        hit = p.receiveShot(row, col)
        enemy.send(str(hit).encode('ascii'))
    if hit:
        explosion()
        last = " Your enemy scored a HIT at "+ row + str(col)
        lost = p.hasLost()
        if lost:
            # send over your board
            enemy.send(p.sendBoard().encode('ascii'))
            board = enemy.recv(1024).decode('ascii')
            if not board:
                # Server lost...
                print("SORRY! Server connection lost...")
                break
            p.receiveBoard(board)
            wipe = os.system(clearscreen)
            print("\n", p)
            print("   *****************************************")
            print("   ******** YOU HAVE BEEN DEFEATED! ********")
            print("   *****************************************")
            print()
            break
    else:
        last = "Your enemy MISSED at "+ row + str(col)


### CLEAN-UP ###
s.close()
print(" GAME OVER")
input()
