from enum import Enum

BOARD_SIZE = 9

WIN = 1
LOSS = 0
DRAW = 0.5

class Player(Enum):
    CIRLCE = 1
    CROSS = 2

class Field(Enum):
    Cirlce = 1
    Cross = 2
    Empty = 0
    Undecided = 3

char_mapper = {
    Field.Empty.value: ' ',
    Field.Cirlce.value: '0',
    Field.Cross.value: 'X'
}

MAX_MOVE_TIME = 2

HASH_SIZE = 3