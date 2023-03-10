import pygame
import ghost as ghost_obj
import player
import math
import copy


class Game:
    def __init__(self, level, score, music_path, text_path, square, spriteRatio, spriteOffset, game_board, original_board, screen):
        self.paused = True
        self.ghostUpdateDelay = 1
        self.ghostUpdateCount = 0
        self.pacmanUpdateDelay = 1
        self.pacmanUpdateCount = 0
        self.tictakChangeDelay = 10
        self.tictakChangeCount = 0
        self.ghostsAttacked = False
        self.highScore = self.getHighScore()
        self.score = score
        self.level = level
        self.lives = 3
        self.ElementPath = "Assets/ElementImages/"
        self.square = square
        self.spriteRatio = spriteRatio
        self.spriteOffset = spriteOffset
        self.screen = screen
        self.BoardPath = "Assets/BoardImages/"
        self.MusicPath = music_path
        self.DataPath = "Assets/Data/"
        self.TextPath = text_path
        self.gameBoard = game_board
        self.pelletColor = (222, 161, 133)
        self.originalGameBoard = original_board
        self.ghosts = []
#        self.ghosts = [
#            ghost_obj.Ghost(14.0, 13.5, "red", 0, self.ElementPath, square, spriteRatio, spriteOffset, game_board, self, 0, (4, 25)),
#            ghost_obj.Ghost(17.0, 11.5, "blue", 1, self.ElementPath, square, spriteRatio, spriteOffset, game_board, self, 1, (4, 2)),
#            ghost_obj.Ghost(17.0, 13.5, "pink", 2, self.ElementPath, square, spriteRatio, spriteOffset, game_board, self, 2, (26, 2)),
#            ghost_obj.Ghost(17.0, 15.5, "orange", 3, self.ElementPath, square, spriteRatio, spriteOffset, game_board, self, 3, (26, 25))
#        ]
        self.pacman = player.Pacman(26.0, 13.5, self.ElementPath, square, spriteRatio, spriteOffset, game_board, screen) # Center of Second Last Row
        self.total = self.getCount()
        self.ghostScore = 200
        self.levels = [[350, 250], [150, 450], [150, 450], [0, 600]]
        # Level index and Level Progress
        self.ghostStates = [[0, 230], [0, 100], [1, 300], [1, 420]]
        self.collected = 0
        self.started = False
        self.gameOver = False
        self.gameOverCounter = 0
        self.points = []
        self.pointsTimer = 10
        # Berry Spawn Time, Berry Death Time, Berry Eaten
        self.berryState = [200, 400, False]
        self.berryLocation = [20.0, 13.5]
        self.berries = ["tile080.png", "tile081.png", "tile082.png", "tile083.png", "tile084.png", "tile085.png", "tile086.png", "tile087.png"]
        self.berriesCollected = []
        self.levelTimer = 0
        self.berryScore = 100
        self.lockedInTimer = 100
        self.lockedIn = True
        self.extraLifeGiven = False
        self.musicPlaying = 0

    def pause(self, time):
        cur = 0
        while not cur == time:
            cur += 1

    # Reset after death
    def reset(self):
        self.ghosts = []
