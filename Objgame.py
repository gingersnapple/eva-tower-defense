import pygame
from pygame.locals import (FULLSCREEN)
import math
import random
import time

# screen dimensions
screen_width = 1536
screen_height = 864
fullscreen = False

# this will help place sprites in a smaller grid rather than calculating each pixel position
# scale works best for 16:9 resolutions (grid is 32:18)
# returns 48 for current resolution
sc = round(screen_width / 32)

# adjust for gameplay balance
plr_speed = 6
som_speed = 0.5
bullet_speed = 16
enemy_cooldown = 900
build_cooldown = 900
turret_cooldown = 0.5
turret_range = round((300 / 1534) * screen_width)
dogHP = 24
enemyHP = 6

# misc. constants
# returns 3 for current resolution
sprite_scale = round(sc / 16)
framerate = 30
plr_x = 10
plr_y = 500
dog_x = 15 * sc + round(sc / 2)
dog_y = 9 * sc

# create clock object
clock = pygame.time.Clock()


def scalesprite(sprite):
    # replace new_width and new_height with the desired width and height
    sprite.image = pygame.transform.scale(sprite.image,
                                          (sprite.image.get_size()[0] * sprite_scale,
                                           sprite.image.get_size()[1] * sprite_scale))


class Wall(pygame.sprite.Sprite):
    def __init__(self, sprite, pos):
        super(Wall, self).__init__()

        # load sprite, scale it and size object rect to image size
        self.image = pygame.image.load(sprite).convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()

        # move to given position
        self.rect.x = pos[0]
        self.rect.y = pos[1]

        # change hitbox for 3d effect
        self.rect.inflate_ip(0, -sc)


class Dog(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Dog, self).__init__()

        # load sprite, scale it and size object rect to image size
        self.image = pygame.image.load('dog1.png').convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()

        # declare local variables
        self.health = dogHP
        self.dead = False

        # go to given coordinates
        self.rect.x = x
        self.rect.y = y

    def damage(self, dmg):
        # take damage
        self.health -= dmg

        # change sprite depending on remaining health compared to full health
        if self.health <= (dogHP / 3) * 2:
            if self.health > dogHP / 3:
                self.image = pygame.image.load('dog2.png').convert_alpha()
                scalesprite(self)

            elif self.health > 0:
                self.image = pygame.image.load('dog3.png').convert_alpha()
                scalesprite(self)

            # if health lower than 0, die
            else:
                self.image = pygame.image.load('dog4.png').convert_alpha()
                scalesprite(self)
                self.dead = True


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Player, self).__init__()

        # load sprite, scale it and size object rect to image size
        self.image = pygame.image.load('dad1.png').convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()

        # go to given coordinates
        self.rect.y = y
        self.rect.x = x
        # set theoretical x and y values that can be float
        self.x = x
        self.y = y
        # set speed vector
        self.change_x = 0
        self.change_y = 0

        # declare other stuff
        self.walls = None
        self.building = False
        self.turretcount = 7

    def startbuild(self):
        # function for when player presses [space]
        removed = False
        # if player collides with turrets, remove those turrets
        # plan to make a progress for this as well to avoid accidental removal
        for t in theApp.turrets:
            if t in theApp.all_sprites and self.rect.colliderect(t.rect):
                theApp.all_sprites.remove(t)
                t.kill()
                self.turretcount += 1
                removed = True

        # if you didn't remove turrets and haven't run out, start building one instead
        if self.turretcount > 0 and not removed:
            self.building = True
            # make progress bar on top of player
            self.buildbar = Buildbar('build1.png', self.rect.x, self.rect.y - (5 * sprite_scale))
            theApp.ui_sprites.append(self.buildbar)
            # track start time
            self.start_time = pygame.time.get_ticks()

    def endbuild(self):
        # when [space] goes up
        # if you were building, kill progress bar and stop building
        if self.building:
            self.buildbar.kill()
            theApp.ui_sprites.remove(self.buildbar)
            self.building = False

    def changespeed(self, x, y):
        # prepare to move by given vector
        self.change_x += x
        self.change_y += y

    def update(self):
        # only move if you are not building
        if not self.building:

            # move left/right
            self.rect.x += self.change_x

            for w in theApp.wall_list:
                if self.rect.colliderect(w.rect):
                    # if you are moving right and collide with a wall, instead go to wall's left side
                    if self.change_x > 0:
                        self.rect.right = w.rect.left
                    else:
                        # if you are moving left and collide with a wall, do the opposite
                        self.rect.left = w.rect.right

            # move up/down
            self.rect.y += self.change_y

            for w in theApp.wall_list:
                if self.rect.colliderect(w.rect):
                    # if you are moving down and collide with a wall, instead go to wall's top side
                    if self.change_y > 0:
                        self.rect.bottom = w.rect.top
                    else:
                        # if you are moving up and collide with a wall, do the opposite
                        self.rect.top = w.rect.bottom

            # dont go off screen
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > screen_width:
                self.rect.right = screen_width
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height

        else:
            # run if building

            # update sprite based on fraction of time done by number of sprites
            now = pygame.time.get_ticks()
            buildsprites = ['build7.png', 'build6.png', 'build5.png', 'build4.png', 'build3.png', 'build2.png']
            i = len(buildsprites)
            sl = len(buildsprites) + 1

            for s in buildsprites:
                if now - self.start_time >= ((build_cooldown / sl) * i):
                    self.buildbar.image = pygame.image.load(s).convert_alpha()
                    scalesprite(self.buildbar)
                    break
                i -= 1

            # if the time is up, spawn the turret next to you and stop building
            if now - self.start_time >= build_cooldown:
                new_turret = Turret((int(self.rect.x) + 5, int(self.rect.y) + 10))
                theApp.turrets.add(new_turret)
                theApp.all_sprites.append(new_turret)
                self.turretcount -= 1
                self.endbuild()


