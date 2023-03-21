import pygame
pygame.mixer.init()

#file = open('sett.txt')
  
# read the content of the file opened
#content = file.readlines()

#SCREEN_WIDTH = int(content[0])
#SCREEN_HEIGHT = int(content[1])


class Projectile(pygame.sprite.Sprite):

    def check_hit(self, enemies, damage):
        for enemy in enemies:
            if not (enemy in self.hitCashe):
              self.hit()
              pygame.mixer.Sound.play(self.hitsfx)
              enemy.hit(damage)
              self.hitCashe.append(enemy)
              if (self.peirce<=0):
                break
              
      
    def render(self, screen):
        screen.blit(self.surf, self.rect)

    def __init__(self, x, y, target, speed, peirce, surf, hitsfx):
        super(Projectile, self).__init__()
        self.surf = surf
        self.rect = self.surf.get_rect(center=(
            x,
            y,
        ))
        self.x = x
        self.y = y
        self.xVel = target[0]*speed
        self.yVel = target[1]*speed
        self.x = x 
        self.y = y
        self.peirce = peirce
        self.hitCashe = []
        self.hitsfx = hitsfx
      
    def hit(self):   
      if (self.peirce<=1):
        self.kill()
      self.peirce -=1

    def clear(self):
      # Keep player on the screen
        if self.rect.left < 0:
            self.kill()
        if self.rect.right > 800:
            self.kill()
        if self.rect.top <= 0:
            self.kill()
        if self.rect.bottom >= 600:
            self.kill()
          
    def update(self, deltaTime):
        self.x += self.xVel * deltaTime
        self.y += self.yVel * deltaTime

        roundx = round(self.x)
        roundy = round(self.y)
        self.rect.topleft = roundx, roundy
