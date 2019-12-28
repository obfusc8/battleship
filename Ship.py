class Ship:

    def __init__(self, ID):
        self.ID = ID
        self.DIR = "H"
        self.name = {1: "Aircraft Carrier",
                     2: "Battleship",
                     3: "Destroyer",
                     4: "Submarine",
                     5: "Patrol Boat"}
        self.size = {1: 5,
                     2: 4,
                     3: 3,
                     4: 3,
                     5: 2}
        self.dir = {"H": [0, 1], "V": [1, 0]}

    def getName(self):
        return str(self.name[self.ID])

    def getID(self):
        return self.ID

    def getSize(self):
        return self.size[self.ID]

    def setDirection(self, d):
        self.DIR = d

    def rotate(self):
        if self.DIR == "H":
            self.DIR = "V"
        else:
            self.DIR = "H"
