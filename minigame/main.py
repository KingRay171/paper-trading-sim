from Player import Player
from Enemy import Enemy
import button
import pygame, sys
import math
from pygame.locals import QUIT
# Import random for random numbers
import random
# Import the pygame module

# Define constants for the screen width and height
file = open('minigame/sett.txt')

# read the content of the file opened
content = file.readlines()

SCREEN_WIDTH = int(content[0])
SCREEN_HEIGHT = int(content[1])

FRAME_COUNT = 60
SPAWN_DELAY = 5000
WAVE_SPAWN_DELAY = 200
WAVE_BASE = 1000
WAVE_RATE = 1.1

# Initialize pygame
pygame.init()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    K_RETURN,
    QUIT,
)

clock = pygame.time.Clock()


def show_game_over():
    font = pygame.font.SysFont('arial', 30)
    line1 = font.render("Game is over!", True, (255, 255, 255))
    screen.blit(line1, ((SCREEN_WIDTH / 2) - 100, (SCREEN_HEIGHT / 2) - 60))
    line2 = font.render("Enter to restart", True, (255, 255, 255))
    screen.blit(line2, ((SCREEN_WIDTH / 2) - 100, (SCREEN_HEIGHT / 2)))


#create buttons
resume_img = pygame.image.load("minigame/Resources/block.png").convert_alpha()
resume_img = pygame.transform.scale(resume_img, (200, 240))
resume_img = pygame.transform.flip(resume_img, True, False)
resume_button = button.Button(420, 200, resume_img, 1)

pierce_img = pygame.image.load("minigame/Resources/Pierce.png").convert_alpha()
pierce_button = button.Button(0, 80, pierce_img, 1)

faster_img = pygame.image.load("minigame/Resources/Faster.png").convert_alpha()
faster_button = button.Button(125, 80, faster_img, 1)

damage_img = pygame.image.load("minigame/Resources/Damage.png").convert_alpha()
damage_button = button.Button(250, 80, damage_img, 1)

speed_img = pygame.image.load("minigame/Resources/Speed.png").convert_alpha()
speed_button = button.Button(375, 80, speed_img, 1)


def rewrite_line(line, text):
    with open('minigame/sett.txt', 'r') as file:
        # read a list of lines into data
        data = file.readlines()
    # now change the 2nd line, note that you have to add a newline
    data[line] = str(text) + '\n'

    # and write everything back
    with open('minigame/sett.txt', 'w') as file:
        file.writelines(data)


font = pygame.font.SysFont('arial', 50)
fontsmall = pygame.font.SysFont('arial', 20)
line1 = font.render("Stocker", True, (255, 255, 255))
line2 = fontsmall.render("Space to pause and unpause", True, (255, 255, 255))


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


bg = pygame.image.load("minigame/Resources/background.jpeg")


def render_background():

    screen.blit(bg, (0, 0))
    screen.blit(bg, (0, 220))
    screen.blit(bg, (220, 220))
    screen.blit(bg, (440, 220))
    screen.blit(bg, (220, 0))
    screen.blit(bg, (440, 0))


class Game():

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

        pygame.time.set_timer(WAVE_LENGTH, round(WAVE_BASE * pow(WAVE_RATE, game.WAVE)))
        pygame.time.set_timer(ADDENEMY, WAVE_SPAWN_DELAY)
        self.inWave = True
        self.ENEMY_HP = 1 + math.floor(self.WAVE / 10)
        self.WAVE += 1

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

        new_enemy = Enemy(ex, ey, game.ENEMY_HP)
        enemyGroup.add(new_enemy)
        allGroup.add(new_enemy)

    def buy(self, cost):
        if self.MONEY >= cost:
            self.MONEY -= cost
            rewrite_line(13, self.MONEY)
            return True
        return False

# Create the new enemy and add it to sprite groups

    def __init__(self):
        self.time = 0
        self.lastSpawn = 0
        self.MONEY = int(content[13])

        self.inWave = False
        self.WAVE = int(content[15])
        self.DART_DAMAGE = int(content[9])
        self.ENEMY_HP = int(content[11])

        self.ENEMY_WAVE = 0

    def tickTimer(self, deltaTime):
        self.time += deltaTime


# Create the 'player'
player = Player()
game = Game()

# Create groups to hold enemy sprites and all sprites
# - enemies is used for collision detection and position updates
# - all_sprites is used for rendering
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Variable to keep the main loop running
running = True
game_over = False
paused = True

# Main loop
# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 0)
CLEAR_PROJ = pygame.USEREVENT + 2
pygame.time.set_timer(CLEAR_PROJ, 1000)
WAVE_LENGTH = pygame.USEREVENT + 3
pygame.time.set_timer(WAVE_LENGTH, 0)

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

                    player = Player()
                    all_sprites.add(player)
                    pygame.time.set_timer(WAVE_LENGTH, 0)
                    pygame.time.set_timer(ADDENEMY, SPAWN_DELAY)

                elif (not game.inWave) and (not paused):
                    game.start_wave()

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

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
