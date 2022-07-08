import numpy as np
import time
from src.game import TicTacGame

class MCTSAgent:
    def __init__(self) -> None:
        self.pi_t = {}
        self.I = 1e5
        self.V = {}
        self.not_visited = {}
        self.children = {}
        self.parent = {}

        self.C = np.sqrt(2)

    def step(self, game: TicTacGame):

        start = time.time()

        if game.get_hash_of_state() not in self.V.keys():
            self.V[game.]

def main():

    pass

if __name__ == "__main__":

    main()