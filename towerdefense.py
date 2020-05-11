# import necessary libraries
import pygame
from pygame.locals import (FULLSCREEN)
import math
import random
import time

# screen dimensions
# i tried to make it fully scalable but i didnt have enought time
# anything smaller than 1536x864 will have a broken background
screen_width = 1536
screen_height = 864

# change to True for fullscreeen or False for window
fullscreen = False

# this will help place sprites in a smaller grid rather than calculating each pixel position
# scale works best for 16:9 resolutions (grid is 32:18)
sc = round(screen_width / 32)

# adjust for gameplay balance
plr_speed = round(sc / 8)
som_speed = (sc / 96)
bullet_speed = 16
enemy_cooldown = 900
build_cooldown = 900
turret_cooldown = 0.5
turret_range = round(sc * 4)
turret_limit = 6
dogHP = 24
enemyHP = 8

# misc. constants
sprite_scale = round(sc / 16)
framerate = 30
plr_x = 10
plr_y = 500
dog_x = 15 * sc + round(sc / 2)
dog_y = 9 * sc

# create clock object
clock = pygame.time.Clock()


# this scales all my pixelart sprites to a bigger size
def scalesprite(sprite):
    # replace new_width and new_height with the desired width and height
    sprite.image = pygame.transform.scale(sprite.image,
                                          (sprite.image.get_size()[0] * sprite_scale,
                                           sprite.image.get_size()[1] * sprite_scale))


# remove redundancies in sprite objects
class Sprt(pygame.sprite.Sprite):
    def __init__(self, sprite, x, y):
        super(Sprt, self).__init__()

        # load sprite, scale it and size object rect to image size
        self.image = pygame.image.load(sprite).convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()

        # go to given coordinates
        self.rect.x = x
        self.rect.y = y


# this class is for all my hay walls
class Wall(Sprt):
    def __init__(self, sprite, x, y):
        super().__init__(sprite, x, y)
        self.rect.inflate_ip(0, -sc)


# this class is for the dog you need to protect
class Dog(Sprt):
    def __init__(self, sprite, x, y):
        super().__init__(sprite, x, y)
        self.health = dogHP
        self.dead = False

    # runs when dog takes damage
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


# this class is for the player character
class Player(Sprt):
    # runs when player is created
    def __init__(self, sprite, x, y):
        super().__init__(sprite, x, y)

        # set theoretical x and y values that can be float
        self.x = x
        self.y = y
        # set speed vector
        self.change_x = 0
        self.change_y = 0

        # declare other stuff
        self.walls = None
        self.building = False
        self.turretcount = turret_limit

    # runs when player presses [space]
    def startbuild(self):
        removed = False
        # if player collides with turrets, remove those turrets
        # i plan to make a progress bar for this as well to avoid accidental removal
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
            self.buildbar = Sprt('build1.png', self.rect.x, self.rect.y - (5 * sprite_scale))
            theApp.ui_sprites.append(self.buildbar)
            # track start time
            self.start_time = pygame.time.get_ticks()

    # runs when [space] is released
    def endbuild(self):
        # if you were building, kill progress bar and stop building
        if self.building:
            self.buildbar.kill()
            theApp.ui_sprites.remove(self.buildbar)
            self.building = False

    # runs when [w], [a], [s] or [d] are pressed or released
    def changespeed(self, x, y):
        # prepare to move by given vector
        self.change_x += x
        self.change_y += y

    def move(self):
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

    # run if building
    def build(self):
        # update bar sprite based on fraction of time done by number of sprites
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
            new_turret = Turret('turret1.png', (int(self.rect.x) + 5), (int(self.rect.y) + 10))
            theApp.turrets.add(new_turret)
            theApp.all_sprites.append(new_turret)
            self.turretcount -= 1
            self.endbuild()

    # runs every loop
    def update(self):
        # move if you are not building
        if self.building:
            self.build()
        else:
            self.move()


# this class is for turret towers (they shoot at enemies)
class Turret(Sprt):
    def __init__(self, sprite, x, y):
        super().__init__(sprite, x, y)

        # declare local variables
        self.range = turret_range
        self.buffer = enemy_cooldown
        self.oldtime = pygame.time.get_ticks()
        self.blind = False

    # runs every loop
    # made this with multiple if statements with calculations between for efficiency
    def update(self):
        # continue if enough time has passed
        now = pygame.time.get_ticks()
        if now - self.oldtime >= self.buffer:

            # runs for each enemy
            # could change to order of distance later, though it is more expensive
            for t in theApp.enemies:

                # calcutate distance to enemy w. pythagoras
                dist = math.sqrt((t.rect.x - self.rect.x) ** 2 + (t.rect.y - self.rect.y) ** 2)

                # continue if the enemy is close enough
                if dist < self.range:
                    # draw line between turret and enemy
                    line = pygame.draw.line(theApp._display_surf, (0, 0, 0), (self.rect.x, self.rect.y + round(sc / 2)),
                                            (t.rect.x, t.rect.y + sc))

                    # shoot if a wall isn't in the way
                    for w in theApp.wall_list:
                        if line.colliderect(w.rect):
                            self.blind = True
                            break
                    if not self.blind:
                        self.oldtime = time.time()
                        new_bullet = Bullet('bullet.png', self.rect.x, (self.rect.y + 10), t)
                        theApp.bullets.add(new_bullet)
                        theApp.all_sprites.append(new_bullet)
                        self.oldtime = now
                    self.blind = False


