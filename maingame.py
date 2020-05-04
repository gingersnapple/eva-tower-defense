import pygame
from pygame.locals import (FULLSCREEN)
import math
import random

# -- Global constants

# Colors
BACKDROP = (168, 238, 121)
creature_scale = 3
wall_scale = 6
framerate = 30
plr_speed = 6
som_speed = 0.5
plr_x = 10
plr_y = 500
turretcount = 7

# Screen dimensions
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 864
fullscreen = False


class Player(pygame.sprite.Sprite):
    # Constructor function
    def __init__(self, x, y):
        # Call the parent's constructor
        super(Player, self).__init__()
        self.x = x
        self.y = y
        self.image = pygame.image.load("dad1.png").convert_alpha()
        self.rect = self.image.get_rect()
        # replace new_width and new_height with the desired width and height
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_size()[0] * creature_scale,
                                             self.image.get_size()[1] * creature_scale))
        self.rect = self.image.get_rect()
        # (top left x, top left y, width, height)
        # Make our top-left corner the passed-in location.
        self.rect.y = y
        self.rect.x = x

        # Set speed vector
        self.change_x = 0
        self.change_y = 0
        self.walls = None

    def update(self):
        # move to hitbox
        self.rect.x = hitbox.rect.x
        self.rect.y = (hitbox.rect.y - 48)


class Hitbox(Player):
    def __init__(self):
        super(Hitbox, self).__init__(10, 500)
        self.surf = pygame.Surface((42, 15))
        self.rect = self.surf.get_rect()

        self.rect.x = player.x
        self.rect.y = (player.y + 48)

    def changespeed(self, x, y):
        self.change_x += x
        self.change_y += y

    def update(self):
        # Move left/right
        self.rect.x += self.change_x

        for w in self.walls:
            if self.rect.colliderect(w.rect):
                if self.change_x > 0:
                    self.rect.right = w.rect.left
                else:
                    # Otherwise if we are moving left, do the opposite.
                    self.rect.left = w.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        for w in self.walls:
            if self.rect.colliderect(w.rect):
                if self.change_y > 0:
                    self.rect.bottom = w.rect.top
                else:
                    # Otherwise if we are moving left, do the opposite.
                    self.rect.top = w.rect.bottom

        # dont go off screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 48:
            self.rect.top = 48
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        player.update()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()

        self.image = pygame.image.load('sombi1.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = som_speed

        # replace new_width and new_height with the desired width and height
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_size()[0] * creature_scale,
                                             self.image.get_size()[1] * creature_scale))
        self.type = random.randrange(1, 6)

        if self.type == 1:
            self.agenda = [[1, 1], [5, 4], [5, 12], [15, 12], [15, 9]]

        elif self.type == 2:
            self.agenda = [[16, 1], [16, 4], [11, 4], [11, 9], [15, 9]]

        elif self.type == 3:
            self.agenda = [[30, 1], [26, 4], [21, 4], [20.5, 9], [15, 9]]

        elif self.type == 4:
            self.agenda = [[1, 16], [14, 16], [15, 9]]

        elif self.type == 5:
            self.agenda = [[30, 16], [26, 12], [19, 12], [15, 9]]

        for i in self.agenda:
            i[0] = i[0] * 48
            i[1] = i[1] * 48

        self.rect = self.agenda[0]
        self.dx = 0
        self.dy = 0
        self.steps = 0
        self.goal = (0, 0)
        self.stage = 1
        self.startup = True
        self.moving = False

    def moveto(self, point):
        px = int(point[0])
        py = int(point[1])
        x = px - self.rect[0]
        y = py - self.rect[1]
        v = self.speed
        s = math.sqrt((x ** 2) + (y ** 2))
        self.dx = v * (x / s)
        self.dy = v * (y / s)
        self.steps = round(s / v)
        self.goal = (point[0], point[1])
        self.moving = True

    def update(self):
        if self.startup:
            self.moveto(self.agenda[1])
            self.startup = False

        if self.moving:
            self.rect = (self.rect[0] + self.dx, self.rect[1] + self.dy)
            self.steps -= 1
            if self.steps < 1:
                self.moving = False
                # uncomment for glitchy but precise ending
                # self.rect = self.goal
                if self.stage + 1 < len(self.agenda):
                    self.stage += 1
                    self.moveto(self.agenda[self.stage])
                else:
                    self.kill()


class Wall(pygame.sprite.Sprite):
    def __init__(self, sprite, pos):
        # Call the parent's constructor
        super(Wall, self).__init__()
        self.image = pygame.image.load(sprite).convert()
        self.rect = self.image.get_rect()

        # replace new_width and new_height with the desired width and height
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_size()[0] * wall_scale,
                                             self.image.get_size()[1] * wall_scale))

        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.x = (pos[0])
        self.rect.y = (pos[1])


