import pygame
import sys

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BACKGROUND = (0,40,80)
BOARD_FG = (0,153,255)
BOARD_BG = (255,255,255)
FRAMERATE = 60
SHIP_DARK = (128,128,128)
SHIP_LIGHT = (92,92,92)
MISS_COLOR = (255,255,255)
HIT_COLOR = (255,0,0)

pygame.init()
clock = pygame.time.Clock()
GAME_FONT = pygame.font.SysFont(None,20)

def drawBoard(screen, x, y):
    cell = 40
    border = 4
    margin = 2
    width = (cell + margin) * 10 + border + margin
    height = width
    image = pygame.Surface([width, height])
    pygame.draw.rect(image, BOARD_BG, [0, 0, width, height])

    for row in range(10):
        for col in range(10):
            # CODE FOR SHIP/SHOT DATA HERE
            pygame.draw.rect(image, BOARD_FG, [(cell + margin) * col + border,
                                               (cell + margin) * row + border,
                                                cell, cell])
            
    screen.blit(image, (x,y))

def main():
    mainSurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('BATTLESHIP')

    #showStartScreen(mainSurface)

    done = False
    while not done:
        clock.tick(FRAMERATE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True

            mainSurface.fill(BACKGROUND)
            drawBoard(mainSurface, 50, 50)
            drawBoard(mainSurface, 600, 50)

            pygame.display.update()

    pygame.quit()
    sys.exit()        

if __name__ == '__main__':
    main()