# this class is for bullets shot by turrets
class Bullet(Sprt):
    def __init__(self, sprite, x, y, target):
        super().__init__(sprite, x, y)

        # declare local variables
        self.speed = bullet_speed
        self.target = target
        self.goal = (target.rect.x + round(sc / 4), target.rect.y + round(sc / 4))

        # setup for bullet movement
        self.x = x
        self.y = y
        v = self.speed
        x = self.goal[0] - self.x
        y = self.goal[1] - self.y
        s = math.sqrt((x ** 2) + (y ** 2))
        self.dx = float(v * (x / s))
        self.dy = float(v * (y / s))

    # runs every loop
    def update(self):
        # move approximately to where the bullet should be
        self.x += self.dx
        self.y += self.dy
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

        # if it hits an enemy, damage the enemy and kill self
        for enemy in theApp.enemies:
            if enemy in theApp.all_sprites and self.rect.colliderect(enemy.rect):
                enemy.damage(1)
                # for some reason this come sometimes runs without the bullet already being on all_sprites
                if self in theApp.all_sprites:
                    theApp.all_sprites.remove(self)
                self.kill()

        # if it hits a wall,and kill self
        for wall in theApp.wall_list:
            if self.rect.colliderect(wall.rect):
                if self in theApp.all_sprites:
                    theApp.all_sprites.remove(self)
                self.kill()


# class for the enemies
class Enemy(Sprt):
    # runs when enemy is created
    def __init__(self, sprite, x, y):
        super().__init__(sprite, x, y)

        # declare local variables
        self.speed = som_speed
        self.health = enemyHP
        self.buffer = enemy_cooldown

        # generate path from spawn point and decision tree
        self.type = random.randrange(1, 6)
        self.getpath()

        # position is stored in float values seperate from actual rect position
        self.x = self.agenda[0][0]
        self.y = self.agenda[0][1]

        # declare variables for later use
        self.dx = 0
        self.dy = 0
        self.steps = 0
        self.stage = 0
        self.attacking = False

    # planned to change this so attackers don't all stand on top of each other
    def finpos(self):
        return [16, 8]

    # runs in init when generating path
    # moved to function for convenience
    def getpath(self):
        # looong function of if/else statement decision trees to generate path of enemy
        # currently don't know a better way but it only runs once per enemy spawn
        if self.type == 1:
            self.agenda = [[-1, -2], [2, 1]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[15, 1], [15, 4]])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[20.5, 4], [20.5, 8], self.finpos()])
                else:
                    self.agenda.extend([[10.5, 4], [10.5, 8], self.finpos()])
            else:
                self.agenda.append([5, 4])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[10.5, 4], [10.5, 8], self.finpos()])
                else:
                    self.agenda.extend([[5, 12], [14, 12], self.finpos()])

        elif self.type == 2:
            self.agenda = [[15.5, -2], [15.5, 3]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[10.5, 5], [10.5, 8], self.finpos()])
            else:
                self.agenda.extend([[20.5, 5], [20.5, 8], self.finpos()])

        elif self.type == 3:
            self.agenda = [[32, -2], [29, 1]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[16, 1], [16, 4]])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[20.5, 4], [20.5, 8], self.finpos()])
                else:
                    self.agenda.extend([[10.5, 4], [10.5, 8], self.finpos()])
            else:
                self.agenda.append([26, 4])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[20.5, 4], [20.5, 8], self.finpos()])
                else:
                    self.agenda.extend([[26, 12], [17, 12], self.finpos()])

        elif self.type == 4:
            self.agenda = [[-1, 18], [1, 16]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[15, 16], self.finpos()])
            else:
                self.agenda.append([5.5, 12])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[12, 12], self.finpos()])
                else:
                    self.agenda.extend([[6, 4], [10.5, 4], [10.5, 8], self.finpos()])

        elif self.type == 5:
            self.agenda = [[32, 18], [30, 16]]
            if random.getrandbits(1) == 1:
                self.agenda.extend([[16, 16], self.finpos()])
            else:
                self.agenda.append([25.5, 12])
                if random.getrandbits(1) == 1:
                    self.agenda.extend([[19, 12], self.finpos()])
                else:
                    self.agenda.extend([[25, 4], [20.5, 4], [20.5, 8], self.finpos()])

        # scale coordinates to bigger grid
        for i in self.agenda:
            i[0] = i[0] * sc
            i[1] = i[1] * sc

    # runs when preparing path to next goal
    def moveto(self, point):
        # calculates number of steps needed, and vector for each step given speed w. pythagoras
        v = self.speed
        x = point[0] - self.rect.x
        y = point[1] - self.rect.y
        s = math.sqrt((x ** 2) + (y ** 2))
        self.dx = float(v * (x / s))
        self.dy = float(v * (y / s))
        self.steps = round((s / v))

    # runs every loop
    def update(self):

        if self.attacking:
            # if attacking, attack
            self.attack(self.target)
        # move if not attacking
        else:
            # change theoretical placement and real placement
            self.x += self.dx
            self.y += self.dy
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
            # count step
            self.steps -= 1

            # if at goal, go to next goal or start attacking dog
            if self.steps < 1:
                self.stage += 1
                if self.stage > len(self.agenda) - 1:
                    self.attacking = True
                    self.target = theApp.dog
                    self.oldtime = pygame.time.get_ticks()
                else:
                    self.moveto(self.agenda[self.stage])

    # runs every loop while attacking
    # could also be used if i built in enemies attacking turrets etc.
    def attack(self, target):
        # damage target every [buffer] ticks
        now = pygame.time.get_ticks()
        if now - self.oldtime >= self.buffer:
            self.oldtime = now
            target.damage(1)

    # runs when enemy takes damage
    def damage(self, dmg):
        # take damage
        self.health -= dmg

        # change sprite depending on health
        if self.health <= (enemyHP / 3) * 2:

            if self.health > enemyHP / 3:
                self.image = pygame.image.load('sombi2.png').convert_alpha()
                scalesprite(self)

            elif self.health > 0:
                self.image = pygame.image.load('sombi3.png').convert_alpha()
                scalesprite(self)

            # die at sub 0 health
            else:
                theApp.gore = Sprt('blood.png', self.rect.x, self.rect.y)
                theApp.floor_sprites.append(theApp.gore)
                theApp.all_sprites.remove(self)
                self.kill()


