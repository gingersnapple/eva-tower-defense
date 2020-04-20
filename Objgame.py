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
    def __init__(self, sprite, x, y):
        # Call the parent's constructor
        super().__init__()
        self.image = pygame.image.load(sprite).convert()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

        # replace new_width and new_height with the desired width and height
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_size()[0] * wall_scale,
                                             self.image.get_size()[1] * wall_scale))

        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


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


# dog = Dog()

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

        sc = 48
        self.wall_L1 = Wall("wall-long.png", 6, 2)
        self.wall_L2 = Wall("wall-long.png", 18, 2)
        self.wall_L3 = Wall("wall-long.png", 6, 14)
        self.wall_L4 = Wall("wall-long.png", 18, 14)
        self.wall_L5 = Wall("wall-long.png", 12, 6)
        self.wall_S1 = Wall("wall-side.png", 3, 6)
        self.wall_S2 = Wall("wall-side.png", 28, 6)
        self.wall_SS1 = Wall("wall-short-side.png", 7, 6)
        self.wall_SS2 = Wall("wall-short-side.png", 24, 6)

        self.wall_SF1 = Wall("wall-short-l.png", 8, 10)
        self.wall_SB1 = Wall("wall-short-l.png", 8, 6)

        self.wall_SF2 = Wall("wall-short-r.png", 22, 10)
        self.wall_SB2 = Wall("wall-short-r.png", 22, 6)
        self.wall_list = [self.wall_L1, self.wall_L2, self.wall_L3, self.wall_L4, self.wall_L5, self.wall_S1,
                          self.wall_S2, self.wall_SS1, self.wall_SS2, self.wall_SF1,
                          self.wall_SF2,
                          self.wall_SB1, self.wall_SB2]

        for wall in self.wall_list:
            wall.x *= sc
            wall.y *= sc

            # correct position of some walls
            if wall == self.wall_SS2 or wall == self.wall_SF2 or wall == self.wall_SB2:
                wall.x -= 6

            elif wall == self.wall_SF1 or wall == self.wall_SB1:
                wall.x += 6

            self.all_sprites.append(wall)

        self.dog = Dog()
        self.all_sprites.append(self.dog)

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
