import random
from copy import deepcopy
from Ship import Ship


class GameBoard:

    def __init__(self, p_board=None, o_board=None):
        self.p_board = [[0 for x in range(10)] for x in range(10)]
        self.o_board = [[0 for x in range(10)] for x in range(10)]
        if p_board is not None:
            self.p_board = deepcopy(p_board)
        if o_board is not None:
            self.o_board = deepcopy(o_board)

    def reset(self):
        for i in range(10):
            for j in range(10):
                self.p_board[i][j] = 0
                self.o_board[i][j] = 0

    def copy(self):
        return GameBoard(self.p_board, self.o_board)

    def sendBoard(self):
        temp = ""
        for i in self.p_board:
            for j in i:
                temp += str(j)
        return temp

    def receiveBoard(self, board):
        for i in range(len(board)):
            self.o_board[i // 10][i % 10] = int(board[i])

    def getPBoard(self):
        return self.p_board

    def getOBoard(self):
        return self.o_board

    def oBoardIsKnown(self):
        count = 0
        for i in range(100):
            if self.o_board[i // 10][i % 10] == 0 or self.o_board[i // 10][i % 10] == 6:
                count += 1
        if count == 83:
            return True
        else:
            return False

    def shipsRemaining(self):
        count = 0
        for i in range(100):
            if 1 <= self.p_board[i // 10][i % 10] <= 5:
                count += 1
        return count

    def setShip(self, r, c, ship):
        b = self.p_board
        s = ship
        # *** OUT OF BOUNDS? ***#
        if s.DIR == "H" and s.size[s.getID()] + c > 10:
            return False
        elif s.DIR == "V" and s.size[s.getID()] + r > 10:
            return False
        # *** OBSTRUCTION? ***#
        for i in range(s.size[s.getID()]):
            row = r + i * s.dir[s.DIR][0]
            col = c + i * s.dir[s.DIR][1]
            if b[row][col] != 0:
                return False
        # *** PLACE SHIP ***#
        for i in range(s.size[s.getID()]):
            row = r + i * s.dir[s.DIR][0]
            col = c + i * s.dir[s.DIR][1]
            b[row][col] = s.getID()
        return True

    def autoSet(self):
        # Board must be empty #
        for i in range(100):
            if self.p_board[i // 10][i % 10] != 0:
                return False
        for i in range(1, 6):
            ship = Ship(i)
            vert = random.randrange(2)
            if vert == 1:
                ship.setDirection("V")
            success = False
            while not success:
                row = random.randrange(10)
                col = random.randrange(10)
                success = self.setShip(row, col, ship)
        return True

    def isSet(self):
        count = 0
        for i in range(100):
            if 1 <= self.p_board[i // 10][i % 10] <= 5:
                count += 1
        if count == 17:
            return True
        else:
            return False

    def receiveShot(self, r, c):
        b = self.p_board
        if (1 <= b[r][c] <= 5) or b[r][c] == 7:
            # *** HIT ***#
            b[r][c] = 7
            return True
        else:
            # *** MISS ***#
            b[r][c] = 6
            return False

    def logShot(self, r, c, hit):
        b = self.o_board
        if hit:
            # *** HIT ***#
            b[r][c] = 7
        else:
            # *** MISS ***#
            b[r][c] = 6

    def isWin(self):
        count = 0
        for i in range(100):
            if self.o_board[i // 10][i % 10] == 7:
                count += 1
        if count == 17:
            return True
        else:
            return False

    def hasLost(self):
        count = 0
        for i in range(100):
            if self.p_board[i // 10][i % 10] == 7:
                count += 1
        if count == 17:
            return True
        else:
            return False

    def findEnemyMiss(self):
        for i in range(100):
            if self.o_board[i // 10][i % 10] == 0:
                return str(i // 10) + str(i % 10)
        return False

    def findMiss(self):
        for i in range(100):
            if self.p_board[i // 10][i % 10] == 0:
                return str(i // 10) + str(i % 10)
        return False

    def findEnemyHit(self):
        for i in range(100):
            if self.o_board[i // 10][i % 10] == 7:
                return str(i // 10) + str(i % 10)
        return False

    def findHit(self):
        for i in range(100):
            if 1 <= self.p_board[i // 10][i % 10] <= 5:
                return str(i // 10) + str(i % 10)
        return False

    def takeHit(self):
        for i in range(100):
            if 1 <= self.p_board[i // 10][i % 10] <= 5:
                self.p_board[i // 10][i % 10] = 7
                return True
        return False

    def nuke(self):
        for i in range(100):
            if 1 <= self.p_board[i // 10][i % 10] <= 5:
                self.p_board[i // 10][i % 10] = 7
        return True
