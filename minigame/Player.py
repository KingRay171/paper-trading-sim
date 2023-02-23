import pygame
import mathStuff
from Projectile import Projectile
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

file = open('minigame/sett.txt')

# read the content of the file opened
content = file.readlines()

SCREEN_WIDTH = int(content[0])
SCREEN_HEIGHT = int(content[1])
SPEED = int(content[2])



class Player(pygame.sprite.Sprite):
    def render(self, screen):
        screen.blit(self.surf, (self.rect.x - 30, self.rect.y-35))

    def update_speed(self, num):
        self.DART_SPEED = num
    def update_pierce(self, num):
        self.DART_PIERCE = num

    def update_fire(self,num):
        #print(num)
        self.FIRE_RATE = num


    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("minigame/Resources/block.png").convert_alpha()

        self.surf = pygame.transform.scale(self.surf, (50, 60))

        self.rect = pygame.Rect(0, 0, 10, 10)
        self.x = SCREEN_WIDTH/2
        self.y = SCREEN_HEIGHT/2
        self.fire_timer = 60

        self.DART_SPEED = int(content[7])
        self.DART_PIERCE = int(content[8])
        self.FIRE_RATE = int(content[3])

        # Move the sprite based on user keypresses
    def update(self, pressed_keys, deltaTime):
        target = [0, 0]
        if pressed_keys[K_UP]:
            target[1]-=1
        if pressed_keys[K_DOWN]:
            target[1]+=1
        if pressed_keys[K_LEFT]:
            target[0]-=1
        if pressed_keys[K_RIGHT]:
            target[0]+=1

        target = mathStuff.normalize_vector(target)
        self.x += target[0]* SPEED * deltaTime
        self.y += target[1]* SPEED * deltaTime

        roundx = round(self.x)
        roundy = round(self.y)
        self.rect.topleft = roundx, roundy

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT



        # Define the enemy object by extending pygame.sprite.Sprite

    def process_mouse(self, mouse, hero, deltaTime, bullets, all_sprites):
        if mouse[0]:
            self.fire_timer += (deltaTime*self.FIRE_RATE)
            if self.fire_timer >= 60:
              while self.fire_timer >=60:
                self.fire_timer -= 60
                self.shoot(pygame.mouse.get_pos(), bullets, all_sprites)
        else:
          self.fire_timer = min(60, self.fire_timer+(deltaTime*self.FIRE_RATE))

    def shoot(self, mousePos, bullets, all_sprites):

        direction = ((mousePos[0] - self.rect.x), (mousePos[1] - self.rect.y))
        target = mathStuff.normalize_vector(direction)

        bullet = Projectile(self.rect.x, self.rect.y, target ,self.DART_SPEED, self.DART_PIERCE)
        bullets.add(bullet)
        all_sprites.add(bullet)


