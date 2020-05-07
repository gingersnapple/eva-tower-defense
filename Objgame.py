# coding=utf-8
import pygame
from pygame.locals import (FULLSCREEN)
import math
import random
import time

BACKDROP = (168, 238, 121)
creature_scale = 3
wall_scale = 6
framerate = 30
plr_speed = 6
som_speed = 0.5
plr_x = 10
plr_y = 500

# Screen dimensions
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 864
fullscreen = False
clock = pygame.time.Clock()


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
        self.rect.x = theApp.hitbox.rect.x
        self.rect.y = (theApp.hitbox.rect.y - 48)


class Hitbox(Player):
    def __init__(self):
        super(Hitbox, self).__init__(10, 500)
        self.surf = pygame.Surface((42, 15))
        self.rect = self.surf.get_rect()

        self.rect.x = theApp.player.x
        self.rect.y = (theApp.player.y + 48)

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

        theApp.player.update()


class Turret(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Turret, self).__init__()
        self.image = pygame.image.load('turret1.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.range = 500
        self.buffer = 3
        self.oldtime = time.time()
        self.timer = 0

        # replace new_width and new_height with the desired width and height
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_size()[0] * creature_scale,
                                             self.image.get_size()[1] * creature_scale))
        self.rect = self.image.get_rect()
        self.rect.x = (pos[0])
        self.rect.y = (pos[1])

    def update(self):
        for t in theApp.enemies:
            tx = int(t.rect.x)
            ty = int(t.rect.y)
            x = tx - self.rect.x
            y = ty - self.rect.y
            s = math.sqrt((x ** 2) + (y ** 2))
            self.timer = time.time() - self.oldtime
            if s < self.range and self.timer > self.buffer:
                new_bullet = Bullet(self.rect, t)
                theApp.bullets.add(new_bullet)
                theApp.all_sprites.append(new_bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target):
        super(Bullet, self).__init__()
        self.image = pygame.image.load('bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = 10
        self.target = target

        # replace new_width and new_height with the desired width and height
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_size()[0] * creature_scale,
                                             self.image.get_size()[1] * creature_scale))
        self.rect = self.image.get_rect()
        self.rect.x = (int(pos[0]))
        self.rect.y = (int(pos[1]))

        self.goal = (target.rect[0]+10, target.rect[1]+10)
        px = int(self.goal[0])
        py = int(self.goal[1])
        x = px - self.rect.x
        y = py - self.rect.y
        v = self.speed
        s = math.sqrt((x ** 2) + (y ** 2))
        self.dx = v * (x / s)
        self.dy = v * (y / s)
        self.steps = round(s / v)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.steps -= 1
        for enemy in theApp.enemies:
            if enemy in theApp.all_sprites and self.rect.colliderect(enemy.rect):
                enemy.damage(1)
                self.kill()
                break

        if self.steps < 1:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()

        self.image = pygame.image.load('sombi1.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = som_speed
        self. health = 3
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

        self.rect.x = self.agenda[0][0]
        self.rect.y = self.agenda[0][1]
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
        x = px - self.rect.x
        y = py - self.rect.y
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
            self.rect.x += self.dx
            self.rect.y += self.dy
            self.steps -= 1
            if self.steps < 1:
                self.moving = False
                if self.stage + 1 < len(self.agenda):
                    self.stage += 1
                    self.moveto(self.agenda[self.stage])
                else:
                    self.kill()

    def damage(self, dmg):
        self.health -= dmg
        if self.health > 1:
            self.kill()

class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = SCREEN_WIDTH, SCREEN_HEIGHT

        self.all_sprites = []
        self.enemies = pygame.sprite.Group()
        self.turrets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.turretcount = 7
        self.buildone = False

    def on_init(self):
        pygame.init()
        if fullscreen:
            self._display_surf = pygame.display.set_mode(self.size, FULLSCREEN | pygame.DOUBLEBUF)
        else:
            self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        # Beskriver hvor vaeggene skal hen. er foreloebigt grimt skrevet fordi
        # enkelte vaegge ogsaa skal et par ekstra pixels i en retning
        sc = 48
        self.wall_L1 = Wall("wall-long.png", (6 * sc, 2 * sc))
        self.wall_L2 = Wall("wall-long.png", (18 * sc, 2 * sc))
        self.wall_L3 = Wall("wall-long.png", (6 * sc, 14 * sc))
        self.wall_L4 = Wall("wall-long.png", (18 * sc, 14 * sc))
        self.wall_L5 = Wall("wall-long.png", (12 * sc, 6 * sc))
        self.wall_S1 = Wall("wall-side.png", (3 * sc, 6 * sc))
        self.wall_S2 = Wall("wall-side.png", (28 * sc, 6 * sc))

        self.wall_SS1 = Wall("wall-short-side.png", (7 * sc, 6 * sc))

        self.wall_SS2 = Wall("wall-short-side.png", (24 * sc - 6, 6 * sc))

        self.wall_SF1 = Wall("wall-short-l.png", (8 * sc + 6, 10 * sc))
        self.wall_SB1 = Wall("wall-short-l.png", (8 * sc + 6, 6 * sc))

        self.wall_SF2 = Wall("wall-short-r.png", (22 * sc - 6, 10 * sc))
        self.wall_SB2 = Wall("wall-short-r.png", (22 * sc - 6, 6 * sc))
        self.wall_list = [self.wall_L1, self.wall_L2, self.wall_L3, self.wall_L4, self.wall_L5, self.wall_S1,
                          self.wall_S2, self.wall_SS1, self.wall_SS2, self.wall_SF1,
                          self.wall_SF2,
                          self.wall_SB1, self.wall_SB2]

        self.player = Player(plr_x, plr_y)
        self.hitbox = Hitbox()
        self.hitbox.walls = self.wall_list
        self.wallcount = len(self.wall_list)
        self.dog = Dog()

        self.all_sprites.extend(self.wall_list)
        self.all_sprites.extend([self.dog, self.player])


    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.hitbox.changespeed(-plr_speed, 0)
            elif event.key == pygame.K_d:
                self.hitbox.changespeed(plr_speed, 0)
            elif event.key == pygame.K_w:
                self.hitbox.changespeed(0, -plr_speed)
                self.player.kill()
            elif event.key == pygame.K_s:
                self.hitbox.changespeed(0, plr_speed)
            elif event.key == pygame.K_SPACE:
                for t in self.turrets:
                    if t in self.all_sprites and self.player.rect.colliderect(t.rect):
                        self.all_sprites.remove(t)
                        t.kill()
                        self.turretcount += 1
                        self.buildone = True

                if self.turretcount > 0 and not self.buildone:
                    new_turret = Turret((int(self.player.rect.x) + 5, int(self.player.rect.y) + 10))
                    self.turrets.add(new_turret)
                    self.all_sprites.append(new_turret)
                    self.turretcount -= 1
                self.buildone = False

            elif event.key == pygame.K_ESCAPE:
                self._running = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.hitbox.changespeed(plr_speed, 0)
            elif event.key == pygame.K_d:
                self.hitbox.changespeed(-plr_speed, 0)
            elif event.key == pygame.K_w:
                self.hitbox.changespeed(0, plr_speed)
            elif event.key == pygame.K_s:
                self.hitbox.changespeed(0, -plr_speed)

    def on_loop(self):
        if random.randrange(1, 101) == 1:
            new_enemy = Enemy()
            self.enemies.add(new_enemy)
            # indsæt fjender lige over vægge
            self.all_sprites.insert(self.wallcount, new_enemy)

        self.bullets.update()
        self.enemies.update()
        self.turrets.update()
        self.hitbox.update()

    def on_render(self):
        self._display_surf.fill((168, 238, 121))
        for sprite in self.all_sprites:
            # blit each sprite onto display.
            # (round(sprite.rect.x), round(sprite.rect.y)) fixes DeprecationWarning but breaks enemies and bullets
            self._display_surf.blit(sprite.image, sprite.rect)

        pygame.display.flip()
        clock.tick(60)

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
