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
        
        # Check for render_mode and set display mode accordingly
        if render_mode:
            # Real rendering mode
            self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
            pygame.display.set_caption("Pacman Game")
        else:
            # Dummy mode for training without display
            self.screen = pygame.Surface(SCREENSIZE)
        
        self.background = None
        self.clock = pygame.time.Clock()
        self.fruits = None

    def setBackground(self):
        # Ensure screen dimensions are correct
        if not hasattr(self, 'screen') or self.screen is None:
            raise ValueError("Screen has not been initialized before calling setBackground.")
    
        # Use screen size from display mode or surface dimensions
        size = self.screen.get_size()
    
        # Headless mode: Use plain surface without .convert()
        if os.environ.get("SDL_VIDEODRIVER") == "dummy":
            self.background = pygame.Surface(size)  # Do not use .convert() in dummy mode
        else:
            self.background = pygame.Surface(size).convert()  # Real mode with display

        self.background.fill(BLACK)

    def showScore(self, score):
        score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

    def startGame(self, life_amount):
        self.setBackground()
        #self.nodes = NodeGroup("maze.txt")
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0,17), (27, 17))
        self.pacman = Pacman(self.nodes.getStartTempNode(), life_amount)
        self.ghosts = Ghosts(self.nodes.nodesPORTAL, 2)
        self.pellets = PelletGroup("maze1.txt")
        self.fruits = None

    def update(self):
        #ilość czasu w sekundach jaka minęła od ostatniego wywołania wiersza
        dt = self.clock.tick(30) / 1000.0
        self.pacman.update(dt)
        self.ghosts.update_ghosts(dt, self.pacman)
        self.pellets.update(dt)
        if self.fruits is not None:
            self.fruits.update(dt)
        self.checkCollisionEvents()
        self.checkEvents()
        self.render()

    #na ten moment jedynie zamyka okno przy naciścięniu X w rogu
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
                if self.pacman.can_eat_ghosts:  # Sprawdzenie, czy Pacman może zjeść duszki
                    ghost.respawn()  # Tylko wtedy teleportuje duszka
                    self.score += 200  # Dodanie punktów za zjedzenie duszka
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
            #print("Updated empty_positions:", [((pos.x/16) +1, (pos.y/16) +1) for pos in self.empty_positions])

            if self.score % 400 == 0 and self.fruits is None:
            #if self.pellets.numEaten % 10 == 0 and self.fruits is None:
                if self.empty_positions:
                    spawn_position = random.choice(self.empty_positions)
                    column = spawn_position.x // TILEWIDTH
                    row = spawn_position.y // TILEHEIGHT
                    self.fruits = Fruits(column, row)  
                 
                else:
                    print("No empty positions available to spawn the fruit.")
        
        if self.fruits is not None:
            #print(f"Fruit is active at ({(self.fruits.position.x/16)+1}, {(self.fruits.position.y/16)+1})")
            if self.pacman.eatFruits(self.fruits):
                self.score += self.fruits.points
                self.pacman.can_eat_ghosts = True
                self.pacman.power_timer = self.pacman.power_duration
                self.fruits = None  
                #print("Pacman ate the fruit.")
            elif self.fruits.destroy:
                self.fruits = None  


    #wykorzystamy do narysowania obrazków na ekranie
    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.nodes.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render_ghosts(self.screen)
        self.pellets.render(self.screen)
        if self.fruits is not None:
            self.fruits.render(self.screen)
        self.showScore(self.score)

        # Only update the display if a real display is set
        if os.environ.get("SDL_VIDEODRIVER") != "dummy":
            pygame.display.update()                  

if __name__ == "__main__":
    game = GameController()
    game.startGame(3)
    while True:
        game.update()
