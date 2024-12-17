import pygame
from vector import Vector2
from constants import *

class Fruits(object):
    def __init__(self, column, row):
        self.name = FRUITS
        self.color = PURPLE
        self.timer = 0
        self.lifetime = 10
        self.destroy = False
        self.points = 100
        self.radius = int(8*TILEWIDTH/16)
        self.collideRadius = int(4*TILEWIDTH/16)
        self.position = Vector2(column*TILEWIDTH, row*TILEHEIGHT)

    def render(self, screen):
        if not self.destroy:  # Change this line to check if the fruit is not destroyed
            p = self.position.asInt()
            pygame.draw.circle(screen, self.color, p, self.radius)


    def update(self, dt):
        self.timer+=dt
        if self.timer >= self.lifetime:
            self.destroy = True