class Buildbar(pygame.sprite.Sprite):
    # object for build progress bar
    def __init__(self, image, x, y):
        super(Buildbar, self).__init__()

        # load sprite, scale it and size object rect to image size
        self.image = pygame.image.load(image).convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()

        # go to given coordinates
        self.rect.x = x
        self.rect.y = y


class Turret(pygame.sprite.Sprite):
    # object for turrets
    def __init__(self, pos):
        super(Turret, self).__init__()

        # load sprite, scale it and size object rect to image size
        self.image = pygame.image.load('turret1.png').convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()

        # go to given coordinates
        self.rect.x = (pos[0])
        self.rect.y = (pos[1])

        # declare local variables
        self.range = turret_range
        self.buffer = enemy_cooldown
        self.oldtime = pygame.time.get_ticks()
        self.blind = False


    def update(self):
        for t in theApp.enemies:
            linelen = math.sqrt((t.rect.x - self.rect.x) ** 2 + (t.rect.y - self.rect.y) ** 2)
            now = pygame.time.get_ticks()
            if now - self.oldtime >= self.buffer and linelen < self.range:
                line = pygame.draw.line(theApp._display_surf, (0, 0, 0), (self.rect.x, self.rect.y + 10),
                                        (t.rect.x, t.rect.y + 50))
                for w in theApp.wall_list:
                    if line.colliderect(w.rect):
                        self.blind = True
                        break
                if not self.blind:
                    self.oldtime = time.time()
                    new_bullet = Bullet((self.rect.x, self.rect.y + 10), t)
                    theApp.bullets.add(new_bullet)
                    theApp.all_sprites.append(new_bullet)
                    self.oldtime = now
                self.blind = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target):
        super(Bullet, self).__init__()
        self.image = pygame.image.load('bullet.png').convert_alpha()
        self.speed = bullet_speed
        self.target = target

        scalesprite(self)
        self.rect = self.image.get_rect()
        self.x = pos[0]
        self.y = pos[1]
        self.goal = (target.rect.x + 10, target.rect.y + 10)

        # setup til skudbane
        v = self.speed
        x = self.goal[0] - self.x
        y = self.goal[1] - self.y
        s = math.sqrt((x ** 2) + (y ** 2))
        self.dx = float(v * (x / s))
        self.dy = float(v * (y / s))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)
        for enemy in theApp.enemies:
            if enemy in theApp.all_sprites and self.rect.colliderect(enemy.rect):
                enemy.damage(1)
                if self in theApp.all_sprites:
                    theApp.all_sprites.remove(self)
                self.kill()

        for wall in theApp.wall_list:
            if self.rect.colliderect(wall.rect):
                if self in theApp.all_sprites:
                    theApp.all_sprites.remove(self)
                self.kill()


