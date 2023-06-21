import unittest
import numpy as np
import sys

from ..src.game import TicTacGame

class makeMoveTest(unittest.TestCase):

    def test_game_make_move(self):

        game_1 = TicTacGame(1)
        

        game_2 = TicTacGame(2)

        while ~game_1.termninal():
            
            game_1.make_move()