#        self.ghosts = [
#            ghost_obj.Ghost(14.0, 13.5, "red", 0, self.ElementPath, self.square, self.spriteRatio, self.spriteOffset, self.gameBoard, self, 0, (4, 25)),
#            ghost_obj.Ghost(17.0, 11.5, "blue", 1, self.ElementPath, self.square, self.spriteRatio, self.spriteOffset, self.gameBoard, self, 1, (4, 2)),
#            ghost_obj.Ghost(17.0, 13.5, "pink", 2, self.ElementPath, self.square, self.spriteRatio, self.spriteOffset, self.gameBoard, self, 2, (26, 2)),
#            ghost_obj.Ghost(17.0, 15.5, "orange", 3, self.ElementPath, self.square, self.spriteRatio, self.spriteOffset, self.gameBoard, self, 3, (26, 25))
#        ]
        for ghost in self.ghosts:
            ghost.setTarget()

        self.pacman = player.Pacman(26.0, 13.5, self.ElementPath, self.square, self.spriteRatio, self.spriteOffset, self.gameBoard, self.screen)
        self.lives -= 1
        self.paused = True
        self.render()

    # Driver method: The games primary update method
    def update(self):
        if self.gameOver:
            self.gameOverFunc()
            return
        if self.paused or not self.started:
            self.drawTilesAround(21, 10)
            self.drawTilesAround(21, 11)
            self.drawTilesAround(21, 12)
            self.drawTilesAround(21, 13)
            self.drawTilesAround(21, 14)
            self.drawReady()
            pygame.display.update()
            return

        self.levelTimer += 1
        self.ghostUpdateCount += 1
        self.pacmanUpdateCount += 1
        self.tictakChangeCount += 1
        self.ghostsAttacked = False

        if self.score >= 10000 and not self.extraLifeGiven:
            self.lives += 1
            self.extraLifeGiven = True
            self.forcePlayMusic("pacman_extrapac.wav")

        # Draw tiles around ghosts and pacman
        self.clearBoard()
        for ghost in self.ghosts:
            if ghost.attacked:
                self.ghostsAttacked = True

        # Check if the ghost should case pacman
        index = 0
        for state in self.ghostStates:
            state[1] += 1
            if state[1] >= self.levels[index][state[0]]:
                state[1] = 0
                state[0] += 1
                state[0] %= 2
            index += 1

        index = 0
        for ghost in self.ghosts:
            if not ghost.attacked and not ghost.dead and self.ghostStates[index][0] == 0:
                ghost.target = [self.pacman.row, self.pacman.col]
            index += 1

        if self.levelTimer == self.lockedInTimer:
            self.lockedIn = False

        if self.ghostUpdateCount == self.ghostUpdateDelay:
            for ghost in self.ghosts:
                ghost.update()
            self.ghostUpdateCount = 0

        if self.tictakChangeCount == self.tictakChangeDelay:
            #Changes the color of special Tic-Taks
            self.flipColor()
            self.tictakChangeCount = 0

        if self.pacmanUpdateCount == self.pacmanUpdateDelay:
            self.pacmanUpdateCount = 0
            self.pacman.update()
            self.pacman.col %= len(self.gameBoard[0])
            if self.pacman.row % 1.0 == 0 and self.pacman.col % 1.0 == 0:
                if self.gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 2 or self.gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 7:
                    self.playMusic("munch_1.wav")
                    self.gameBoard[int(self.pacman.row)][int(self.pacman.col)] = 1
                    self.score += 10
                    self.collected += 1
                    # Fill tile with black
                    pygame.draw.rect(self.screen, (0, 0, 0), (self.pacman.col * self.square, self.pacman.row * self.square, self.square, self.square))
                elif self.gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 5 or self.gameBoard[int(self.pacman.row)][int(self.pacman.col)] == 6:
                    self.forcePlayMusic("power_pellet.wav")
                    self.gameBoard[int(self.pacman.row)][int(self.pacman.col)] = 1
                    self.collected += 1
                    # Fill tile with black
                    pygame.draw.rect(self.screen, (0, 0, 0), (self.pacman.col * self.square, self.pacman.row * self.square, self.square, self.square))
                    self.score += 50
                    self.ghostScore = 200
                    for ghost in self.ghosts:
                        ghost.attackedCount = 0
                        ghost.setAttacked(True)
                        ghost.setTarget()
                        self.ghostsAttacked = True
        self.checkSurroundings()
        self.highScore = max(self.score, self.highScore)

        global running
        if self.collected == self.total:
            self.forcePlayMusic("intermission.wav")
            self.level += 1
            self.newLevel()

        if self.level - 1 == 8: #(self.levels[0][0] + self.levels[0][1]) // 50:
            running = False
        self.softRender()

    # Render method
    def render(self):
        self.screen.fill((0, 0, 0)) # Flushes the screen
        # Draws game elements
        currentTile = 0
        self.displayLives()
        self.displayScore()
        for i in range(3, len(self.gameBoard) - 2):
            for j in range(len(self.gameBoard[0])):
                if self.gameBoard[i][j] == 3: # Draw wall
                    imageName = str(currentTile)
                    if len(imageName) == 1:
                        imageName = "00" + imageName
                    elif len(imageName) == 2:
                         imageName = "0" + imageName
                    # Get image of desired tile
                    imageName = "tile" + imageName + ".png"
                    tileImage = pygame.image.load(self.BoardPath + imageName)
                    tileImage = pygame.transform.scale(tileImage, (self.square, self.square))

                    #Display image of tile
                    self.screen.blit(tileImage, (j * self.square, i * self.square, self.square, self.square))

                    # pygame.draw.rect(screen, (0, 0, 255),(j * square, i * square, square, square)) # (x, y, width, height)
                elif self.gameBoard[i][j] == 2 or self.gameBoard[i][j] == 7: # Draw Tic-Tak
                    pygame.draw.circle(self.screen, self.pelletColor,(j * self.square + self.square//2, i * self.square + self.square//2), self.square//4)
                elif self.gameBoard[i][j] == 5: #Black Special Tic-Tak
                    pygame.draw.circle(self.screen, (0, 0, 0),(j * self.square + self.square//2, i * self.square + self.square//2), self.square//2)
                elif self.gameBoard[i][j] == 6: #White Special Tic-Tak
                    pygame.draw.circle(self.screen, self.pelletColor,(j * self.square + self.square//2, i * self.square + self.square//2), self.square//2)

                currentTile += 1
        # Draw Sprites
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        self.pacman.draw(self)
        # Updates the screen
        pygame.display.update()


    def softRender(self):
        pointsToDraw = []
        for point in self.points:
            if point[3] < self.pointsTimer:
                pointsToDraw.append([point[2], point[0], point[1]])
                point[3] += 1
            else:
                self.points.remove(point)
                self.drawTilesAround(point[0], point[1])

        for point in pointsToDraw:
            self.drawPoints(point[0], point[1], point[2])

        # Draw Sprites
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        self.pacman.draw(self)
        self.displayScore()
        self.displayBerries()
        self.displayLives()
        # for point in pointsToDraw:
        #     self.drawPoints(point[0], point[1], point[2])
        self.drawBerry()
        # Updates the screen
        pygame.display.update()

    def playMusic(self, music):
        # return False # Uncomment to disable music
        global musicPlaying
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.unload()
            pygame.mixer.music.load(self.MusicPath + music)
            pygame.mixer.music.queue(self.MusicPath + music)
            pygame.mixer.music.play()
            if music == "munch_1.wav":
                musicPlaying = 0
            elif music == "siren_1.wav":
                musicPlaying = 2
            else:
                musicPlaying = 1

    def forcePlayMusic(self, music):
        # return False # Uncomment to disable music
        pygame.mixer.music.unload()
        pygame.mixer.music.load(self.MusicPath + music)
        pygame.mixer.music.play()
        global musicPlaying
        musicPlaying = 1

    def clearBoard(self):
            # Draw tiles around ghosts and pacman
            for ghost in self.ghosts:
                self.drawTilesAround(ghost.row, ghost.col)
            self.drawTilesAround(self.pacman.row, self.pacman.col)
            self.drawTilesAround(self.berryLocation[0], self.berryLocation[1])
            # Clears Ready! Label
            self.drawTilesAround(20, 10)
            self.drawTilesAround(20, 11)
            self.drawTilesAround(20, 12)
            self.drawTilesAround(20, 13)
            self.drawTilesAround(20, 14)

    def checkSurroundings(self):
        # Check if pacman got killed
        for ghost in self.ghosts:
            if self.touchingPacman(ghost.row, ghost.col) and not ghost.attacked:
                if self.lives == 1:
                    self.forcePlayMusic("death_1.wav")
                    self.gameOver = True
                    #Removes the ghosts from the screen
                    for ghost in self.ghosts:
                        self.drawTilesAround(ghost.row, ghost.col)
                    self.drawTilesAround(self.pacman.row, self.pacman.col)
                    self.pacman.draw(self)
                    pygame.display.update()
                    self.pause(10000000)
                    return
                self.started = False
                self.forcePlayMusic("pacman_death.wav")
                self.reset()
            elif self.touchingPacman(ghost.row, ghost.col) and ghost.isAttacked() and not ghost.isDead():
                ghost.setDead(True)
                ghost.setTarget()
                ghost.ghostSpeed = 1
                ghost.row = math.floor(ghost.row)
                ghost.col = math.floor(ghost.col)
                self.score += self.ghostScore
                self.points.append([ghost.row, ghost.col, self.ghostScore, 0])
                self.ghostScore *= 2
                self.forcePlayMusic("eat_ghost.wav")
                self.pause(10000000)
        if self.touchingPacman(self.berryLocation[0], self.berryLocation[1]) and not self.berryState[2] and self.levelTimer in range(self.berryState[0], self.berryState[1]):
            self.berryState[2] = True
            self.score += self.berryScore
            self.points.append([self.berryLocation[0], self.berryLocation[1], self.berryScore, 0])
            self.berriesCollected.append(self.berries[(self.level - 1) % 8])
            self.forcePlayMusic("eat_fruit.wav")
    # Displays the current score
    def displayScore(self):
        textOneUp = ["tile033.png", "tile021.png", "tile016.png"]
        textHighScore = ["tile007.png", "tile008.png", "tile006.png", "tile007.png", "tile015.png", "tile019.png", "tile002.png", "tile014.png", "tile018.png", "tile004.png"]
        index = 0
        scoreStart = 5
        highScoreStart = 11
        for i in range(scoreStart, scoreStart+len(textOneUp)):
            tileImage = pygame.image.load(self.TextPath + textOneUp[index])
            tileImage = pygame.transform.scale(tileImage, (self.square, self.square))
            self.screen.blit(tileImage, (i * self.square, 4, self.square, self.square))
            index += 1
        score = str(self.score)
        if score == "0":
            score = "00"
        index = 0
        for i in range(0, len(score)):
            digit = int(score[i])
            tileImage = pygame.image.load(self.TextPath + "tile0" + str(32 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (self.square, self.square))
            self.screen.blit(tileImage, ((scoreStart + 2 + index) * self.square, self.square + 4, self.square, self.square))
            index += 1

        index = 0
        for i in range(highScoreStart, highScoreStart+len(textHighScore)):
            tileImage = pygame.image.load(self.TextPath + textHighScore[index])
            tileImage = pygame.transform.scale(tileImage, (self.square, self.square))
            self.screen.blit(tileImage, (i * self.square, 4, self.square, self.square))
            index += 1

        highScore = str(self.highScore)
        if highScore == "0":
            highScore = "00"
        index = 0
        for i in range(0, len(highScore)):
            digit = int(highScore[i])
            tileImage = pygame.image.load(self.TextPath + "tile0" + str(32 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (self.square, self.square))
            self.screen.blit(tileImage, ((highScoreStart + 6 + index) * self.square, self.square + 4, self.square, self.square))
            index += 1

    def drawBerry(self):
        if self.levelTimer in range(self.berryState[0], self.berryState[1]) and not self.berryState[2]:
            berryImage = pygame.image.load(self.ElementPath + self.berries[(self.level - 1) % 8])
            berryImage = pygame.transform.scale(berryImage, (int(self.square * self.spriteRatio), int(self.square * self.spriteRatio)))
            self.screen.blit(berryImage, (self.berryLocation[1] * self.square, self.berryLocation[0] * self.square, self.square, self.square))


    def drawPoints(self, points, row, col):
        pointStr = str(points)
        index = 0
        for i in range(len(pointStr)):
            digit = int(pointStr[i])
            tileImage = pygame.image.load(self.TextPath + "tile" + str(224 + digit) + ".png")
            tileImage = pygame.transform.scale(tileImage, (self.square//2, self.square//2))
            self.screen.blit(tileImage, ((col) * self.square + (self.square//2 * index), row * self.square - 20, self.square//2, self.square//2))
            index += 1

    def drawReady(self):
        ready = ["tile274.png", "tile260.png", "tile256.png", "tile259.png", "tile281.png", "tile283.png"]
        for i in range(len(ready)):
            letter = pygame.image.load(self.TextPath + ready[i])
            letter = pygame.transform.scale(letter, (int(self.square), int(self.square)))
            self.screen.blit(letter, ((11 + i) * self.square, 20 * self.square, self.square, self.square))

    def gameOverFunc(self):
        global running
        if self.gameOverCounter == 12:
            running = False
            self.recordHighScore()
            return

        # Resets the screen around pacman
        self.drawTilesAround(self.pacman.row, self.pacman.col)

        # Draws new image
        pacmanImage = pygame.image.load(self.ElementPath + "tile" + str(116 + self.gameOverCounter) + ".png")
        pacmanImage = pygame.transform.scale(pacmanImage, (int(self.square * self.spriteRatio), int(self.square * self.spriteRatio)))
        self.screen.blit(pacmanImage, (self.pacman.col * self.square + self.spriteOffset, self.pacman.row * self.square + self.spriteOffset, self.square, self.square))
        pygame.display.update()
        self.pause(5000000)
        self.gameOverCounter += 1

    def displayLives(self):
        # 33 rows || 28 cols
        # Lives[[31, 5], [31, 3], [31, 1]]
        livesLoc = [[34, 3], [34, 1]]
        for i in range(self.lives - 1):
            lifeImage = pygame.image.load(self.ElementPath + "tile054.png")
            lifeImage = pygame.transform.scale(lifeImage, (int(self.square * self.spriteRatio), int(self.square * self.spriteRatio)))
            self.screen.blit(lifeImage, (livesLoc[i][1] * self.square, livesLoc[i][0] * self.square - self.spriteOffset, self.square, self.square))

    def displayBerries(self):
        firstBerrie = [34, 26]
        for i in range(len(self.berriesCollected)):
            berrieImage = pygame.image.load(self.ElementPath + self.berriesCollected[i])
            berrieImage = pygame.transform.scale(berrieImage, (int(self.square * self.spriteRatio), int(self.square * self.spriteRatio)))
            self.screen.blit(berrieImage, ((firstBerrie[1] - (2*i)) * self.square, firstBerrie[0] * self.square + 5, self.square, self.square))

    def touchingPacman(self, row, col):
        if row - 0.5 <= self.pacman.row and row >= self.pacman.row and col == self.pacman.col:
            return True
        elif row + 0.5 >= self.pacman.row and row <= self.pacman.row and col == self.pacman.col:
            return True
        elif row == self.pacman.row and col - 0.5 <= self.pacman.col and col >= self.pacman.col:
            return True
        elif row == self.pacman.row and col + 0.5 >= self.pacman.col and col <= self.pacman.col:
            return True
        elif row == self.pacman.row and col == self.pacman.col:
            return True
        return False

    def newLevel(self):
        self.reset()
        self.lives += 1
        self.collected = 0
        self.started = False
        self.berryState = [200, 400, False]
        self.levelTimer = 0
        self.lockedIn = True
        for level in self.levels:
            level[0] = min((level[0] + level[1]) - 100, level[0] + 50)
            level[1] = max(100, level[1] - 50)
        self.gameBoard = copy.deepcopy(self.originalGameBoard)
        self.render()

    def drawTilesAround(self, row, col):
        row = math.floor(row)
        col = math.floor(col)
        for i in range(row-2, row+3):
            for j in range(col-2, col+3):
                if i >= 3 and i < len(self.gameBoard) - 2 and j >= 0 and j < len(self.gameBoard[0]):
                    imageName = str(((i - 3) * len(self.gameBoard[0])) + j)
                    if len(imageName) == 1:
                        imageName = "00" + imageName
                    elif len(imageName) == 2:
                         imageName = "0" + imageName
                    # Get image of desired tile
                    imageName = "tile" + imageName + ".png"
                    tileImage = pygame.image.load(self.BoardPath + imageName)
                    tileImage = pygame.transform.scale(tileImage, (self.square, self.square))
                    #Display image of tile
                    self.screen.blit(tileImage, (j * self.square, i * self.square, self.square, self.square))

                    if self.gameBoard[i][j] == 2: # Draw Tic-Tak
                        pygame.draw.circle(self.screen, self.pelletColor,(j * self.square + self.square//2, i * self.square + self.square//2), self.square//4)
                    elif self.gameBoard[i][j] == 5: #Black Special Tic-Tak
                        pygame.draw.circle(self.screen, (0, 0, 0),(j * self.square + self.square//2, i * self.square + self.square//2), self.square//2)
                    elif self.gameBoard[i][j] == 6: #White Special Tic-Tak
                        pygame.draw.circle(self.screen, self.pelletColor,(j * self.square + self.square//2, i * self.square + self.square//2), self.square//2)

    # Flips Color of Special Tic-Taks
    def flipColor(self):
        for i in range(3, len(self.gameBoard) - 2):
            for j in range(len(self.gameBoard[0])):
                if self.gameBoard[i][j] == 5:
                    self.gameBoard[i][j] = 6
                    pygame.draw.circle(self.screen, self.pelletColor,(j * self.square + self.square//2, i * self.square + self.square//2), self.square//2)
                elif self.gameBoard[i][j] == 6:
                    self.gameBoard[i][j] = 5
                    pygame.draw.circle(self.screen, (0, 0, 0),(j * self.square + self.square//2, i * self.square + self.square//2), self.square//2)

    def getCount(self):
        total = 0
        for i in range(3, len(self.gameBoard) - 2):
            for j in range(len(self.gameBoard[0])):
                if self.gameBoard[i][j] == 2 or self.gameBoard[i][j] == 5 or self.gameBoard[i][j] == 6 or self.gameBoard[i][j] == 7:
                    total += 1
        return total

    def getHighScore(self):
        file = open("Assets/Data/" + "HighScore.txt", "r")
        highScore = int(file.read())
        file.close()
        return highScore

    def recordHighScore(self):
        file = open(self.DataPath + "HighScore.txt", "w").close()
        file = open(self.DataPath + "HighScore.txt", "w+")
        file.write(str(self.highScore))
        file.close()
