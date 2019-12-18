import pygame
import sys

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 760
FRAMERATE = 60

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

BACKGROUND = (0,40,80)
BOARD_FG = (0,153,255)
BOARD_BG = (255,255,255)
SHIP_DARK = (128,128,128)
SHIP_LIGHT = (92,92,92)
MISS_COLOR = (255,255,255)
HIT_COLOR = (255,0,0)
FLASH_COLOR = (0,150,255)
TEXT_COLOR = (255,255,255)

pygame.init()
clock = pygame.time.Clock()
TITLE_FONT = pygame.font.SysFont(None,200)
GAME_FONT = pygame.font.SysFont(None,40)
TEXT_FONT = pygame.font.SysFont(None,24)

# TEMP BOARD DATA FOR TESTING #
board1 = [[0 for x in range(NUM_CELLS)] for x in range(NUM_CELLS)]
board2 = [[0 for x in range(NUM_CELLS)] for x in range(NUM_CELLS)]

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

#HIT_SURF = pygame.transform.scale(makeSurfFromASCII(HIT_ASCII, HIT_COLOR), (CELL_WIDTH, CELL_WIDTH))

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

def startScreen(surf):

    surf.fill(BACKGROUND)
        
    ready = False
    connected = False
    while not ready:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if connected == True and \
            (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or \
            event.type == pygame.MOUSEBUTTONDOWN:
                ready = True

        if not connected:
            delay = 1000
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
    

def main():
    mainSurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    flashSurface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    flashSurface.fill(FLASH_COLOR)

    pygame.display.set_caption('BATTLESHIP')

    startScreen(mainSurface)
    #setupScreen(mainSurface)

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

                if pos[0] >= P_BOARD_POSX + CELL_BORDER and pos[0] <= P_BOARD_POSX + BOARD_WIDTH \
                and pos[1] >= P_BOARD_POSY + CELL_BORDER and pos[1] <= P_BOARD_POSY + BOARD_HEIGHT:
                    col = (pos[0] - P_BOARD_POSX - CELL_BORDER) // (CELL_WIDTH + CELL_MARGIN)
                    row = (pos[1] - P_BOARD_POSY - CELL_BORDER) // (CELL_WIDTH + CELL_MARGIN)
                    board1[row][col] = 7
                    yourTurn = True

                if pos[0] >= O_BOARD_POSX + CELL_BORDER and pos[0] <= O_BOARD_POSX + BOARD_WIDTH \
                and pos[1] >= O_BOARD_POSY + CELL_BORDER and pos[1] <= O_BOARD_POSY + BOARD_HEIGHT:
                    col = (pos[0] - O_BOARD_POSX - CELL_BORDER) // (CELL_WIDTH + CELL_MARGIN)
                    row = (pos[1] - O_BOARD_POSY - CELL_BORDER) // (CELL_WIDTH + CELL_MARGIN)
                    board2[row][col] = 7
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
        drawBoard(mainSurface, board1, (P_BOARD_POSX, P_BOARD_POSY))

        # OPPONENT BOARD #
        drawText("ENEMY",
                 mainSurface,
                 GAME_FONT,
                 O_BOARD_POSX+(BOARD_WIDTH//2),
                 O_BOARD_POSY-30,
                 TEXT_COLOR,
                 BACKGROUND,
                 'center')
        drawBoard(mainSurface, board2, (O_BOARD_POSX, O_BOARD_POSY))

        pygame.display.update()

    pygame.quit()
    sys.exit()        

if __name__ == '__main__':
    main()