class Dog(pygame.sprite.Sprite):
    def __init__(self):
        super(Dog, self).__init__()
        self.image = pygame.image.load('dog1.png').convert_alpha()
        self.rect = self.image.get_rect()

        # replace new_width and new_height with the desired width and height
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_size()[0] * creature_scale,
                                             self.image.get_size()[1] * creature_scale))
        self.rect = ((15 * 48 + 21), (9 * 48))


class Turret(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Turret, self).__init__()
        self.image = pygame.image.load('turret1.png').convert_alpha()
        self.rect = self.image.get_rect()

        # replace new_width and new_height with the desired width and height
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_size()[0] * creature_scale,
                                             self.image.get_size()[1] * creature_scale))
        self.rect = self.image.get_rect()
        self.rect.x = (pos[0])
        self.rect.y = (pos[1])


# Call this function so the Pygame library can initialize itself
pygame.init()

if fullscreen:
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], FULLSCREEN)
else:
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

# make mouse cursor invisible
pygame.mouse.set_visible(0)

# Set the title of the window
pygame.display.set_caption('A Dad and his Dog')

# List to hold all the sprites
all_sprites = pygame.sprite.Group()

# Make the walls.
sc = 48
wall_list = pygame.sprite.Group()
wall_L1 = Wall("wall-long.png", (6 * sc, 2 * sc))
wall_L2 = Wall("wall-long.png", (18 * sc, 2 * sc))
wall_L3 = Wall("wall-long.png", (6 * sc, 14 * sc))
wall_L4 = Wall("wall-long.png", (18 * sc, 14 * sc))
wall_L5 = Wall("wall-long.png", (12 * sc, 6 * sc))
wall_S1 = Wall("wall-side.png", (3 * sc, 6 * sc))
wall_S2 = Wall("wall-side.png", (28 * sc, 6 * sc))

wall_SS1 = Wall("wall-short-side.png", (7 * sc, 6 * sc))
wall_SS2 = Wall("wall-short-side.png", (24 * sc - 6, 6 * sc))
wall_SF1 =  Wall("wall-short-l.png", (8 * sc + 6, 10 * sc))
wall_SB1 = Wall("wall-short-l.png", (8 * sc + 6, 6 * sc))
wall_SF2 = Wall("wall-short-r.png", (22 * sc - 6, 10 * sc))
wall_SB2 = Wall("wall-short-r.png", (22 * sc - 6, 6 * sc))
wall_list.add(wall_L1, wall_L2, wall_L3, wall_L4, wall_L5, wall_S1, wall_S2, wall_SS1, wall_SS2, wall_SF1, wall_SF2,
              wall_SB1, wall_SB2)

# Create the player
player = Player(plr_x, plr_y)
hitbox = Hitbox()
hitbox.walls = wall_list

dog = Dog()
# enemy = Enemy()
enemies = pygame.sprite.Group()
turrets = pygame.sprite.Group()

sprites = [wall_list, dog]
for sc in sprites:
    all_sprites.add(sc)

clock = pygame.time.Clock()

buildone = False
startup = True
done = False

while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                hitbox.changespeed(-plr_speed, 0)
            elif event.key == pygame.K_d:
                hitbox.changespeed(plr_speed, 0)
            elif event.key == pygame.K_w:
                hitbox.changespeed(0, -plr_speed)
            elif event.key == pygame.K_s:
                hitbox.changespeed(0, plr_speed)
            elif event.key == pygame.K_SPACE:
                for t in turrets:
                    if player.rect.colliderect(t.rect):
                        t.kill()
                        turretcount += 1
                        buildone = True

                if turretcount > 0 and not buildone:
                    new_turret = Turret((int(player.rect.x) + 5, int(player.rect.y) + 10))
                    turrets.add(new_turret)
                    all_sprites.add(new_turret)
                    turretcount -= 1
                buildone = False

            elif event.key == pygame.K_ESCAPE:
                done = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                hitbox.changespeed(plr_speed, 0)
            elif event.key == pygame.K_d:
                hitbox.changespeed(-plr_speed, 0)
            elif event.key == pygame.K_w:
                hitbox.changespeed(0, plr_speed)
            elif event.key == pygame.K_s:
                hitbox.changespeed(0, -plr_speed)

    screen.fill(BACKDROP)

    # every frame has a 1/100 chance of spawning an enemy
    if random.randrange(1, 101) == 1:
        new_enemy = Enemy()
        enemies.add(new_enemy)
        all_sprites.add(new_enemy)

    enemies.update()
    hitbox.update()

    # all_sprites.draw(screen)
    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect)

    screen.blit(player.image, player.rect)

    pygame.display.flip()
    clock.tick(60)
    if startup:
        startup = False

pygame.quit()
