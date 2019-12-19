import pygame
import sys
import random
from GameBoard import GameBoard
from Ship import Ship

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
P_BOARD_POSY = 75
O_BOARD_POSX = SCREEN_WIDTH // 2 + BOARD_MARGIN
O_BOARD_POSY = P_BOARD_POSY

# COLOR SETTINGS #
BACKGROUND = (0,40,80)
BOARD_FG = (0,153,255)
BOARD_BG = (255,255,255)
SHIP_LIGHT = (128,128,128)
SHIP_DARK = (92,92,92)
MISS_COLOR = (255,255,255)
HIT_COLOR = (255,0,0)
FLASH_COLOR = (0,150,255)
TEXT_COLOR = (255,255,255)

# PYGAME INITIALIZATION #
pygame.init()
clock = pygame.time.Clock()

# FONT SETTINGS #
TITLE_FONT = pygame.font.SysFont(None,200)
GAME_FONT = pygame.font.SysFont(None,40)
TEXT_FONT = pygame.font.SysFont(None,24)

""" TEMP BOARD DATA FOR TESTING """
board1 = [[0 for x in range(NUM_CELLS)] for x in range(NUM_CELLS)]
board2 = [[0 for x in range(NUM_CELLS)] for x in range(NUM_CELLS)]
p = GameBoard()

HIT_ASCII2 = """
XX      XX
  XX  XX
    XX
  XX  XX
XX      XX
"""

HIT_ASCII = """
X  X  X
 X X X
  XXX
XXXXXXX
  XXX
 X X X
X  X  X
"""

def makeHitSurf():
    surf = pygame.Surface([CELL_WIDTH, CELL_WIDTH])
    surf.fill((255,255,255))
    surf.set_colorkey((255,255,255))
    pygame.draw.line(surf, HIT_COLOR, (CELL_WIDTH, CELL_WIDTH), (0,0), 10)
    pygame.draw.line(surf, HIT_COLOR, (-3, CELL_WIDTH), (CELL_WIDTH,0), 10)
    return surf

def makeSurfFromASCII(text, fg=(0,0,0), bg=(255,255,255)):
    text = text.split('\n')[1:-1]
    width = max([len(x) for x in text])
    height = len(text)
    surf = pygame.Surface((width, height))
    surf.fill(bg)

    pArr = pygame.PixelArray(surf)
    for i in range(height):
        for j in range(len(text[i])):
            if text[i][j] == 'X':
                pArr[j][i] = fg

    surf.set_colorkey(bg)
    return surf

def makeButton(text, fg, bg, width):
    button = pygame.Surface([width, 40])
    button.fill(bg)
    drawText(text,
         button, GAME_FONT,
         width//2, 8,
         fg, bg, 'center')
    return button

#HIT_SURF = pygame.transform.scale(makeSurfFromASCII(HIT_ASCII, HIT_COLOR), (CELL_WIDTH, CELL_WIDTH))

# HELPER FUNCTIONS #
def boardClicked(boardRect, pos):
    if pos[0] > boardRect.x + CELL_BORDER and pos[0] < boardRect.x + BOARD_WIDTH \
    and pos[1] > boardRect.y + CELL_BORDER and pos[1] < boardRect.y + BOARD_HEIGHT:
        col = (pos[0] - boardRect.x - CELL_BORDER) // (CELL_WIDTH + CELL_MARGIN)
        row = (pos[1] - boardRect.y - CELL_BORDER) // (CELL_WIDTH + CELL_MARGIN)
        return min(row,9), min(col,9)
    else:
        return False

def boardXY(boardRect, pos):
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

def drawBoard(screen, board, xy):
    image = pygame.Surface([BOARD_WIDTH, BOARD_HEIGHT])
    boardrect = pygame.draw.rect(image, BOARD_BG, [0, 0, BOARD_WIDTH, BOARD_HEIGHT])
    boardrect.x = xy[0]
    boardrect.y = xy[1]

    for row in range(NUM_CELLS):
        for col in range(NUM_CELLS):
            # CODE FOR SHIP/SHOT DATA HERE
            if (board[row][col] >= 1 and board[row][col] <= 5):
                color = SHIP_DARK
            elif (board[row][col] == 7):
                color = HIT_COLOR
            elif (board[row][col] == 6):
                color = BACKGROUND
            else:
                color = BOARD_FG
            x = (CELL_WIDTH + CELL_MARGIN) * col + CELL_BORDER
            y = (CELL_WIDTH + CELL_MARGIN) * row + CELL_BORDER
            pygame.draw.rect(image, color, [x, y, CELL_WIDTH, CELL_WIDTH])

    screen.blit(image, xy)
    return boardrect