def finpos():
    return [16, 8]


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.speed = som_speed
        self.health = enemyHP
        self.buffer = enemy_cooldown
        self.oldtime = pygame.time.get_ticks()

        self.image = pygame.image.load('sombi1.png').convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()

        # generate path from spawn point and decision tree
        self.type = random.randrange(1, 6)
        self.getpath()

        # position bliver lagret i float seperat fra rect så fjenderne kan bevæge sig i små trin
        self.x = self.agenda[0][0]
        self.y = self.agenda[0][1]
        self.dx = 0
        self.dy = 0
        self.steps = 0
        self.goal = (0, 0)
        self.stage = 0
        self.attacking = False
        self.startup = True

    def getpath(self):
        if self.type == 1:
            self.agenda = [[-1, -2], [2, 1]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[15, 1], [15, 4]])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[20.5, 4], [20.5, 8], finpos()])
                else:
                    self.agenda.extend([[10.5, 4], [10.5, 8], finpos()])
            else:
                self.agenda.append([5, 4])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[10.5, 4], [10.5, 8], finpos()])
                else:
                    self.agenda.extend([[5, 12], [14, 12], finpos()])

        elif self.type == 2:
            self.agenda = [[15.5, -2], [15.5, 3]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[10.5, 5], [10.5, 8], finpos()])
            else:
                self.agenda.extend([[20.5, 5], [20.5, 8], finpos()])

        elif self.type == 3:
            self.agenda = [[32, -2], [29, 1]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[16, 1], [16, 4]])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[20.5, 4], [20.5, 8], finpos()])
                else:
                    self.agenda.extend([[10.5, 4], [10.5, 8], finpos()])
            else:
                self.agenda.append([26, 4])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[20.5, 4], [20.5, 8], finpos()])
                else:
                    self.agenda.extend([[26, 12], [17, 12], finpos()])

        elif self.type == 4:
            self.agenda = [[-1, 18], [1, 16]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[15, 16], finpos()])
            else:
                self.agenda.append([5.5, 12])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[12, 12], finpos()])
                else:
                    self.agenda.extend([[6, 4], [10.5, 4], [10.5, 8], finpos()])

        elif self.type == 5:
            self.agenda = [[32, 18], [30, 16]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[16, 16], finpos()])
            else:
                self.agenda.append([25.5, 12])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[19, 12], finpos()])
                else:
                    self.agenda.extend([[25, 4], [20.5, 4], [20.5, 8], finpos()])

        # scale to bigger grid
        for i in self.agenda:
            i[0] = i[0] * sc
            i[1] = i[1] * sc

    def moveto(self, point):
        self.goal = point
        v = self.speed
        x = point[0] - self.rect.x
        y = point[1] - self.rect.y
        s = math.sqrt((x ** 2) + (y ** 2))
        self.dx = float(v * (x / s))
        self.dy = float(v * (y / s))
        self.steps = round((s / v))

    def update(self):
        if not self.attacking:
            self.x += self.dx
            self.y += self.dy
            self.rect.x = round(self.x)
            self.rect.y = round(self.y)
            self.steps -= 1
            if self.steps < 1:
                self.stage += 1
                if self.stage + 1 > len(self.agenda):
                    # self.kill()
                    self.attacking = True
                    self.target = theApp.dog
                else:
                    self.moveto(self.agenda[self.stage])
        else:
            self.attack(self.target)

    def attack(self, target):
        now = pygame.time.get_ticks()
        if now - self.oldtime >= self.buffer:
            self.oldtime = now
            target.damage(1)

    def damage(self, dmg):
        self.health -= dmg

        if self.health <= (enemyHP / 3) * 2:

            if self.health > enemyHP / 3:
                self.image = pygame.image.load('sombi2.png').convert_alpha()
                scalesprite(self)

            elif self.health > 0:
                self.image = pygame.image.load('sombi3.png').convert_alpha()
                scalesprite(self)

            else:
                theApp.gore = Gore(self.rect.x, self.rect.y)
                theApp.all_sprites.remove(self)
                self.kill()


