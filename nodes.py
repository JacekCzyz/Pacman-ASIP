import pygame
from vector import Vector2
from constants import *
import numpy as np

class Node(object):
    def __init__(self, x, y):
        self.position = Vector2(x,y)
        self.neighbors = {UP:None, DOWN:None, LEFT:None, RIGHT:None, PORTAL: None, STOP: None}


    def render(self, screen):
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.asTuple()
                line_end = self.neighbors[n].position.asTuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.asInt(), 12)

class NodeGroup(object):
    def __init__(self, level):
        self.level = level
        self.nodesPORTAL = []
        self.nodesST = {}
        self.nodeSymbols = ['+', 'P', 'n']
        self.pathSymbols = ['.', '-', '|', 'p']
        data = self.readMaze(level)
        self.createNodeTable(data)
        self.connectHorizontally(data)
        self.connectVertically(data)

    def render(self, screen):
        for node in self.nodesST.values():
            node.render(screen)

    def readMaze(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')
    
    def createNodeTable(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    x, y = self.constructKey(col+xoffset, row+yoffset)
                    self.nodesST[(x, y)] = Node(x, y)

    def constructKey(self, x, y):
        return x * TILEWIDTH, y * TILEHEIGHT
    
    def connectHorizontally(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesST[key].neighbors[RIGHT] = self.nodesST[otherkey]
                        self.nodesST[otherkey].neighbors[LEFT] = self.nodesST[key]
                        key = otherkey
                elif data[row][col] not in self.pathSymbols:
                    key = None

    def connectVertically(self, data, xoffset=0, yoffset=0):
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesST[key].neighbors[DOWN] = self.nodesST[otherkey]
                        self.nodesST[otherkey].neighbors[UP] = self.nodesST[key]
                        key = otherkey
                elif dataT[col][row] not in self.pathSymbols:
                    key = None

                   
    def getNodeFromPixels(self, xpixel, ypixel):
        if (xpixel, ypixel) in self.nodesST.keys():
            return self.nodesST[(xpixel, ypixel)]
        return None
    
    def getNodeFromTiles(self, col, row):
        x, y = self.constructKey(col, row)
        if (x, y)  in self.nodesST.keys():
            return self.nodesST[(x,y)]
        return None
    
    def getStartTempNode(self):
        nodes = list(self.nodesST.values())
        return nodes[0]

    def setPortalPair(self, pair1, pair2):
        key1 = self.constructKey(*pair1)
        key2 = self.constructKey(*pair2)
        if key1 in self.nodesST.keys() and key2 in self.nodesST.keys():
            self.nodesST[key1].neighbors[PORTAL] =self.nodesST[key2]
            self.nodesST[key2].neighbors[PORTAL] =self.nodesST[key1]
            self.nodesPORTAL.append(self.nodesST[key2])
            self.nodesPORTAL.append(self.nodesST[key1])