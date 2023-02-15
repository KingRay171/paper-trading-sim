import pygame

file = open('sett.txt')
  
# read the content of the file opened
content = file.readlines()

SCREEN_WIDTH = int(content[0])
SCREEN_HEIGHT = int(content[1])


class Projectile(pygame.sprite.Sprite):

    def check_hit(self, enemies, damage):
        for enemy in enemies:
            if not (enemy in self.hitCashe):
              self.hit()
              enemy.hit(damage)
              self.hitCashe.append(enemy)
              if (self.peirce<=0):
                break
              
      
    def render(self, screen):
        screen.blit(self.surf, self.rect)

    def __init__(self, x, y, target, speed, peirce):
        super(Projectile, self).__init__()
        self.surf = pygame.Surface((10, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(center=(
            x,
            y,
        ))
        self.xVel = target[0]*speed
        self.yVel = target[1]*speed
        self.x = x 
        self.y = y
        self.peirce = peirce
        self.hitCashe = []
      
    def hit(self):   
      if (self.peirce<=1):
        self.kill()
      self.peirce -=1

    def clear(self):
      # Keep player on the screen
        if self.rect.left < 0:
            self.kill()
        if self.rect.right > SCREEN_WIDTH:
            self.kill()
        if self.rect.top <= 0:
            self.kill()
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.kill()
          
    def update(self, deltaTime):
        self.x += self.xVel * deltaTime
        self.y += self.yVel * deltaTime

        roundx = round(self.x)
        roundy = round(self.y)
        self.rect.topleft = roundx, roundy