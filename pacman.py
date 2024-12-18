#from asyncio.windows_events import NULL
from tarfile import NUL
import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from fruits import Fruits

class Pacman(object):
    def __init__(self, node, life_amount):
        self.life_amount = life_amount
        self.name = PACMAN
        self.directions = {UP:Vector2(0, -1), DOWN:Vector2(0,1), LEFT:Vector2(-1,0), RIGHT:Vector2(1,0), STOP:Vector2()}
        self.direction = STOP
        self.speed = 100
        self.radius = 10
        self.color = YELLOW
        self.node = node
        self.setPosition()
        self.target = node
        self.collideRadius = 5
        self.can_eat_ghosts = False
        self.power_timer = 0
        self.power_duration = 10
        self.prev_action = 100

    def setPosition(self):
        self.position = self.node.position.copy()
     
    def update(self, dt):	
        if self.direction not in self.directions:
            print(f"Invalid direction: {self.direction}")
            return
        self.position += self.directions[self.direction]*self.speed*dt
        self.prev_action = self.direction
        direction = self.getValidKey()

        if self.can_eat_ghosts:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.can_eat_ghosts = False

        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)
            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def validDirection(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                if self.prev_action==100:
                    return True
                else:
                    if direction == self.prev_action:
                        return True
                    elif direction == -1*self.prev_action:
                        self.reverseDirection()
                        return True
        return False



    def getNewTarget(self, direction):
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node    



    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def render(self, screen):
        p = self.position.asInt()
        pygame.draw.circle(screen, self.color, p, self.radius)

    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()

            threshold = 20
            return node2Self >= (node2Target - threshold)
        return False
    
    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self,direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            d = self.position - pellet.position
            dSquared = d.magnitudeSquared()
            rSquared = (pellet.radius+self.collideRadius)**2
            if dSquared <= rSquared:
                return pellet
        return None
    
    def eatFruits(self, fruits):
        d = self.position - fruits.position
        dSquared = d.magnitudeSquared()
        rSquared = (fruits.radius+self.collideRadius)**2
        if dSquared <= rSquared:
            return fruits
        return None

    def collides_with_ghost(self, ghostList):
        for ghost in ghostList:
            distance = self.position - ghost.position
            distance_squared = distance.magnitudeSquared() 
            radius_squared = (ghost.radius + self.collideRadius) ** 2 

            if distance_squared <= radius_squared:
                return ghost
        return None 
