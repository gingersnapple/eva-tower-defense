import pygame
from pygame.locals import (FULLSCREEN)
import math
import random

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

clock = pygame.time.Clock()


class Wall(pygame.sprite.Sprite):
    def __init__(self, sprite, pos):
        # Call the parent's constructor
        super().__init__()
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
        super().__init__()
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
        self.rect.x = App.hitbox.rect.x
        self.rect.y = (App.hitbox.rect.y - 48)


class Hitbox(Player):
    def __init__(self):
        super(Hitbox, self).__init__(10, 500)
        self.surf = pygame.Surface((42, 15))
        self.rect = self.surf.get_rect()

        self.rect.x = App.player.x
        self.rect.y = (App.player.y + 48)

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

        App.player.update()


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = SCREEN_WIDTH, SCREEN_HEIGHT

        self.all_sprites = []

    def on_init(self):
        pygame.init()
        if fullscreen:
            self._display_surf = pygame.display.set_mode(self.size, FULLSCREEN | pygame.DOUBLEBUF)
        else:
            self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True


        # Beskriver hvor væggene skal hen. er foreløbigt grimt skrevet fordi
        # enkelte vægge også skal et par ekstra pixels i en retning
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

        self.dog = Dog()
        self.all_sprites.append(self.dog, self.player, self.wall_list)


        for wall in self.wall_list:
            self.all_sprites.append(wall)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        self._display_surf.fill((168, 238, 121))
        for sprite in self.all_sprites:
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
