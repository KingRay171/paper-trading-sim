import pygame
import mathStuff

class Enemy(pygame.sprite.Sprite):
    def render(self, screen):
      screen.blit(self.surf, self.rect)

    def hit(self, damage):
      self.hp -=damage
      if self.hp <= 0:
          self.kill()

    def __init__(self, x, y, hp ,sprite, speed):
        super(Enemy, self).__init__()

        self.hp = hp
      
        self.surf = sprite
        self.speed = speed
      
        self.surf = pygame.transform.scale(self.surf, (60, 60))
        self.rect = self.surf.get_rect(center=(
            x,
            y,
        ))
        self.x = x
        self.y = y
        

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self, deltaTime, target):
        direction = ((target[0] - self.rect.x), (target[1] - self.rect.y))
        target = mathStuff.normalize_vector(direction)
        self.x += target[0]* self.speed * deltaTime
        self.y += target[1]* self.speed * deltaTime

        roundx = round(self.x)
        roundy = round(self.y)
        self.rect.topleft = roundx, roundy

