from enum import auto, Enum


class GameStates(Enum):
    PLAYERS_TURN = auto()
    ENEMY_TURN = auto()
    PLAYER_DEAD = auto()
    SHOW_INVENTORY = auto()
    DROP_INVENTORY = auto()
    TARGETING = auto()
