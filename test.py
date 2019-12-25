import random
import pygame
import math
import time

BACKGROUND = (0, 50, 150)
PIXEL_SIZE = 10
PIXEL_COLOR = (255, 0, 0)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

MY_EVENT = pygame.USEREVENT + 0

class Pixel(pygame.sprite.Sprite):

    def __init__(self, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((PIXEL_SIZE, PIXEL_SIZE))
        self.image.fill(PIXEL_COLOR)
        self.rect = self.image.get_rect()
        self.angle = random.random()*(2*math.pi)
        self.rect.x = x
        self.rect.y = y
        self.speed = random.random()*20
        self.image.set_alpha(255)

    def update(self, *args):
        if self.rect.x > SCREEN_WIDTH - PIXEL_SIZE or self.rect.x < 0:
            self.angle = math.pi - self.angle
        if self.rect.y > SCREEN_HEIGHT - PIXEL_SIZE or self.rect.y < 0:
            self.angle *= -1
        self.rect.x += int(self.speed * math.cos(self.angle))
        self.rect.y += int(self.speed * math.sin(self.angle))
        self.image.set_alpha(self.image.get_alpha() - 1)
        if self.image.get_alpha() <= 0:
            self.kill()
            del self

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pixels = pygame.sprite.RenderPlain(())
posx = SCREEN_WIDTH // 2
posy = SCREEN_HEIGHT // 2

ts = pygame.time.get_ticks()

done = False
while not done:
    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i in range(100):
                    x, y = pygame.mouse.get_pos()
                    pixels.add(Pixel(x, y))

        if event.type == MY_EVENT:
            print(event.temp)

    # Movement #
    pixels.update()

    # Screen painting #
    screen.fill(BACKGROUND)

    pixels.draw(screen)

    pygame.display.update()

    if pygame.time.get_ticks() - ts > 5000:
        ts = pygame.time.get_ticks()
        pygame.event.post(pygame.event.Event(MY_EVENT, temp="MY EVENT WORKED"))

pygame.quit()
