import copy
import pprint
from copy import deepcopy
from random import randint


empty = "empty"

w_paw = "w_paw"
w_rook = "w_rook"
w_knight = "w_knight"
w_bishop = "w_bishop"
w_king = "w_king"
w_queen = "w_queen"

b_paw = "b_paw"
b_rook = "b_rook"
b_knight = "b_knight"
b_bishop = "b_bishop"
b_king = "b_king"
b_queen = "b_queen"


chess = [
    [w_rook, w_knight, w_bishop, w_queen, w_king, w_bishop, w_knight, w_rook],
    [w_paw] * 8,
    [empty] * 8, [empty] * 8, [empty] * 8, [empty] * 8,
    [b_paw] * 8,
    [b_rook, b_knight, b_bishop, b_queen, b_king, b_bishop, b_knight, b_rook]
]


class Game:
    users = []
    gaming = False
    join_key = randint(10000, 99999)
    field = []
    start = None
    finish = None

    def __init__(self, id):
        self.id = id
        self.users = []
        self.gaming = False
        self.join_key = randint(10000, 99999)

        self.field = []

    def player_join(self, user):
        if (len(self.users) < 2):
            self.users.append(user)
        else:
            return False
        return True

    def default_field(self, n, t):
        self.size = n
        self.type = t
        if (t == "CHESS"):
            self.field = copy.deepcopy(chess)

    def make_move(self, s, f=None):
        if (f is not None):
            self.field[s[0]][s[1]], self.field[f[0]][f[1]] = self.field[f[0]][f[1]], self.field[s[0]][s[1]]
        elif (self.start is None):
            self.start = s
        else:
            f = copy.copy(s)
            s = self.start
            self.field[s[0]][s[1]], self.field[f[0]][f[1]] = self.field[f[0]][f[1]], self.field[s[0]][s[1]]
            self.start = None

    def reset_field(self):
        self.default_field(self.size, self.type)
        self.start = None