class Gore(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Gore, self).__init__()
        self.image = pygame.image.load('blood.png').convert_alpha()
        self.rect = self.image.get_rect()

        scalesprite(self)
        self.rect.x = (x)
        self.rect.y = (y)
        theApp.floor_sprites.append(self)


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = screen_width, screen_height

        self.all_sprites = []
        self.ui_sprites = []
        self.floor_sprites = []
        self.wall_list = []
        self.enemies = pygame.sprite.Group()
        self.turrets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        pygame.init()
        if fullscreen:
            self._display_surf = pygame.display.set_mode(self.size, FULLSCREEN | pygame.DOUBLEBUF)
        else:
            self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        wallsprites = ['WLX.png', 'WLX.png', 'WLX.png', 'WLX.png', 'WLX.png', 'WLY.png', 'WLY.png', 'WSY.png',
                       'WSY.png', 'WSX.png', 'WSX.png', 'WSX.png', 'WSX.png']
        wallcoords = [(6, 2), (18, 2), (6, 14), (18, 14), (12, 6), (3, 6), (28, 8), (7, 6), (24, 6), (8, 10), (8, 6),
                      (22, 10), (22, 6)]
        i = 0
        for s in wallsprites:
            c = wallcoords[i]
            if i == 11 or i == 9:
                # short walls get moved slightly down
                # this probably doesn't scale well but is works for 3 pixels in the res i'm using
                self.wall = Wall(s, ((c[0] * sc), (c[1] * sc) + sprite_scale))
            else:
                # create walls for sprite and corresponding scaled corrdinate
                self.wall = Wall(s, (c[0] * sc, c[1] * sc))

            self.wall_list.append(self.wall)
            i += 1

        self.player = Player(plr_x, plr_y)
        self.dog = Dog(dog_x, dog_y)

        self.all_sprites.extend(self.wall_list)
        self.all_sprites.extend([self.dog, self.player])

        # grid draw a grass tile in a scaled grid
        self.grid = []
        self.image = pygame.image.load('grasstile.png').convert()
        scalesprite(self)

        for y in range(0, screen_height, sc):
            for x in range(0, screen_width, sc):
                self.grid.append([x, y])

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.player.changespeed(-plr_speed, 0)
            elif event.key == pygame.K_d:
                self.player.changespeed(plr_speed, 0)
            elif event.key == pygame.K_w:
                self.player.changespeed(0, -plr_speed)
            elif event.key == pygame.K_s:
                self.player.changespeed(0, plr_speed)
            elif event.key == pygame.K_SPACE:
                self.player.startbuild()
            elif event.key == pygame.K_ESCAPE:
                self._running = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.player.changespeed(plr_speed, 0)
            elif event.key == pygame.K_d:
                self.player.changespeed(-plr_speed, 0)
            elif event.key == pygame.K_w:
                self.player.changespeed(0, plr_speed)
            elif event.key == pygame.K_s:
                self.player.changespeed(0, -plr_speed)
            elif event.key == pygame.K_SPACE:
                self.player.endbuild()

    def on_loop(self):

        if random.randrange(1, 101) == 1:
            new_enemy = Enemy()
            self.enemies.add(new_enemy)
            self.all_sprites.append(new_enemy)

        self.bullets.update()
        self.enemies.update()
        self.turrets.update()
        self.player.update()

        if self.dog.dead:
            self.on_render()
            time.sleep(3)
            self._running = False

    def on_render(self):

        # blit backdrop tiles
        for p in self.grid:
            # blit each sprite onto display
            self._display_surf.blit(self.image, p)

        # floor is blitted on top of backdrop but below other sprites
        for sprite in self.floor_sprites:
            self._display_surf.blit(sprite.image, sprite.rect)

        # display lower sprites on top of higher sprites based on bottom left corner
        self.all_sprites.sort(key=lambda x: (x.rect.y + x.rect.height))
        for sprite in self.all_sprites:
            self._display_surf.blit(sprite.image, sprite.rect)

        # user interface is blitted on top of anything else
        for sprite in self.ui_sprites:
            self._display_surf.blit(sprite.image, sprite.rect)

        pygame.display.flip()
        clock.tick(60)

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


# run my program
theApp = App()
theApp.on_execute()
