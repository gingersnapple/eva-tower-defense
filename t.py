import pygame
import time

oldtime = time.time()

while True:
    print(int(round(time.time()))-oldtime)
    time.sleep(1)