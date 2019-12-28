import socket
from tkinter import Tk, messagebox
import pygame
from pygame.compat import geterror
import math
import sys
import os
import random
from GameBoard import GameBoard
from Ship import Ship
import threading

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

# DISPLAY SETTINGS #
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 760
FRAMERATE = 60

# GAME BOARD SETTINGS #
CELL_WIDTH = 40
CELL_BORDER = 4
CELL_MARGIN = 2
NUM_CELLS = 10

BOARD_WIDTH = CELL_BORDER + (CELL_WIDTH + CELL_MARGIN) * NUM_CELLS + CELL_BORDER - CELL_MARGIN
BOARD_HEIGHT = BOARD_WIDTH

BOARD_MARGIN = 50
P_BOARD_POSX = SCREEN_WIDTH // 2 - BOARD_WIDTH - BOARD_MARGIN
P_BOARD_POSY = 110
O_BOARD_POSX = SCREEN_WIDTH // 2 + BOARD_MARGIN
O_BOARD_POSY = P_BOARD_POSY

# COLOR SETTINGS #
BACKGROUND = (0, 40, 80)
BOARD_FG = (0, 153, 255)
BOARD_BG = (255, 255, 255)
SHIP_LIGHT = (128, 128, 128)
SHIP_DARK = (92, 92, 92)
MISS_COLOR = BACKGROUND
HIT_COLOR = (200, 0, 0)
MISSILE_COLOR = (255, 255, 255)
FLASH_COLOR = (0, 150, 255)
TEXT_COLOR = (255, 255, 255)

# PYGAME INITIALIZATION #
pygame.init()
clock = pygame.time.Clock()
error_flag = False
player_turn = False
player_queue = list()
enemy_queue = list()
cheat_queue = list()

# FONT SETTINGS #
TITLE_FONT = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 160)
BANNER_FONT = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 52)
GAME_FONT = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 30)
TEXT_FONT = pygame.font.Font(os.path.join(data_dir, "freesansbold.ttf"), 18)

# NETWORKING SETUP #
if len(sys.argv) > 1:
    SERVER_IP = sys.argv[1]
else:
    SERVER_IP = "192.168.86.38"
    # SERVER_IP = "SAL-1908-KJ"
PORT = 9999
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
EVENT_CLOSE_SOCKET = pygame.USEREVENT + 0
EVENT_RECEIVE = pygame.USEREVENT + 1
EVENT_SERVER_ERROR = pygame.USEREVENT + 2


def server_thread():
    global player_turn
    global error_flag
    gameon = False

    try:
        print(" Connecting to the Battleship server... ")
        SERVER.connect((SERVER_IP, PORT))
        greeting = SERVER.recv(1024).decode('ascii')
        enemy_queue.insert(0, "CONNECTED")
        print(" " + greeting)

        print(" " + "Waiting for the other player to join...")
        greeting = SERVER.recv(1024).decode('ascii')

        print(" All players have joined...")
        if greeting.find("PLAYER 1") != -1:
            print(" PLAYER 1 assignment")
            enemy_queue.insert(0, "PLAYER 1")
            player_turn = True
        else:
            print(" PLAYER 2 assignment ")
            player_turn = False
            enemy_queue.insert(0, "PLAYER 2")

        gameon = True

    except OSError:
        info = "OSError: [WinError 10038] Try restarting the game..."
        print(info)
        error_flag = True
    except ConnectionResetError:
        info = "[Connection Reset Error] Try restarting the game..."
        print(info)
        error_flag = True
    except ConnectionAbortedError:
        info = "[Connection Aborted Error] Try restarting the game..."
        print(info)
        error_flag = True
    except ConnectionRefusedError:
        info = "[Connection Refused Error] Try restarting the game..."
        print(info)
        print(" If this continues to occur, restart the Battleship server")
        error_flag = True
    except KeyboardInterrupt:
        info = "[Keyboard Interrupt] Restart the game..."
        print(info)
        error_flag = True

    print("Starting the game...")
    while gameon:

        try:
            comm = SERVER.recv(1024).decode('ascii')
        except OSError:
            break
        if not comm:
            info = "SORRY! Server connection lost..."
            print(info)
            error_flag = True
            break
        print("Received:", comm)
        if comm.find("CHEAT,") != -1:
            cheat = comm.replace("CHEAT,", "")
            cheat_queue.insert(0, cheat)
        elif comm.find("MOVE,") != -1:
            move = comm.replace("MOVE,", "")
            enemy_queue.insert(0, move)

        for event in pygame.event.get(EVENT_CLOSE_SOCKET):
            if event.type == EVENT_CLOSE_SOCKET:
                print("THREAD: EVENT CLOSE DETECTED")
                gameon = False
                break

    SERVER.close()
    print("Thread FINISHED")
    return


