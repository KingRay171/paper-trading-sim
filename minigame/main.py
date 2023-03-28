from Player import Player
from Enemy import Enemy
import button
import pygame, sys
import math
import random
from bs4 import BeautifulSoup

import os

def run_game():
  #----------------------INITIALIZE VARS----------------
  #file path names
  settfile = 'minigame/sett.txt'
  deathsoundfile = "minigame/Resources/die.wav"
  upgrades = ["minigame/Resources/Pierce.png", "minigame/Resources/Faster.png", "minigame/Resources/Damage.png","minigame/Resources/Speed.png"]
  playerspritep = "minigame/Resources/block.png"
  backgroundp = "minigame/Resources/background.jpeg"
  enemyspritep = "minigame/Resources/Bill.png"
  bulletspritep = "minigame/Resources/coin.png"
  
  #read from sett.txt 
  file = open(settfile)
  content = file.readlines()
  SCREEN_WIDTH = int(content[0])
  SCREEN_HEIGHT = int(content[1])
  ENEMY_SPEED = float(content[4])
  
  # start pygame stuff
  pygame.mixer.init()
  pygame.init()
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  from pygame.locals import (
      K_ESCAPE,
      K_SPACE,
      KEYDOWN,
      K_RETURN,
      QUIT,
  )
  clock = pygame.time.Clock()

  #get sound affects
  death_sound = pygame.mixer.Sound(deathsoundfile)
  
  #get sprites
  bg = pygame.image.load(backgroundp)

  resume_img = pygame.image.load(playerspritep).convert_alpha()
  resume_img = pygame.transform.scale(resume_img, (200, 240))
  resume_img = pygame.transform.flip(resume_img, True, False)

  pierce_img = pygame.image.load(upgrades[0]).convert_alpha()
  faster_img = pygame.image.load(upgrades[1]).convert_alpha()
  damage_img = pygame.image.load(upgrades[2]).convert_alpha()
  speed_img = pygame.image.load(upgrades[3]).convert_alpha()

  BULLET_SURF = pygame.image.load(bulletspritep).convert_alpha()
  BULLET_SURF = pygame.transform.scale(BULLET_SURF, (20, 20))

  #set variables
  FRAME_COUNT = 60
  SPAWN_DELAY = 5000
  WAVE_SPAWN_DELAY = 200
  WAVE_BASE = 1000
  WAVE_RATE = 1.1
  ENEMY_SPRITE = 0

  #init variables that change regularly
  running = True
  game_over = False
  paused = True

  #make buttons
  resume_button = button.Button(420, 200, resume_img, 1)
  pierce_button = button.Button(0, 80, pierce_img, 1)
  faster_button = button.Button(125, 80, faster_img, 1)
  damage_button = button.Button(250, 80, damage_img, 1)  
  speed_button = button.Button(375, 80, speed_img, 1)

  #make fonts
  font = pygame.font.SysFont('arial', 50)
  fontsmall = pygame.font.SysFont('arial', 20)

  #make lines
  line1 = font.render("Stocker", True, (255, 255, 255))
  line2 = fontsmall.render("Space to pause and unpause. Click to shoot and WASD to move", True, (255, 255, 255))

  
  #make methods
  def colorize(image, newColor):
    image = image.copy()
          
    # add in new RGB values
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    return image
  
  def show_game_over():
      font = pygame.font.SysFont('arial', 30)
      line1 = font.render("Game is over!", True, (255, 255, 255))
      screen.blit(line1, ((SCREEN_WIDTH / 2) - 100, (SCREEN_HEIGHT / 2) - 60))
      line2 = font.render("Enter to restart", True, (255, 255, 255))
      screen.blit(line2, ((SCREEN_WIDTH / 2) - 100, (SCREEN_HEIGHT / 2)))
  
  
  def rewrite_line(line, text):
      with open(settfile, 'r') as file:
          # read a list of lines into data
          data = file.readlines()
      # now change the 2nd line, note that you have to add a newline
      data[line] = str(text) + '\n'
  
      # and write everything back
      with open(settfile, 'w') as file:
          file.writelines(data)
  
  def update_price(game, player):
      priceList = []
      base = 100
      rate = 1.2
      priceList.append(round(base * pow(rate, player.DART_PIERCE - 1)))
      priceList.append(round(base * pow(rate, player.FIRE_RATE - 1)))
      priceList.append(round(base * pow(rate, game.DART_DAMAGE - 1)))
      priceList.append(round(base * pow(rate, player.DART_SPEED - 3)))
  
      return priceList
  
  
  def draw_shop(game, player):
      screen.fill((52, 78, 91))
  
      line3 = fontsmall.render(f"Money:   {game.MONEY}", True, (255, 255, 255))
  
      lineUps = []
      lineUps.append(
          fontsmall.render(f"Peirce: {player.DART_PIERCE}", True,
                           (255, 255, 255)))
      lineUps.append(
          fontsmall.render(f"Fire Rate: {player.FIRE_RATE}", True,
                           (255, 255, 255)))
      lineUps.append(
          fontsmall.render(f"Damage: {game.DART_DAMAGE}", True, (255, 255, 255)))
      lineUps.append(
          fontsmall.render(f"Bullet speed: {player.DART_SPEED}", True,
                           (255, 255, 255)))
  
      prices = update_price(game, player)
  
      i = 0
      for line in lineUps:
          screen.blit(line, (125 * i, 150))
          i += 1
  
      price_text = []
      for price in prices:
          price_text.append(
              fontsmall.render(f"Cost: {price}", True, (255, 255, 255)))
  
      i = 0
      for price in prices:
          screen.blit(price_text[i], (125 * i, 180))
          i += 1
  
      screen.blit(line1, (10, 10))
      screen.blit(line2, (10, SCREEN_HEIGHT - 30))
      screen.blit(line3, (10, SCREEN_HEIGHT - 60))
  
      if pierce_button.draw(screen):
  
          if (game.buy(prices[0])):
              p = player.DART_PIERCE
              p += 1
              #print(p)
              rewrite_line(8, p)
              player.update_pierce(p)
  
      if faster_button.draw(screen):  #doesn't work yet
          if (game.buy(prices[1])):
              p = player.FIRE_RATE
              p += 1
              rewrite_line(3, p)
              player.update_fire(p)
  
      if damage_button.draw(screen):
          if (game.buy(prices[2])):
              game.DART_DAMAGE += 1
              rewrite_line(9, game.DART_DAMAGE)
  
      if speed_button.draw(screen):
          if (game.buy(prices[3])):
              p = player.DART_SPEED
              p += 1
              rewrite_line(7, p)
              player.update_speed(p)
  
      if resume_button.draw(screen):
          return True
  
      return False
  
  def render_background():
      for x in range(0, SCREEN_WIDTH, 220):
        for y in range(0, SCREEN_HEIGHT, 220):
          screen.blit(bg, (x, y))
      
  
  
  #make class
  class Game():
      def update_enemy_sprite(self):
        image = pygame.image.load(enemyspritep).convert_alpha()
      
        color = (0,0,0)
        match self.ENEMY_HP%8:
          case 1:
            color = (0,0,0)
          case 2:
            color = (255,0,0)
          case 3:
            color = (0,255,0)
          case 4:
            color = (0,0,255)
          case 5:
            color = (255,255,0)
          case 6:
            color = (255,0,255)
          case 7:
            color = (0,255,255)
          case 0:
            color = (255, 255, 255)
        image = colorize(image, color)
        
        return image
  
      def end_wave(self):
          pygame.time.set_timer(ADDENEMY, SPAWN_DELAY)
          print("stopped normal spawning")
  
          self.inWave = False
          if (self.ENEMY_WAVE <= 0):
              pygame.time.set_timer(WAVE_LENGTH, 0)
              print("wave end")
              rewrite_line(15, self.WAVE)
              rewrite_line(11, self.ENEMY_HP)
              pygame.time.set_timer(ADDENEMY, SPAWN_DELAY)
          else:
              print("waiting for wave to stop")
              print(self.ENEMY_WAVE)
              pygame.time.set_timer(WAVE_LENGTH, 1000)
  
          if (game_over):
              print("OVER")
              self.WAVE = int(content[15])
              self.inWave = False
              pygame.time.set_timer(WAVE_LENGTH, 0)
              game.ENEMY_WAVE = 0
  
              pygame.time.set_timer(ADDENEMY, 0)
  
      def start_wave(self):
          print("wave start")
  
          pygame.time.set_timer(WAVE_LENGTH,
                                round(WAVE_BASE * pow(WAVE_RATE, game.WAVE)))
          pygame.time.set_timer(ADDENEMY, WAVE_SPAWN_DELAY)
          self.inWave = True
          self.ENEMY_HP = 1 + math.floor(self.WAVE / 3)
          self.WAVE += 1
          self.update_enemy_sprite()
  
      def spawn(self, enemyGroup, allGroup):
          if (self.inWave):
              self.ENEMY_WAVE += 1
  
          ex = 0
          ey = 0
  
          r = random.randint(0, 3)
          if r == 0:
              ey = -20
              ex = r = random.randint(-20, SCREEN_WIDTH + 20)
          elif r == 1:
              ey = random.randint(-20, SCREEN_HEIGHT + 20)
              ex = SCREEN_WIDTH + 20
          elif r == 2:
              ey = SCREEN_HEIGHT + 20
              ex = r = random.randint(-20, SCREEN_WIDTH + 20)
          elif r == 3:
              ey = random.randint(-20, SCREEN_HEIGHT + 20)
              ex = -20
  
          new_enemy = Enemy(ex, ey, game.ENEMY_HP, ENEMY_SPRITE, ENEMY_SPEED)
          enemyGroup.add(new_enemy)
          allGroup.add(new_enemy)
  
      def buy(self, cost):
          path = rf"{os.getcwd()}/portfolio.xml"
  
  
          file = open(path, "r")
          contents = file.read()
          
          # parsing
          soup = BeautifulSoup(contents, 'xml')
          
          num = soup.find("amount").string
          
          self.MONEY = float(num)
          file.close()
  
          if self.MONEY >= cost:
              self.MONEY -= cost
              rewrite_line(13, self.MONEY)
              
              soup.find("amount").string=str(self.MONEY)
          
              f = open(path, "w")
              f.write(soup.prettify())
              f.close()
              
              return True
          return False
  
  # Create the new enemy and add it to sprite groups
  
      def __init__(self):
          self.time = 0
          self.lastSpawn = 0
          self.MONEY = float(content[13])
  
          self.inWave = False
          self.WAVE = int(content[15])
          self.DART_DAMAGE = int(content[9])
          self.ENEMY_HP = int(content[11])
  
          self.ENEMY_WAVE = 0
  
      def tickTimer(self, deltaTime):
          self.time += deltaTime
  
  
  # Create the 'player'
  
  
  

  #create instances
  player = Player(BULLET_SURF)
  game = Game()
  game.buy(0)

  #create sprite groups
  bullets = pygame.sprite.Group()
  enemies = pygame.sprite.Group()
  all_sprites = pygame.sprite.Group()
  all_sprites.add(player)

  # Create a custom events
  ADDENEMY = pygame.USEREVENT + 1
  pygame.time.set_timer(ADDENEMY, 0)
  CLEAR_PROJ = pygame.USEREVENT + 2
  pygame.time.set_timer(CLEAR_PROJ, 1000)
  WAVE_LENGTH = pygame.USEREVENT + 3
  pygame.time.set_timer(WAVE_LENGTH, 0)
  
  #idk man
  ENEMY_SPRITE = game.update_enemy_sprite()
  
  
  # Main loop
  while running:
      deltaTime = clock.get_time() / 20
  
      # Look at every event in the queue
      for event in pygame.event.get():
          # Did the user hit a key?
          if event.type == KEYDOWN:
              # Was it the Escape key? If so, stop the loop.
              if event.key == pygame.K_SPACE:
                  if (not game.inWave):
                      paused = not paused
  
                      if paused:
                          print("game is paused")
                          game.buy(0)
                          pygame.time.set_timer(ADDENEMY, 0)
                      else:
                          pygame.time.set_timer(ADDENEMY, SPAWN_DELAY)
                          print("start spawning")
  
              if event.key == K_ESCAPE:
                  running = False
  
              if event.key == K_RETURN:
                  if game_over:
                      #reset
                      game_over = False
                      for entity in all_sprites:
                          entity.kill()
  
                      player = Player(BULLET_SURF)
                      all_sprites.add(player)
                      pygame.time.set_timer(WAVE_LENGTH, 0)
                      pygame.time.set_timer(ADDENEMY, SPAWN_DELAY)
  
                  elif (not game.inWave) and (not paused):
                      game.start_wave()
  
          # Did the user click the window close button? If so, stop the loop.
          elif event.type == QUIT:
              running = False
              pygame.quit()
  
          elif event.type == ADDENEMY:
              # Create the new enemy and add it to sprite groups
              game.spawn(enemies, all_sprites)
  
          elif event.type == CLEAR_PROJ:
              for projectileGroup in bullets:
                  projectileGroup.clear()
  
          elif event.type == WAVE_LENGTH:
              game.end_wave()
  
      if paused:
          if (draw_shop(game, player)):
              paused = False
  
      # Get the set of keys pressed and check for user input
      if game_over == False and paused == False:
          pressed_keys = pygame.key.get_pressed()
  
          game.tickTimer(deltaTime)
          player.update(pressed_keys, deltaTime)
          mouse = pygame.mouse.get_pressed()
          player.process_mouse(mouse, player, deltaTime, bullets, all_sprites)
  
          # spawn
          #game.spawn_time(enemies, bullets, all_sprites)
  
          # Update enemy position
          bullets.update(deltaTime)
  
          target = player.x, player.y
          # Update enemy position
          enemies.update(deltaTime, target)
  
          # Fill the screen with black
          # screen.fill((0, 0, 0))
          render_background()
  
          # Draw all sprites
          for entity in all_sprites:
              entity.render(screen)
  
          # KILL Check if any enemies have collided with the player
          if pygame.sprite.spritecollideany(player, enemies):
              # If so, then remove the player and stop the loop
  
              game_over = True
              pygame.mixer.Sound.play(death_sound)
              render_background()
              player.render(screen)
              player.kill()
              show_game_over()
              pygame.time.set_timer(WAVE_LENGTH, 0)
              pygame.time.set_timer(ADDENEMY, 0)
              game.WAVE = int(content[15])
              game.inWave = False
              game.ENEMY_WAVE = 0
  
          for proj in bullets:
              enemyhit = pygame.sprite.spritecollide(proj, enemies, False)
  
              if enemyhit:
                  game.ENEMY_WAVE = max(game.ENEMY_WAVE - 1, 0)
                  proj.check_hit(enemyhit, game.DART_DAMAGE)
  
          line = 0
          line2 = fontsmall.render(f"Wave: {game.WAVE}", True, (255, 255, 255))
          if (game.ENEMY_WAVE == 0):
              line = fontsmall.render("Hit enter to start a wave", True,
                                      (255, 255, 255))
          else:
              line = fontsmall.render(f"Enemies left: {game.ENEMY_WAVE}", True,
                                      (255, 255, 255))
  
          screen.blit(line2, (10, 10))
          screen.blit(line, (10, 40))
  
      # Draw the player on the screen
      #screen.blit(player.surf, player.rect)
  
      # Update the display
      pygame.display.flip()
      clock.tick(FRAME_COUNT)

  pygame.quit()
  

run_game()
