from random import randint


class Game:
    def __init__(self, id):
        self.id = id
        self.players = []
        self.gaming = False
        self.join_code = randint(10000, 99999)

    def player_join(self, user):
        if (len(self.players) < 2):
            self.players.append(user)
        else:
            return False
        return True