# SCENE FUNCTIONS #
def startScreen(surf):

    surf.fill(BACKGROUND)
        
    ready = False
    connected = False
    while not ready:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                ########### SHUTDOWN EVERYTHING ###########
                pygame.quit()
                sys.exit()

            if connected == True and \
            (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or \
            event.type == pygame.MOUSEBUTTONDOWN:
                ready = True

        if not connected:
            delay = 200
        else:
            delay = 0

        drawText("BATTLESHIP",
                 surf, TITLE_FONT,
                 SCREEN_WIDTH//2, SCREEN_HEIGHT//4,
                 TEXT_COLOR, BACKGROUND, 'center')
        temp = drawText("Connecting to the battleship server...",
                 surf, TEXT_FONT,
                 SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                 TEXT_COLOR, BACKGROUND, 'center')
        pygame.display.update()
        pygame.time.delay(delay)
        temp = drawText("Connected!",
                 surf, TEXT_FONT,
                 SCREEN_WIDTH//2, temp.y+temp.height+5,
                 TEXT_COLOR, BACKGROUND, 'center')
        pygame.display.update()
        pygame.time.delay(delay)
        temp = drawText("Waiting for the other player to join...",
                 surf, TEXT_FONT,
                 SCREEN_WIDTH//2, temp.y+temp.height+5,
                 TEXT_COLOR, BACKGROUND, 'center')
        pygame.display.update()
        pygame.time.delay(delay)
        temp = drawText("All players have joined...",
                 surf, TEXT_FONT,
                 SCREEN_WIDTH//2, temp.y+temp.height+5,
                 TEXT_COLOR, BACKGROUND, 'center')
        pygame.display.update()
        pygame.time.delay(delay)
        temp = drawText("You are PLAYER 1: Press ENTER to continue...",
                 surf, TEXT_FONT,
                 SCREEN_WIDTH//2, temp.y+temp.height+5,
                 TEXT_COLOR, BACKGROUND, 'center')
        connected = True
        
        pygame.display.update()
        
    return

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
                 P_BOARD_POSX+(BOARD_WIDTH//2),
                 P_BOARD_POSY-30,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')
        player_board = drawBoard(surf, p.getPBoard(), (P_BOARD_POSX, P_BOARD_POSY))

        pygame.display.update()
    return

class makeShip(pygame.sprite.Sprite):
    def __init__(self, stype, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.ship = Ship(stype)
        self.image = pygame.Surface([self.ship.getSize()*(CELL_MARGIN+CELL_WIDTH), CELL_WIDTH])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def rotate(self):
        x = self.rect.x
        y = self.rect.y
        self.ship.rotate()
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def placeShipsScreen(surf):

    ships = pygame.sprite.RenderPlain(())
    for i in range(1,6):
        ship = makeShip(i, SHIP_LIGHT, 40*3+3*2, 40)
        ship.rect.x = 700
        ship.rect.y = 100+i*50
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
                            dragging = s
                            mouse_x, mouse_y = event.pos
                            offset_x = s.rect.x - mouse_x
                            offset_y = s.rect.y - mouse_y
                if event.button == 3:
                    for s in ships.sprites():
                        if s.rect.collidepoint(event.pos):
                            s.rotate()
                            # rotate s                    

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    dragging.rect.x = mouse_x + offset_x
                    dragging.rect.y = mouse_y + offset_y

        surf.fill(BACKGROUND)
        
        # PLAYER BOARD #
        drawText("PLACE YOUR SHIPS",
                 surf,
                 GAME_FONT,
                 P_BOARD_POSX+(BOARD_WIDTH//2),
                 P_BOARD_POSY-30,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')
        
        player_board = drawBoard(surf, p.getPBoard(), (P_BOARD_POSX, P_BOARD_POSY))
        
        ships.draw(surf)

        # INTERACTIVE PLACEMENT #
        p.reset()
        for s in ships.sprites():
            if boardClicked(player_board, (s.rect.x+20,s.rect.y+20)):
                x, y = boardClicked(player_board, (s.rect.x+20,s.rect.y+20))
                if p.setShip(x, y, s.ship):
                    if not dragging:
                        s.image.set_alpha(0)
                        s.rect.x, s.rect.y = boardXY(player_board,(x,y))
                    else:
                        dragging.image.set_alpha(255)
                else:
                    s.image.set_alpha(255)

        if p.isSet():
            surf.blit(s_button, (bRect.x, bRect.y))               
            
        pygame.display.update()                

    return

def main():
    mainSurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    flashSurface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    flashSurface.fill(FLASH_COLOR)

    pygame.display.set_caption('BATTLESHIP')

    startScreen(mainSurface)
    setupScreen(mainSurface)

    yourTurn = True
    done = False
    alpha = 0
    direction = 1
    while not done:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if boardClicked(player_board, pos):
                    row, col = boardClicked(player_board, pos)
                    p.receiveShot(row, col)
                    yourTurn = True

                if yourTurn and boardClicked(opponent_board, pos):
                    row, col = boardClicked(opponent_board, pos)
                    hit = random.randrange(0,2)
                    p.logShot(row, col, hit)
                    yourTurn = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    yourTurn = True

        # If a hit was registered #
            #hitAnimation(mainSurface)

        # IF game is over
            #finalScreen(mainSurface)
            #QUIT

        # If it is players turn #
        if yourTurn:
            alpha += direction
            if alpha % 100 == 0: direction *= -1
        else:
            alpha = 0
            direction = 1
            

        mainSurface.fill(BACKGROUND)
        
        flashSurface.set_alpha(alpha)
        mainSurface.blit(flashSurface, (0,0))

        # PLAYER BOARD #
        drawText("YOU",
                 mainSurface,
                 GAME_FONT,
                 P_BOARD_POSX+(BOARD_WIDTH//2),
                 P_BOARD_POSY-30,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')
        player_board = drawBoard(mainSurface, p.getPBoard(), (P_BOARD_POSX, P_BOARD_POSY))

        # OPPONENT BOARD #
        drawText("ENEMY",
                 mainSurface,
                 GAME_FONT,
                 O_BOARD_POSX+(BOARD_WIDTH//2),
                 O_BOARD_POSY-30,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')
        opponent_board = drawBoard(mainSurface, p.getOBoard(), (O_BOARD_POSX, O_BOARD_POSY))

        pygame.display.update()

    pygame.quit()
    sys.exit()        

if __name__ == '__main__':
    main()
