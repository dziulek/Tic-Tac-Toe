from enum import Enum
from collections import namedtuple

BOARD_SIZE = 9

WIN = 1
LOSS = 0
DRAW = 0.5

class Player(Enum):
    CIRCLE = 1
    CROSS = 2

class Field(Enum):
    Circle = 1
    Cross = 2
    Empty = 0
    Undecided = 3

char_mapper = {
    Field.Empty.value: ' ',
    Field.Circle.value: 'O',
    Field.Cross.value: 'X'
}

MAX_MOVE_TIME = 3

HASH_SIZE = 3

Node = namedtuple('Node', ['n_visits' ,'n_wins', 'ucb', 'turn', \
    'parent', 'ea', 'nea'])