class PyGameBoard(GameBoard):

    def __init__(self, blank):
        GameBoard.__init__(self)
        self.blank = blank
        self.pyBoard = [[self.blank for x in range(10)] for x in range(10)]

    def reset(self):
        GameBoard.reset(self)
        for i in range(100):
            self.pyBoard[i // 10][i % 10] = self.blank

    def autoSet(self):
        # Board must be empty #
        for i in range(100):
            if self.p_board[i // 10][i % 10] != 0:
                return False
        for i in range(1, 6):
            s = makeShip(i)
            vert = random.randrange(2)
            if vert == 1:
                s.rotate()
            success = False
            while not success:
                row = random.randrange(10)
                col = random.randrange(10)
                success = self.setShip(row, col, s.ship)
                if success:
                    for x in range(s.ship.getSize()):
                        temp = s.image.subsurface((s.ship.dir[s.ship.DIR][1] * x * CELL_WIDTH,
                                                   s.ship.dir[s.ship.DIR][0] * x * CELL_WIDTH,
                                                   CELL_WIDTH, CELL_WIDTH)).copy()
                        temp.set_alpha(255)
                        self.pyBoard[row][col] = temp
                        row += s.ship.dir[s.ship.DIR][0]
                        col += s.ship.dir[s.ship.DIR][1]
        return True


SHIP_BACK = """
....XXXXXX
.XXXXXXXXX
.XXX------
XX-----XXX
XX-----X--
XX-----X--
XX-----XXX
.XXX------
.XXXXXXXXX
....XXXXXX
"""

SHIP_FRONT = """
XXX.......
XXXXX.....
----XXX...
X------XX.
X-------XX
X-------XX
X------XX.
----XXX...
XXXXX.....
XXX.......
"""

SHIP_MID = """
XXXXXXXXXX
XXXXXXXXXX
----------
XXXXXXXXXX
----------
----------
XXXXXXXXXX
----------
XXXXXXXXXX
XXXXXXXXXX
"""


def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print("Cannot load sound: %s" % fullname)
        raise SystemExit(str(geterror()))
    return sound


fire_sound = load_sound("fire.wav")
boom_sound = load_sound("boom.wav")
splash_sound = load_sound("splash.wav")
start_music = load_sound("start.wav")
lose_sound = load_sound("lose.wav")
win_sound = load_sound("win.wav")
warning_sound = load_sound("warning.wav")
fart_sound = load_sound("fart.wav")


def makeHitSurf():
    surf = pygame.Surface([CELL_WIDTH, CELL_WIDTH])
    surf.fill((255, 255, 255))
    surf.set_colorkey((255, 255, 255))
    pygame.draw.line(surf, HIT_COLOR, (CELL_WIDTH, CELL_WIDTH), (0, 0), 10)
    pygame.draw.line(surf, HIT_COLOR, (-3, CELL_WIDTH), (CELL_WIDTH, 0), 10)
    return surf


def makeSurfFromASCII(text, fg1=(0, 0, 0), bg=(255, 255, 255), fg2=(0, 0, 0)):
    text = text.split('\n')[1:-1]
    width = max([len(x) for x in text])
    height = len(text)
    surf = pygame.Surface((width, height))
    surf.fill(bg)

    pArr = pygame.PixelArray(surf)
    for i in range(height):
        for j in range(len(text[i])):
            if text[i][j] == 'X':
                pArr[j][i] = fg1
            elif text[i][j] == '-':
                pArr[j][i] = fg2

    surf.set_colorkey(bg)
    return surf


SHIP_BACK_SURF = makeSurfFromASCII(SHIP_BACK, SHIP_DARK, BACKGROUND, SHIP_LIGHT)
SHIP_BACK_SURF = pygame.transform.scale(SHIP_BACK_SURF, (CELL_WIDTH, CELL_WIDTH))

SHIP_FRONT_SURF = makeSurfFromASCII(SHIP_FRONT, SHIP_DARK, BACKGROUND, SHIP_LIGHT)
SHIP_FRONT_SURF = pygame.transform.scale(SHIP_FRONT_SURF, (CELL_WIDTH, CELL_WIDTH))

SHIP_MID_SURF = makeSurfFromASCII(SHIP_MID, SHIP_DARK, BACKGROUND, SHIP_LIGHT)
SHIP_MID_SURF = pygame.transform.scale(SHIP_MID_SURF, (CELL_WIDTH, CELL_WIDTH))

BOARD_BLANK_SURF = pygame.Surface((CELL_WIDTH, CELL_WIDTH))
BOARD_BLANK_SURF.fill(BOARD_FG)

BOARD_HIT_SURF = pygame.Surface((CELL_WIDTH, CELL_WIDTH))
BOARD_HIT_SURF.fill(BOARD_BG)
pygame.draw.polygon(BOARD_HIT_SURF, HIT_COLOR, [(5, 20), (20, 35), (35, 20), (20, 5)])
BOARD_HIT_SURF.set_colorkey(BOARD_BG)

BOARD_MISS_SURF = pygame.Surface((CELL_WIDTH, CELL_WIDTH))
BOARD_MISS_SURF.fill(BOARD_BG)
pygame.draw.circle(BOARD_MISS_SURF, MISS_COLOR, (CELL_WIDTH // 2, CELL_WIDTH // 2), CELL_WIDTH // 3)
BOARD_MISS_SURF.set_colorkey(BOARD_BG)

""" TEMP BOARD DATA FOR TESTING """
p = PyGameBoard(BOARD_BLANK_SURF)


def makeButton(text, fg, bg, width):
    button = pygame.Surface([width, 40])
    button.fill(bg)
    drawText(text,
             button, GAME_FONT,
             width // 2, 0,
             fg, bg, 'center')
    return button


# HELPER FUNCTIONS #
def getBoardRC(boardRect, pos):
    if boardRect.x + CELL_BORDER < pos[0] < boardRect.x + BOARD_WIDTH \
            and boardRect.y + CELL_BORDER < pos[1] < boardRect.y + BOARD_HEIGHT:
        col = (pos[0] - boardRect.x - CELL_BORDER) // (CELL_WIDTH + CELL_MARGIN)
        row = (pos[1] - boardRect.y - CELL_BORDER) // (CELL_WIDTH + CELL_MARGIN)
        return min(row, 9), min(col, 9)
    else:
        return False


def getBoardXY(boardRect, pos):
    x = (boardRect.x + CELL_BORDER) + (CELL_WIDTH + CELL_MARGIN) * pos[1]
    y = (boardRect.y + CELL_BORDER) + (CELL_WIDTH + CELL_MARGIN) * pos[0]
    return x, y


# DRAW FUNCTIONS #
def drawText(text, surf, font, x, y, fgcol, bgcol, pos='left'):
    # creates the text in memory (it's not on a surface yet).
    textobj = font.render(text, 1, fgcol, bgcol)
    textobj.set_colorkey(bgcol)
    textrect = textobj.get_rect()

    if pos == 'left':
        textrect.topleft = (int(x), int(y))
    elif pos == 'center':
        textrect.midtop = (int(x), int(y))

    # draws the text onto the surface
    surf.blit(textobj, textrect)
    return textrect


def drawBoard(screen, board, xy, opponent=False):
    image = pygame.Surface([BOARD_WIDTH, BOARD_HEIGHT])
    boardrect = pygame.draw.rect(image, BOARD_BG, [0, 0, BOARD_WIDTH, BOARD_HEIGHT])
    boardrect.x = xy[0]
    boardrect.y = xy[1]

    for row in range(NUM_CELLS):
        for col in range(NUM_CELLS):
            # CODE FOR SHIP/SHOT DATA HERE
            x = (CELL_WIDTH + CELL_MARGIN) * col + CELL_BORDER
            y = (CELL_WIDTH + CELL_MARGIN) * row + CELL_BORDER
            image.blit(BOARD_BLANK_SURF, (x, y))
            if not opponent:
                image.blit(p.pyBoard[row][col], (x, y))

            if 1 <= board[row][col] <= 5:
                if opponent:
                    pygame.draw.rect(image, SHIP_LIGHT, [x, y, CELL_WIDTH, CELL_WIDTH])

            if board[row][col] == 7:
                if opponent:
                    pygame.draw.rect(image, SHIP_LIGHT, [x, y, CELL_WIDTH, CELL_WIDTH])
                image.blit(BOARD_HIT_SURF, (x, y))

            elif board[row][col] == 6:
                image.blit(BOARD_MISS_SURF, (x, y))

    screen.blit(image, xy)
    return boardrect


# SCENE FUNCTIONS #
def startScreen(surf):
    global enemy_queue, player_turn
    surf.fill(BACKGROUND)

    ready = False
    connected = False
    alljoined = False
    while not ready:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ########### SHUTDOWN EVERYTHING ###########
                pygame.quit()
                sys.exit()

            if not error_flag and alljoined and \
                    ((event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or \
                     event.type == pygame.MOUSEBUTTONDOWN):
                return True

        # process enemy queue for connection status
        if not ready and len(enemy_queue) != 0:
            if enemy_queue[-1] == "CONNECTED":
                connected = True
                enemy_queue.pop(-1)
            elif enemy_queue[-1].find("PLAYER") != -1:
                enemy_queue.pop(-1)
                alljoined = True

        drawText("BATTLESHIP",
                 surf, TITLE_FONT,
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4,
                 TEXT_COLOR, BACKGROUND, 'center')

        temp = drawText("Connecting to the battleship server...",
                        surf, TEXT_FONT,
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                        TEXT_COLOR, BACKGROUND, 'center')

        if connected:
            temp = drawText("Connected!",
                            surf, TEXT_FONT,
                            SCREEN_WIDTH // 2, temp.y + temp.height + 5,
                            TEXT_COLOR, BACKGROUND, 'center')

            temp = drawText("Waiting for the other player to join...",
                            surf, TEXT_FONT,
                            SCREEN_WIDTH // 2, temp.y + temp.height + 5,
                            TEXT_COLOR, BACKGROUND, 'center')

        if alljoined:
            temp = drawText("All players have joined",
                            surf, TEXT_FONT,
                            SCREEN_WIDTH // 2, temp.y + temp.height + 5,
                            TEXT_COLOR, BACKGROUND, 'center')

            temp = drawText("Press ENTER to continue",
                            surf, TEXT_FONT,
                            SCREEN_WIDTH // 2, temp.y + temp.height + 5,
                            TEXT_COLOR, BACKGROUND, 'center')
        if error_flag:
            temp = drawText("[SERVER ERROR]: Please close window and restart the game",
                            surf, TEXT_FONT,
                            SCREEN_WIDTH // 2, temp.y + temp.height + 5,
                            TEXT_COLOR, BACKGROUND, 'center')

        pygame.display.update()

    return True


def setupScreen(surf):
    manual = False
    auto = False

    # Setup buttons #
    b_width = 120
    b_height = 40
    b_margin = 50

    m_button = makeButton("Manual", TEXT_COLOR, SHIP_DARK, b_width)
    a_button = makeButton("Auto", TEXT_COLOR, SHIP_DARK, b_width)
    s_button = makeButton("Save", TEXT_COLOR, SHIP_DARK, b_width)
    r_button = makeButton("Redo", TEXT_COLOR, SHIP_DARK, b_width)

    bposx = P_BOARD_POSX + BOARD_WIDTH // 2
    bposy = P_BOARD_POSY + BOARD_HEIGHT + b_height

    x = bposx - b_width - b_margin // 2
    y = bposy
    leftRect = pygame.Rect(x, y, b_width, b_height)

    x = bposx + b_margin // 2
    y = bposy
    rightRect = pygame.Rect(x, y, b_width, b_height)

    done = False
    while not done:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ########### SHUTDOWN EVERYTHING ###########
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                x, y = pos[0], pos[1]

                if not manual and not auto:
                    if leftRect.collidepoint(x, y):
                        manual = True
                        done = True
                    if rightRect.collidepoint(x, y):
                        p.reset()
                        p.autoSet()
                        auto = True
                if auto:
                    if leftRect.collidepoint(x, y):
                        done = True
                        return
                    if rightRect.collidepoint(x, y):
                        p.reset()
                        p.autoSet()

        surf.fill(BACKGROUND)

        # CHOOSE AUTO or MANUAL #
        if not manual and not auto:
            surf.blit(m_button, (leftRect.x, leftRect.y))
            surf.blit(a_button, (rightRect.x, rightRect.y))

        # AUTO #
        if auto:
            surf.blit(s_button, (leftRect.x, leftRect.y))
            surf.blit(r_button, (rightRect.x, rightRect.y))

        # MANUAL #
        if manual:
            placeShipsScreen(surf)
            return

        # PLAYER BOARD #
        drawText("PLACE YOUR SHIPS",
                 surf,
                 GAME_FONT,
                 P_BOARD_POSX + (BOARD_WIDTH // 2),
                 P_BOARD_POSY - 35,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')
        player_board = drawBoard(surf, p.getPBoard(), (P_BOARD_POSX, P_BOARD_POSY))

        pygame.display.update()

    return


class makeShip(pygame.sprite.Sprite):
    def __init__(self, stype):
        pygame.sprite.Sprite.__init__(self)
        self.ship = Ship(stype)
        self.image = pygame.Surface([CELL_WIDTH * self.ship.getSize(), CELL_WIDTH])
        self.image.fill(BACKGROUND)
        self.image.set_colorkey(BACKGROUND)
        for i in range(self.ship.getSize()):
            if i == 0:
                self.image.blit(SHIP_BACK_SURF, (0, 0))
            elif i == self.ship.getSize() - 1:
                self.image.blit(SHIP_FRONT_SURF, (i * CELL_WIDTH, 0))
            else:
                self.image.blit(SHIP_MID_SURF, (i * CELL_WIDTH, 0))
        self.rect = self.image.get_rect()

    def rotate(self):
        x = self.rect.x
        y = self.rect.y
        self.ship.rotate()
        self.image = pygame.transform.rotate(self.image, -90)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def placeShipsScreen(surf):
    ships = pygame.sprite.RenderPlain(())
    for i in range(1, 6):
        ship = makeShip(i)
        ship.rect.x = 700
        ship.rect.y = 100 + i * 50
        ships.add(ship)

    # Setup buttons #
    b_width = 120
    b_height = 40

    s_button = makeButton("Save", TEXT_COLOR, SHIP_DARK, b_width)

    bposx = P_BOARD_POSX + BOARD_WIDTH // 2
    bposy = P_BOARD_POSY + BOARD_HEIGHT + b_height

    x = bposx - b_width // 2
    y = bposy
    bRect = pygame.Rect(x, y, b_width, b_height)

    dragging = False
    done = False
    while not done:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ########### SHUTDOWN EVERYTHING ###########
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    x, y = pos[0], pos[1]
                    if bRect.collidepoint(x, y):
                        done = True
                        return

                    for s in ships.sprites():
                        if s.rect.collidepoint(event.pos):
                            ships.remove(s)
                            ships.add(s)
                            dragging = s
                            mouse_x, mouse_y = event.pos
                            offset_x = s.rect.x - mouse_x
                            offset_y = s.rect.y - mouse_y

                if event.button == 3:
                    for s in ships.sprites():
                        if s.rect.collidepoint(event.pos):
                            s.rotate()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    dragging.rect.x = max(0, mouse_x + offset_x)
                    dragging.rect.x = min(SCREEN_WIDTH - dragging.ship.getSize() * CELL_WIDTH, dragging.rect.x)
                    dragging.rect.y = max(0, mouse_y + offset_y)
                    dragging.rect.y = min(SCREEN_HEIGHT - CELL_WIDTH, dragging.rect.y)

        surf.fill(BACKGROUND)

        # PLAYER BOARD #
        drawText("PLACE YOUR SHIPS",
                 surf,
                 GAME_FONT,
                 P_BOARD_POSX + (BOARD_WIDTH // 2),
                 P_BOARD_POSY - 35,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')

        player_board = drawBoard(surf, p.getPBoard(), (P_BOARD_POSX, P_BOARD_POSY))

        ships.draw(surf)

        drawText("Drag your ships onto the grid",
                 surf,
                 TEXT_FONT,
                 800,
                 player_board.bottom - 60,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')

        drawText("Right-click to rotate",
                 surf,
                 TEXT_FONT,
                 800,
                 player_board.bottom - 30,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')

        # INTERACTIVE PLACEMENT #
        p.reset()
        for s in ships.sprites():
            if getBoardRC(player_board, (s.rect.x + 20, s.rect.y + 20)):
                x, y = getBoardRC(player_board, (s.rect.x + 20, s.rect.y + 20))
                if dragging:
                    dragging.image.set_alpha(255)
                if p.setShip(x, y, s.ship):
                    r, c = x, y
                    for i in range(s.ship.getSize()):
                        temp = (s.image.subsurface(s.ship.dir[s.ship.DIR][1] * i * CELL_WIDTH,
                                                   s.ship.dir[s.ship.DIR][0] * i * CELL_WIDTH,
                                                   CELL_WIDTH, CELL_WIDTH)).copy()
                        temp.set_alpha(255)
                        p.pyBoard[r][c] = temp
                        r += s.ship.dir[s.ship.DIR][0]
                        c += s.ship.dir[s.ship.DIR][1]
                    if not dragging:
                        s.image.set_alpha(0)
                        s.rect.x, s.rect.y = getBoardXY(player_board, (x, y))
                    else:
                        dragging.image.set_alpha(0)
                else:
                    s.image.set_alpha(255)
            else:
                s.image.set_alpha(255)

        if p.isSet():
            surf.blit(s_button, (bRect.x, bRect.y))

        pygame.display.update()

    return


def launchScreen(surf, board, xy):
    fire_sound.play()

    if board.x > SCREEN_WIDTH // 2:
        direction = "Left"
    else:
        direction = "Right"

    if direction == "Left":
        mx_start = -40
        bx_start = -200
        aim = 1
    elif direction == "Right":
        mx_start = SCREEN_WIDTH
        bx_start = SCREEN_WIDTH + 200
        aim = -1

    missile = pygame.Surface((CELL_WIDTH // 2, CELL_WIDTH // 2))
    missile.fill(BACKGROUND)
    missile.set_colorkey(BACKGROUND)
    pygame.draw.circle(missile, MISSILE_COLOR, (10, 10), 10)

    ox, oy = getBoardXY(board, xy)
    oy += 10
    mx = mx_start
    ts = pygame.time.get_ticks()
    v = abs(ox - mx_start) * 0.0491
    t = 0
    tn = 0

    done = False
    while not done:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ########### SHUTDOWN EVERYTHING ###########
                pygame.quit()
                sys.exit()

        surf.fill(BACKGROUND)

        if int(10 + tn * 3) < SCREEN_WIDTH * 2:
            pygame.draw.circle(surf, (100, 100, 175), (bx_start, oy), int(20 + tn * 3), 20)

        player_board, opponent_board = drawBoards(surf)

        my = oy + int((-1 * (v * t)) + (0.5 * 9.8 * t ** 2))
        surf.blit(missile, (mx, my))

        pygame.display.update()

        t += .05
        mx += 5 * aim
        tn = (pygame.time.get_ticks() - ts)

        if direction == "Left" and mx > ox:
            done = True
        elif direction == "Right" and ox + 10 > mx:
            done = True

    return


class HitPixel(pygame.sprite.Sprite):

    def __init__(self, x=0, y=0):

        PIXEL_COLORS = [(255, 0, 0), (255, 255, 0), (255, 153, 51), SHIP_DARK, SHIP_LIGHT]

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((random.randrange(5, 10), random.randrange(5, 10)))
        self.image.fill(random.choice(PIXEL_COLORS))
        self.rect = self.image.get_rect()
        self.angle = random.random() * (2 * math.pi)
        self.rect.center = (x, y)
        self.speed = random.random() * 20
        self.image.set_alpha(255)

    def update(self, *args):
        if self.rect.x > SCREEN_WIDTH - self.image.get_width() or self.rect.x < 0:
            self.angle = math.pi - self.angle
        if self.rect.y > SCREEN_HEIGHT - self.image.get_height() or self.rect.y < 0:
            self.angle *= -1
        self.rect.centerx += int(self.speed * math.cos(self.angle))
        self.rect.centery += int(self.speed * math.sin(self.angle))
        self.image.set_alpha(self.image.get_alpha() - 2)
        if self.image.get_alpha() <= 0:
            self.kill()
            del self


def hitAnimation(surf, board, xy):
    boom_sound.play()

    x, y = getBoardXY(board, xy)
    pixels = pygame.sprite.RenderPlain(())
    for i in range(200):
        pixels.add(HitPixel(x + 20, y + 20))

    done = False
    while not done:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ########### SHUTDOWN EVERYTHING ###########
                pygame.quit()
                sys.exit()

        surf.fill(BACKGROUND)

        player_board, opponent_board = drawBoards(surf)

        pixels.update()
        pixels.draw(surf)
        if len(pixels) == 0:
            done = True

        pygame.display.update()

    return


class MissPixel(pygame.sprite.Sprite):

    def __init__(self, x=0, y=0, hit=True):
        PIXEL_COLORS = [(51, 51, 255), (102, 204, 255), (255, 255, 255)]

        pygame.sprite.Sprite.__init__(self)
        self.width = 20
        self.height = 20
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.color = random.choice(PIXEL_COLORS)
        self.speed = random.randrange(1, 8)
        self.alpha = 255

    def update(self, *args):
        self.width += self.speed
        self.height += self.speed
        self.alpha -= 7
        xy = self.rect.center
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.width // 2, self.height // 2), self.height // 2, 1)
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.image.set_alpha(max(0, self.alpha))
        if self.alpha < 0:
            self.kill()
            del self


def missAnimation(surf, board, xy):
    if random.randrange(0, 10) == 0:
        fart_sound.play()
    else:
        splash_sound.play()

    x, y = getBoardXY(board, xy)
    pixels = pygame.sprite.RenderPlain(())
    for i in range(7):
        pixels.add(MissPixel(x + 20, y + 20))

    done = False
    while not done:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ########### SHUTDOWN EVERYTHING ###########
                pygame.quit()
                sys.exit()

        surf.fill(BACKGROUND)

        player_board, opponent_board = drawBoards(surf)

        pixels.update()
        pixels.draw(surf)

        if len(pixels) == 0:
            done = True

        pygame.display.update()

    return


def finalAnimation(surf, board, win=True):
    if win:
        show_board = p.o_board
        banner_color1 = (0, 153, 51)
        banner_color2 = (0, 100, 0)
        text = "YOU ARE VICTORIOUS"
        music = win_sound
    else:
        show_board = p.p_board
        banner_color1 = (204, 51, 0)
        banner_color2 = (153, 0, 0)
        text = "YOU HAVE BEEN DEFEATED"
        music = lose_sound

    banner = pygame.Surface((SCREEN_WIDTH, 100))
    banner.fill(banner_color1)
    image = pygame.draw.rect(banner, banner_color2, (0, 20, SCREEN_WIDTH, 60))
    drawText(text,
             banner,
             BANNER_FONT,
             SCREEN_WIDTH // 2,
             15,
             TEXT_COLOR,
             banner_color2,
             'center')

    ts = pygame.time.get_ticks()
    count = 0

    bombs = list()
    for i in range(100):
        if show_board[i // 10][i % 10] == 7:
            pixels = pygame.sprite.RenderPlain(())
            x, y = getBoardXY(board, (i // 10, i % 10))
            for j in range(100):
                pixels.add(HitPixel(x + 20, y + 20))
            bombs.append(pixels)

    done = False
    complete = False
    while not done:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ########### SHUTDOWN EVERYTHING ###########
                pygame.quit()
                sys.exit()

            if complete and event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                return False

        surf.fill(BACKGROUND)

        player_board, opponent_board = drawBoards(surf)

        if count <= len(bombs) and count < (pygame.time.get_ticks() - ts) // 250:
            count += 1
            fire_sound.play()
            if count == len(bombs):
                boom_sound.play()
                music.play()
                complete = True

        for b in range(min(count, len(bombs))):
            bombs[b].update()
            bombs[b].draw(surf)

        if complete:
            temp = surf.blit(banner, (0, O_BOARD_POSY + BOARD_HEIGHT + 50))
            drawText("Q = QUIT",
                     surf,
                     TEXT_FONT,
                     SCREEN_WIDTH // 2,
                     temp.bottom + 20,
                     TEXT_COLOR,
                     banner_color2,
                     'center')

        pygame.display.update()

    return


def drawBoards(surf, player=None):
    if player is None:
        player = p

    drawText("BATTLESHIP",
             surf,
             BANNER_FONT,
             SCREEN_WIDTH // 2,
             5,
             SHIP_LIGHT,
             BACKGROUND,
             'center')

    # PLAYER BOARD #
    drawText("YOU",
             surf,
             GAME_FONT,
             P_BOARD_POSX + (BOARD_WIDTH // 2),
             P_BOARD_POSY - 35,
             TEXT_COLOR,
             BACKGROUND,
             'center')
    player_board = drawBoard(surf, player.getPBoard(), (P_BOARD_POSX, P_BOARD_POSY))

    # OPPONENT BOARD #
    drawText("ENEMY",
             surf,
             GAME_FONT,
             O_BOARD_POSX + (BOARD_WIDTH // 2),
             O_BOARD_POSY - 35,
             TEXT_COLOR,
             BACKGROUND,
             'center')
    opponent_board = drawBoard(surf, player.getOBoard(), (O_BOARD_POSX, O_BOARD_POSY), True)

    return player_board, opponent_board


def main():
    global player_turn, enemy_queue, player_queue, error_flag
    mainSurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    flashSurface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption('BATTLESHIP')

    restart = True
    while restart:

        # RESET GAME ELEMENTS #
        flashSurface.fill(FLASH_COLOR)
        p.reset()
        enemy_queue.clear()
        player_queue.clear()
        cheat_queue.clear()
        error_flag = False
        player_turn = False
        thread = threading.Thread(target=server_thread, daemon=True)
        thread.start()

        # PLAYER SETUP #
        start_music.stop()
        start_music.play(-1)
        success = startScreen(mainSurface)
        if not success:
            continue
        setupScreen(mainSurface)
        start_music.stop()

        # GAME LOOP SETUP #
        warned = False
        alpha = 0
        direction = 1
        has_lost = False
        has_won = False
        prow = None
        pcol = None
        board_sent = False
        done = False

        while not done:
            clock.tick(FRAMERATE)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    restart = False
                    done = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    if player_turn and getBoardRC(opponent_board, pos):
                        prow, pcol = getBoardRC(opponent_board, pos)
                        ############# SEND LAUNCH TO ENEMY
                        SERVER.send(("MOVE," + str(prow) + str(pcol)).encode('ascii'))
                        # LAUNCH ANIMATION #
                        launchScreen(mainSurface, opponent_board, (prow, pcol))
                        player_turn = False

            # CHEATS #
            keys = pygame.key.get_pressed()
            if player_turn and keys[pygame.K_SPACE] and keys[pygame.K_EQUALS]:
                SERVER.send(("CHEAT," + "NUKE").encode('ascii'))  ###############################
                player_turn = False
            if player_turn and keys[pygame.K_SPACE] and keys[pygame.K_s]:
                SERVER.send(("CHEAT," + "SATELLITE").encode('ascii'))  ###############################
                pygame.time.delay(2000)

            if error_flag:
                Tk().wm_withdraw()  # to hide the main window
                messagebox.showerror('Server Error', 'Sorry! Please restart the game')
                break

            has_lost = p.hasLost()
            if has_lost and not board_sent:
                SERVER.send(("MOVE," + p.sendBoard()).encode('ascii'))  ###############################
                board_sent = True

            has_won = p.isWin()
            if has_won and not board_sent:
                SERVER.send(("MOVE," + p.sendBoard()).encode('ascii'))  ##################################
                board_sent = True

            # alarm on last shot #
            if p.shipsRemaining() == 1 and not warned:
                warned = True
                flashSurface.fill((255, 0, 0))
                warning_sound.play(-1)

            # If it is players turn #
            if player_turn or warned:
                alpha += direction
                if alpha % 100 == 0:
                    direction *= -1
            else:
                alpha = 0
                direction = 1

            mainSurface.fill(BACKGROUND)

            flashSurface.set_alpha(alpha)
            mainSurface.blit(flashSurface, (0, 0))

            player_board, opponent_board = drawBoards(mainSurface)

            drawText("READY TO FIRE",
                     mainSurface, BANNER_FONT,
                     SCREEN_WIDTH // 2, player_board.bottom + 45,
                     BACKGROUND, BACKGROUND, 'center')

            pygame.display.update()

            # process cheat queue
            if len(cheat_queue) != 0:
                cheat = cheat_queue.pop(-1)

                if cheat == "NUKE":
                    p.nuke()

                if cheat == "SATELLITE":
                    SERVER.send(("CHEAT,"+p.sendBoard()).encode('ascii'))

                if len(cheat) == 100:
                    p.receiveBoard(cheat)

            # process enemy queue
            if (not player_turn or has_lost) and len(enemy_queue) != 0:
                data = enemy_queue[-1]

                # IF SHOT
                if len(data) == 2:
                    row = int(data[0])
                    col = int(data[1])
                    hit = p.copy().receiveShot(row, col)
                    ############# SEND HIT TO ENEMY
                    SERVER.send(("MOVE," + str(hit)).encode('ascii'))  ########################################
                    launchScreen(mainSurface, player_board, (row, col))
                    hit = p.receiveShot(row, col)
                    if hit:
                        if p.shipsRemaining() != 0:
                            hitAnimation(mainSurface, player_board, (row, col))
                    else:
                        missAnimation(mainSurface, player_board, (row, col))
                    player_turn = True
                    enemy_queue.pop(-1)

                # IF HIT
                elif data == "True" or data == "False" and (prow is not None and pcol is not None):
                    if data == "True":
                        hit = True
                    else:
                        hit = False
                    p.logShot(prow, pcol, hit)
                    if hit:
                        hitAnimation(mainSurface, opponent_board, (prow, pcol))
                    else:
                        missAnimation(mainSurface, opponent_board, (prow, pcol))
                    enemy_queue.pop(-1)

                # IF RAW BOARD
                # WILL ACCEPT ANY COMMUNICATION, MUST CHECK ALL OTHER COMMS BEFORE
                else:
                    print("BOARD RECEIVED")
                    data = data[:100]
                    p.receiveBoard(data)
                    enemy_queue.pop(-1)
                    continue
            # END PROCESS ENEMY QUEUE

            # Check if game won/lost
            if (has_lost or has_won) and p.oBoardIsKnown():
                warning_sound.stop()
                if has_won:
                    board = opponent_board
                if has_lost:
                    board = player_board
                play_again = finalAnimation(mainSurface, board, has_won)
                done = True
                restart = False

        # Kill the server thread before closing
        print("Posting EVENT_CLOSE_SOCKET event")
        try:
            SERVER.shutdown(socket.SHUT_WR)
            SERVER.close()
        except OSError:
            pass
        pygame.event.post(pygame.event.Event(EVENT_CLOSE_SOCKET))
        thread.join()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
