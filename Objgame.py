import pygame
from pygame.locals import (FULLSCREEN)
import math
import random
import time

# misc. constants
BACKDROP = (168, 238, 121)
sprite_scale = 3
framerate = 30
plr_x = 10
plr_y = 500

# adjust for gameplay balance
plr_speed = 6
som_speed = 0.5
turret_cooldown = 0.5
enemy_cooldown = 900
bullet_speed = 16
turret_range = 300
dogHP = 24
enemyHP = 6

# screen dimensions
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 864
fullscreen = False

# create clock object
clock = pygame.time.Clock()

def scalesprite(sprite):
    # replace new_width and new_height with the desired width and height
    sprite.image = pygame.transform.scale(sprite.image,
                                        (sprite.image.get_size()[0] * sprite_scale,
                                         sprite.image.get_size()[1] * sprite_scale))

class Wall(pygame.sprite.Sprite):
    def __init__(self, sprite, pos):
        # Call the parent's constructor
        super(Wall, self).__init__()
        self.image = pygame.image.load(sprite).convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()

        self.rect.x = (pos[0])
        self.rect.y = (pos[1])
        self.rect.inflate_ip(0, -50)


class Dog(pygame.sprite.Sprite):
    def __init__(self):
        super(Dog, self).__init__()
        self.image = pygame.image.load('dog1.png').convert_alpha()
        self.health = dogHP
        self.dead = False

        scalesprite(self)
        self.rect = self.image.get_rect()
        self.rect.x = (15 * 48 + 21)
        self.rect.y = (9 * 48)

    def damage(self, dmg):
        self.health -= dmg

        if self.health <= (dogHP / 3) * 2:

            if self.health > dogHP / 3:
                self.image = pygame.image.load('dog2.png').convert_alpha()
                self.image = pygame.transform.scale(self.image,
                                                    (self.image.get_size()[0] * sprite_scale,
                                                     self.image.get_size()[1] * sprite_scale))

            elif self.health > 0:
                self.image = pygame.image.load('dog3.png').convert_alpha()
                self.image = pygame.transform.scale(self.image,
                                                    (self.image.get_size()[0] * sprite_scale,
                                                     self.image.get_size()[1] * sprite_scale))
            else:
                self.image = pygame.image.load('dog4.png').convert_alpha()
                self.image = pygame.transform.scale(self.image,
                                                    (self.image.get_size()[0] * sprite_scale,
                                                     self.image.get_size()[1] * sprite_scale))
                self.dead = True


class Player(pygame.sprite.Sprite):
    # Constructor function
    def __init__(self, x, y):
        # Call the parent's constructor
        super(Player, self).__init__()
        self.x = x
        self.y = y
        self.image = pygame.image.load("dad1.png").convert_alpha()
        scalesprite(self)
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x

        # Set speed vector
        self.change_x = 0
        self.change_y = 0
        self.walls = None

    def changespeed(self, x, y):
        self.change_x += x
        self.change_y += y

    def update(self):
        # Move left/right
        self.rect.x += self.change_x

        for w in theApp.wall_list:
            if self.rect.colliderect(w.rect):
                if self.change_x > 0:
                    self.rect.right = w.rect.left
                else:
                    # Otherwise if we are moving left, do the opposite.
                    self.rect.left = w.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        for w in theApp.wall_list:
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
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Turret(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Turret, self).__init__()
        self.image = pygame.image.load('turret1.png').convert_alpha()
        self.range = turret_range
        self.buffer = enemy_cooldown
        self.oldtime = pygame.time.get_ticks()
        self.blind = False

        scalesprite(self)
        self.rect = self.image.get_rect()
        self.rect.x = (pos[0])
        self.rect.y = (pos[1])

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
        self.rect = self.image.get_rect()
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

        # scale to 48 pixel grid
        for i in self.agenda:
            i[0] = i[0] * 48
            i[1] = i[1] * 48

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
        self.size = self.weight, self.height = SCREEN_WIDTH, SCREEN_HEIGHT

        self.all_sprites = []
        self.floor_sprites = []
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
        self.wall_L1 = Wall("hay-long.png", (6 * sc, 2 * sc))
        self.wall_L2 = Wall("hay-long.png", (18 * sc, 2 * sc))
        self.wall_L3 = Wall("hay-long.png", (6 * sc, 14 * sc))
        self.wall_L4 = Wall("hay-long.png", (18 * sc, 14 * sc))
        self.wall_L5 = Wall("hay-long.png", (12 * sc, 6 * sc))
        self.wall_S1 = Wall("hay-side.png", (3 * sc, 6 * sc))
        self.wall_S2 = Wall("hay-side.png", (28 * sc, 6 * sc))
        self.wall_SS1 = Wall("hay-short-side.png", (7 * sc, 6 * sc))
        self.wall_SS2 = Wall("hay-short-side.png", (24 * sc, 6 * sc))
        self.wall_SF1 = Wall("hay-short.png", (8 * sc, 10 * sc + 3))
        self.wall_SB1 = Wall("hay-short.png", (8 * sc, 6 * sc))
        self.wall_SF2 = Wall("hay-short.png", (22 * sc, 10 * sc + 3))
        self.wall_SB2 = Wall("hay-short.png", (22 * sc, 6 * sc))
        self.wall_list = [self.wall_L1, self.wall_L2, self.wall_L3, self.wall_L4, self.wall_L5, self.wall_S1,
                          self.wall_S2, self.wall_SS1, self.wall_SS2, self.wall_SF1,
                          self.wall_SF2,
                          self.wall_SB1, self.wall_SB2]

        self.player = Player(plr_x, plr_y)
        self.wallcount = len(self.wall_list)
        self.dog = Dog()

        self.all_sprites.extend(self.wall_list)
        self.all_sprites.extend([self.dog, self.player])

        # grid draw a grass tile in a 48 size grid
        self.grid = []
        self.image = pygame.image.load("grasstile.png").convert()
        scalesprite(self)

        for y in range(0, SCREEN_HEIGHT, 48):
            for x in range(0, SCREEN_WIDTH, 48):
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
                for t in self.turrets:
                    if t in self.all_sprites and self.player.rect.colliderect(t.rect):
                        if t in theApp.all_sprites:
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
                self.player.changespeed(plr_speed, 0)
            elif event.key == pygame.K_d:
                self.player.changespeed(-plr_speed, 0)
            elif event.key == pygame.K_w:
                self.player.changespeed(0, plr_speed)
            elif event.key == pygame.K_s:
                self.player.changespeed(0, -plr_speed)

    def on_loop(self):
        if random.randrange(1, 101) == 1:
            new_enemy = Enemy()
            self.enemies.add(new_enemy)
            # indsæt fjender lige over vægge
            self.all_sprites.insert(self.wallcount, new_enemy)

        self.bullets.update()
        self.enemies.update()
        self.turrets.update()
        self.player.update()

        if self.dog.dead:
            self.on_render()
            time.sleep(3)
            self._running = False

    def on_render(self):
        # draw grass
        for p in self.grid:
            self._display_surf.blit(self.image, p)

        for sprite in self.floor_sprites:
            # floor is blitted before anything else
            self._display_surf.blit(sprite.image, sprite.rect)

        # display lower sprites on top of higher sprites
        self.all_sprites.sort(key=lambda x: (x.rect.y + x.rect.height))
        for sprite in self.all_sprites:
            # blit each sprite onto display.
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
