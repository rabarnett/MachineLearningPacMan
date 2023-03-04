import pygame
import math


class Pacman:
    def __init__(self, row, col, element_path, square, sprite_ratio, offset, game_board, screen):
        self.row = row
        self.col = col
        self.mouthOpen = False
        self.pacSpeed = 1/4
        self.mouthChangeDelay = 5
        self.mouthChangeCount = 0
        self.dir = 0 # 0: North, 1: East, 2: South, 3: West
        self.newDir = 0
        self.ElementPath = element_path
        self.square = square
        self.spriteRatio = sprite_ratio
        self.gameBoard = game_board
        self.screen = screen
        self.spriteOffset = offset

    def canMove(self, row, col):
        if col == -1 or col == len(self.gameBoard[0]):
            return True
        if self.gameBoard[int(row)][int(col)] != 3:
            return True
        return False

    def update(self):
        if self.newDir == 0:
            if self.canMove(math.floor(self.row - self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 1:
            if self.canMove(self.row, math.ceil(self.col + self.pacSpeed)) and self.row % 1.0 == 0:
                self.col += self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 2:
            if self.canMove(math.ceil(self.row + self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.pacSpeed
                self.dir = self.newDir
                return
        elif self.newDir == 3:
            if self.canMove(self.row, math.floor(self.col - self.pacSpeed)) and self.row % 1.0 == 0:
                self.col -= self.pacSpeed
                self.dir = self.newDir
                return

        if self.dir == 0:
            if self.canMove(math.floor(self.row - self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row -= self.pacSpeed
        elif self.dir == 1:
            if self.canMove(self.row, math.ceil(self.col + self.pacSpeed)) and self.row % 1.0 == 0:
                self.col += self.pacSpeed
        elif self.dir == 2:
            if self.canMove(math.ceil(self.row + self.pacSpeed), self.col) and self.col % 1.0 == 0:
                self.row += self.pacSpeed
        elif self.dir == 3:
            if self.canMove(self.row, math.floor(self.col - self.pacSpeed)) and self.row % 1.0 == 0:
                self.col -= self.pacSpeed

    # Draws pacman based on his current state
    def draw(self, game):
        if not game.started:
            pacmanImage = pygame.image.load(self.ElementPath + "tile112.png")
            pacmanImage = pygame.transform.scale(pacmanImage, (int(self.square * self.spriteRatio), int(self.square * self.spriteRatio)))
            self.screen.blit(pacmanImage, (self.col * self.square + self.spriteOffset, self.row * self.square + self.spriteOffset, self.square, self.square))
            return

        if self.mouthChangeCount == self.mouthChangeDelay:
            self.mouthChangeCount = 0
            self.mouthOpen = not self.mouthOpen
        self.mouthChangeCount += 1
        # pacmanImage = pygame.image.load("Sprites/tile049.png")
        if self.dir == 0:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(self.ElementPath + "tile049.png")
            else:
                pacmanImage = pygame.image.load(self.ElementPath + "tile051.png")
        elif self.dir == 1:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(self.ElementPath + "tile052.png")
            else:
                pacmanImage = pygame.image.load(self.ElementPath + "tile054.png")
        elif self.dir == 2:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(self.ElementPath + "tile053.png")
            else:
                pacmanImage = pygame.image.load(self.ElementPath + "tile055.png")
        elif self.dir == 3:
            if self.mouthOpen:
                pacmanImage = pygame.image.load(self.ElementPath + "tile048.png")
            else:
                pacmanImage = pygame.image.load(self.ElementPath + "tile050.png")

        pacmanImage = pygame.transform.scale(pacmanImage, (int(self.square * self.spriteRatio), int(self.square * self.spriteRatio)))
        self.screen.blit(pacmanImage, (self.col * self.square + self.spriteOffset, self.row * self.square + self.spriteOffset, self.square, self.square))