# class for my entire game
class App:
    def __init__(self):
        # declare local variables, lists, sprite groups etc.
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

        # launch pygame
        pygame.init()

        # declare game surface
        if fullscreen:
            self._display_surf = pygame.display.set_mode(self.size, FULLSCREEN | pygame.DOUBLEBUF)
        else:
            self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        # describes wall sprites and placement
        wallsprites = ['WLX.png', 'WLX.png', 'WLX.png', 'WLX.png', 'WLX.png', 'WLY.png', 'WLY.png', 'WSY.png',
                       'WSY.png', 'WSX.png', 'WSX.png', 'WSX.png', 'WSX.png']
        wallcoords = [(6, 2), (18, 2), (6, 14), (18, 14), (12, 6), (3, 6), (28, 6), (7, 6), (24, 6), (8, 10), (8, 6),
                      (22, 10), (22, 6)]
        i = 0
        for s in wallsprites:
            c = wallcoords[i]
            if i == 11 or i == 9:
                # short walls get moved slightly down
                # this doesn't scale well but is works for 3 pixels in the res i'm using
                self.wall = Wall(s, (c[0] * sc), ((c[1] * sc) + sprite_scale))
            else:
                # create walls for sprite and corresponding scaled corrdinate
                self.wall = Wall(s, (c[0] * sc), (c[1] * sc))
            # add to list of wall, used for collisions
            self.wall_list.append(self.wall)
            i += 1

        # create player and dog objects
        self.player = Player("dad1.png", plr_x, plr_y)
        self.dog = Dog("dog1.png", dog_x, dog_y)

        # add player, dog and walls to render list
        self.all_sprites.extend(self.wall_list)
        self.all_sprites.extend([self.dog, self.player])

        # create a coordinate list of corners in scaled grid for background
        self.grid = []
        for y in range(0, screen_height, sc):
            for x in range(0, screen_width, sc):
                self.grid.append([x, y])

        # i know this is ugly but technically grass is rendered in the app and not as a seperate object
        self.image = pygame.image.load('grasstile.png').convert()
        scalesprite(self)

    # runs when an input happens
    def on_event(self, event):
        # quit on [esc]
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.KEYDOWN:
            # move with [w], [a], [s], [d]
            if event.key == pygame.K_a:
                self.player.changespeed(-plr_speed, 0)
            elif event.key == pygame.K_d:
                self.player.changespeed(plr_speed, 0)
            elif event.key == pygame.K_w:
                self.player.changespeed(0, -plr_speed)
            elif event.key == pygame.K_s:
                self.player.changespeed(0, plr_speed)

            # build or remove turrets with [space]
            elif event.key == pygame.K_SPACE:
                self.player.startbuild()

            # quit on [esc]
            elif event.key == pygame.K_ESCAPE:
                self._running = False

        # stop moving in that direction when [w], [a], [s], [d] go up
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

    # runs every loop
    def on_loop(self):
        # 1 % chance of spawning an enemy
        # i want to make the chance to up with time later
        if random.randrange(1, 101) == 1:
            new_enemy = Enemy("sombi1.png", -2, -2)
            self.enemies.add(new_enemy)
            self.all_sprites.append(new_enemy)

        # update dynamic objects
        self.bullets.update()
        self.enemies.update()
        self.turrets.update()
        self.player.update()

        # game over if dog dies
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

        # update screen
        pygame.display.flip()

        # wait until next frame
        clock.tick(60)

    # runs when quitting/losing game
    def on_cleanup(self):
        # ends pygame
        pygame.quit()

    # main loop, controls everything
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
