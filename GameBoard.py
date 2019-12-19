import random
from copy import copy, deepcopy
from Ship import Ship

class GameBoard():

    def __init__(self, p_board=None, o_board=None):
        S = b'\xe2\x96\x88'.decode('utf-8')
        H = b'\xe2\x96\x92'.decode('utf-8')
        M = b'\xe2\x97\x8f'.decode('utf-8')
        X = b'\xe2\x95\xb3'.decode('utf-8')
        self.pieces = {0:"   ", # 0-Empty
                       1:S+S+S, # 1-Carrier
                       2:S+S+S, # 2-Battleship
                       3:S+S+S, # 3-Destroyer
                       4:S+S+S, # 4-Submarine
                       5:S+S+S, # 5-Patrol 
                       6:' '+M+' ', # 6-MISS
                       7:H+'X'+H} # 7-HIT
        self.rows = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9}
        self.p_board = [[0 for x in range(10)] for x in range(10)]
        self.o_board = [[0 for x in range(10)] for x in range(10)]
        if (p_board != None):
            self.p_board = deepcopy(p_board)
        if (o_board != None):
            self.o_board = deepcopy(o_board)

    def __repr__(self):
        pb = self.p_board
        ob = self.o_board
        space = "   "
        view =      ""
        view +=      "  ***************    YOU    ***************" + space
        view +=     "   ***************   ENEMY   ***************" + "\n\n"
        view +=     "     0   1   2   3   4   5   6   7   8   9  " + space
        view +=     "     0   1   2   3   4   5   6   7   8   9  " + "\n"
        view += "   ┏━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┓" + space
        view += "   ┏━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┯━━━┓" + "\n"
        labels = list(self.rows)
        for i in range(10):
            view += " "+ labels[i] + " ┃"
            for j in range(10):
                #*** PLAYER BOARD ***#
                if (j < 9):
                    view += self.pieces[pb[i][j]] + "┊"
                else:
                    view += self.pieces[pb[i][j]] + "┃"
            view += space
            view += " "+ labels[i] + " ┃"
            for j in range(10):
                #*** OPPONENT BOARD ***#
                if (j < 9):
                    view += self.pieces[ob[i][j]] + "┊"
                else:
                    view += self.pieces[ob[i][j]] + "┃"
            view += "\n"
            if (i < 9):
                view += "   ┠╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┨" + space
                view += "   ┠╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┼╌╌╌┨" + "\n"
        view +=     "   ┗━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┛" + space
        view +=     "   ┗━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┷━━━┛" + "\n"
        return view

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
            self.o_board[i//10][i%10] = int(board[i])

    def getPBoard(self):
        return self.p_board

    def getOBoard(self):
        return self.o_board

    def setShip(self, r, c, ship):
        if (type(int()) != type(r)):
            r = int(self.rows[r])
        b = self.p_board
        s = ship
        #*** OUT OF BOUNDS? ***#
        if (s.DIR == "H" and s.size[s.getID()] + c > 10):
            return False
        elif (s.DIR == "V" and s.size[s.getID()] + r > 10):
            return False
        #*** OBSTRUCTION? ***#
        for i in range(s.size[s.getID()]):
            row = r + i * s.dir[s.DIR][0]
            col = c + i * s.dir[s.DIR][1]
            if (b[row][col] != 0):
                return False
        #*** PLACE SHIP ***#
        for i in range(s.size[s.getID()]):
            row = r + i * s.dir[s.DIR][0]
            col = c + i * s.dir[s.DIR][1]
            b[row][col] = s.getID()
        return True

    def autoSet(self):
        # Board must be empty #
        for i in range(100):
            if (self.p_board[i//10][i%10] != 0):
                return False
        for i in range(1,6):
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
            if (self.p_board[i//10][i%10] >= 1 and self.p_board[i//10][i%10] <= 5):
                count += 1
        if count == 17:
            return True
        else:
            return False
        

    def receiveShot(self, r, c):
        if (type(int()) != type(r)):
            r = int(self.rows[r.upper()])
        b = self.p_board
        if ((b[r][c] >= 1 and b[r][c] <= 5) or b[r][c] == 7):
            #*** HIT ***#
            b[r][c] = 7
            return True
        else:
            #*** MISS ***#
            b[r][c] = 6
            return False

    def logShot(self, r, c, hit):
        if (type(int()) != type(r)):
            r = int(self.rows[r.upper()])
        b = self.o_board
        if hit:
            #*** HIT ***#
            b[r][c] = 7
        else:
            #*** MISS ***#
            b[r][c] = 6

    def isWin(self):
        count = 0
        for i in range(100):
            if (self.o_board[i//10][i%10] == 7):
                count += 1
        if count == 17:
            return True
        else:
            return False

    def hasLost(self):
        count = 0
        for i in range(100):
            if (self.p_board[i//10][i%10] == 7):
                count += 1
        if count == 17:
            return True
        else:
            return False

    def findEnemyMiss(self):
        for i in range(100):
            if (self.o_board[i//10][i%10] == 0):
                labels = list(self.rows)
                return labels[i//10]+str(i%10)
        return False

    def findMiss(self):
        for i in range(100):
            if (self.p_board[i//10][i%10] == 0):
                labels = list(self.rows)
                return labels[i//10]+str(i%10)
        return False

    def findEnemyHit(self):
        for i in range(100):
            if (self.o_board[i//10][i%10] == 7):
                labels = list(self.rows)
                return labels[i//10]+str(i%10)
        return False

    def findHit(self):
        for i in range(100):
            if (self.p_board[i//10][i%10] >= 1 and self.p_board[i//10][i%10] <= 5):
                labels = list(self.rows)
                return labels[i//10]+str(i%10)
        return False

    def nuke(self):
        for i in range(100):
            if (self.p_board[i//10][i%10] >= 1 and self.p_board[i//10][i%10] <= 5):
                self.p_board[i//10][i%10] = 7
        return True
