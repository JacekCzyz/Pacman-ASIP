import pygame
from pygame.locals import *
from constants import *
from ghost import Ghost
from pacman import Pacman
from nodes import NodeGroup
from ghost import *
from pellets import PelletGroup
from fruits import Fruits
import os

class GameController(object):
    def __init__(self, render_mode=True):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.score = 0
        
        if render_mode:
            self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
            pygame.display.set_caption("Pacman Game")
        else:
            self.screen = pygame.Surface(SCREENSIZE)
        
        self.background = None
        self.clock = pygame.time.Clock()
        self.fruits = None

    def setBackground(self):
        if not hasattr(self, 'screen') or self.screen is None:
            raise ValueError("Screen has not been initialized before calling setBackground.")
    
        size = self.screen.get_size()
    
        if os.environ.get("SDL_VIDEODRIVER") == "dummy":
            self.background = pygame.Surface(size)
        else:
            self.background = pygame.Surface(size).convert()

        self.background.fill(BLACK)

    def showScore(self, score):
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

    def startGame(self, life_amount):
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0,17), (27, 17))
        self.pacman = Pacman(self.nodes.getStartTempNode(), life_amount)
        self.ghosts = Ghosts(self.nodes.nodesPORTAL, 2)
        self.pellets = PelletGroup("maze1.txt")
        self.fruits = None

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.pacman.update(dt)
        self.ghosts.update_ghosts(dt, self.pacman)
        self.pellets.update(dt)
        if self.fruits is not None:
            self.fruits.update(dt)
        self.checkCollisionEvents()
        self.checkEvents()
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

    def check_ghost_coll(self, ghost):
        if self.pacman.position.x-self.pacman.radius/2 >= ghost.position.x-ghost.radius/2 and self.pacman.position.x-self.pacman.radius <= ghost.position.x+ghost.radius/2 or self.pacman.position.x+self.pacman.radius/2 >= ghost.position.x-ghost.radius/2 and self.pacman.position.x+self.pacman.radius/2 <= ghost.position.x+ghost.radius/2: 
            if self.pacman.position.y - self.pacman.radius/2 <= ghost.position.y + ghost.radius/2 and self.pacman.position.y - self.pacman.radius/2 >= ghost.position.y - ghost.radius/2 or self.pacman.position.y + self.pacman.radius/2 <= ghost.position.y + ghost.radius/2 and self.pacman.position.y + self.pacman.radius/2 >= ghost.position.y - ghost.radius/2:
                return True
        return False
            

    def checkCollisionEvents(self):
        if not hasattr(self, 'empty_positions'):
            self.empty_positions = []

        for ghost in self.ghosts.ghosts_list:
            if self.check_ghost_coll(ghost):
                if self.pacman.can_eat_ghosts:
                    ghost.respawn() 
                    self.score += 200 
                else:
                    if self.pacman.life_amount != 0:
                        self.startGame(self.pacman.life_amount - 1)
                        self.score = 0
                    else:
                        exit()
        
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.score += pellet.points
            self.pellets.numEaten += 1
            self.pellets.pelletList.remove(pellet)
            self.empty_positions.append(pellet.position)

            if self.score % 400 == 0 and self.fruits is None:
                if self.empty_positions:
                    spawn_position = random.choice(self.empty_positions)
                    column = spawn_position.x // TILEWIDTH
                    row = spawn_position.y // TILEHEIGHT
                    self.fruits = Fruits(column, row)  
                 
                else:
                    print("No empty positions available to spawn the fruit.")
        
        if self.fruits is not None:
            if self.pacman.eatFruits(self.fruits):
                self.score += self.fruits.points
                self.pacman.can_eat_ghosts = True
                self.pacman.power_timer = self.pacman.power_duration
                self.fruits = None  
            elif self.fruits.destroy:
                self.fruits = None  


    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.nodes.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render_ghosts(self.screen)
        self.pellets.render(self.screen)
        if self.fruits is not None:
            self.fruits.render(self.screen)
        self.showScore(self.score)

        if os.environ.get("SDL_VIDEODRIVER") != "dummy":
            pygame.display.update()                  

if __name__ == "__main__":
    game = GameController()
    game.startGame(3)
    while True:
        game.update()