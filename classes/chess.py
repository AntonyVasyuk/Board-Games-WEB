from classes.game import Game


class Chess(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_field(8, "CHESS")


