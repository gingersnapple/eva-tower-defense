import pygame as pygame
import random
import time
import math

from pygame.locals import (
    RLEACCEL,
    K_w,
    K_s,
    K_a,
    K_d,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    FULLSCREEN,
)

# Setup the clock for a decent framerate
clock = pygame.time.Clock()
framerate = 30
plrSpd = 8
screen_width = 1536
screen_height = 864
plrScale = 3
dogScale = 3
mnstrScale = int(3)
wallScale = 6


# (48*8)/64

# define player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("dad1.png").convert_alpha()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        print(self.rect)
        # replace new_width and new_height with the desired width and height
        center = self.rect.center
        self.surf = pygame.transform.scale(self.surf,
                                           (self.surf.get_size()[0] * plrScale, self.surf.get_size()[1] * plrScale))
        self.rect = self.surf.get_rect()
        self.rect.center = center


    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_w]:
            self.rect.move_ip(0, -plrSpd)
        if pressed_keys[K_s]:
            self.rect.move_ip(0, plrSpd)
        if pressed_keys[K_a]:
            self.rect.move_ip(-plrSpd, 0)
        if pressed_keys[K_d]:
            self.rect.move_ip(plrSpd, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()

        self.surf = pygame.image.load("sombi1.png").convert_alpha()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

        # replace new_width and new_height with the desired width and height
        self.surf = pygame.transform.scale(self.surf,
                                           (self.surf.get_size()[0] * mnstrScale, self.surf.get_size()[1] * mnstrScale))

        # spawn somewhere random on the right edge
        self.rect = self.surf.get_rect(
            center=(
                random.randint(screen_height + 20, screen_width + 100),
                random.randint(0, screen_height),
            )
        )
        self.speed = random.randint(5, 20)

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class Wall(pygame.sprite.Sprite):
    def __init__(self, sprt, pos):
        super(Wall, self).__init__()
        self.surf = pygame.image.load(sprt).convert()
        self.rect = self.surf.get_rect()

        # replace new_width and new_height with the desired width and height
        self.surf = pygame.transform.scale(self.surf,
                                           (self.surf.get_size()[0] * wallScale, self.surf.get_size()[1] * wallScale))
        self.rect = ((pos[0] * 48), (pos[1] * 48))


class Doggy(pygame.sprite.Sprite):
    def __init__(self):
        super(Doggy, self).__init__()
        self.surf = pygame.image.load('dog1.png').convert_alpha()
        self.rect = self.surf.get_rect()

        # replace new_width and new_height with the desired width and height
        self.surf = pygame.transform.scale(self.surf,
                                           (self.surf.get_size()[0] * dogScale, self.surf.get_size()[1] * dogScale))
        self.rect = ((15 * 48 + 21), (9 * 48))


# initialize pygame
pygame.init()

# setup game window
screen = pygame.display.set_mode((screen_width, screen_height), FULLSCREEN)

# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

# wall.image = pygame.image.load("wall-long.png").convert()

# instantiate player
player = Player()
dog = Doggy()

# draw fence
wall_L1 = Wall("wall-long.png", (6, 3))
wall_L2 = Wall("wall-long.png", (18, 3))
wall_L3 = Wall("wall-long.png", (6, 14))
wall_L4 = Wall("wall-long.png", (18, 14))
wall_L5 = Wall("wall-long.png", (12, 7))
wall_S1 = Wall("wall-side.png", (3, 6))
wall_S2 = Wall("wall-side.png", ((28 * 48 + 24) / 48, 6))
wall_SS1 = Wall("wall-short-side.png", (7, 7))
wall_SS2 = Wall("wall-short-side.png", ((24 * 48 + 24) / 48, 7))
wall_SF1 = Wall("wall-short-l.png", (8, 11))
wall_SF2 = Wall("wall-short-r.png", (22, 11))
wall_SB1 = Wall("wall-short-l.png", (8, 7))
wall_SB2 = Wall("wall-short-r.png", (22, 7))

# Create groups to hold enemy sprites and all sprites
# - enemies is used for collision detection and position updates
# - all_sprites is used for rendering
enemies = pygame.sprite.Group()
walls = pygame.sprite.Group()
walls.add(wall_L1, wall_L2, wall_L3, wall_L4, wall_L5, wall_S1, wall_S2, wall_SS1, wall_SS2, wall_SF1, wall_SF2,
          wall_SB1, wall_SB2)
sprites = [walls, dog, player]

all_sprites = pygame.sprite.Group()
for s in sprites:
    all_sprites.add(s)


running = True

while running:
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

            # Add a new enemy?
        elif event.type == ADDENEMY:
            # Create the new enemy and add it to sprite groups
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)
    enemies.update()

    screen.fill((25, 36, 26))

    # draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Check if any enemies have collided with the player
    # if pygame.sprite.spritecollideany(player, enemies):
    # If so, then remove the player and stop the loop
    # player.kill()
    # running = False

    # Check if any walls have collided with the player

    # update display
    pygame.display.flip()

    # Ensure program maintains a rate of 30 frames per second
    clock.tick(framerate)
