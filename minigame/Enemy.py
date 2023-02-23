import pygame
import mathStuff

file = open('minigame/sett.txt')

# read the content of the file opened
content = file.readlines()

SCREEN_WIDTH = int(content[0])
SCREEN_HEIGHT = int(content[1])
ENEMY_SPEED = float(content[4])

class Enemy(pygame.sprite.Sprite):
    def render(self, screen):
      screen.blit(self.surf, self.rect)

    def hit(self, damage):
      self.hp -=damage
      if self.hp <= 0:
          self.kill()

    def __init__(self, x, y, hp):
        super(Enemy, self).__init__()

        self.surf = pygame.image.load("minigame/Resources/coin.png").convert_alpha()

        self.surf = pygame.transform.scale(self.surf, (40, 40))
        self.rect = self.surf.get_rect(center=(
            x,
            y,
        ))
        self.x = x
        self.y = y

        self.hp = hp

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self, deltaTime, target):
        direction = ((target[0] - self.rect.x), (target[1] - self.rect.y))
        target = mathStuff.normalize_vector(direction)
        self.x += target[0]* ENEMY_SPEED * deltaTime
        self.y += target[1]* ENEMY_SPEED * deltaTime

        roundx = round(self.x)
        roundy = round(self.y)
        self.rect.topleft = roundx, roundy

