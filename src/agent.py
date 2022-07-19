from collections import namedtuple
from hashlib import sha1
import numpy as np
import time

import scipy as sp
from src.game import TicTacGame
from src.constants import MAX_MOVE_TIME
from copy import deepcopy

Node = namedtuple('Node', ['n_visits' ,'n_wins', 'ucb', 'turn', \
    'parent', 'children', 'nea'])

# nea is abbreviation from 'Not Explored Actions'

class MCTSAgent:
    def __init__(self) -> None:
        self.pi_t = {}
        self.I = int(1e5)
        self.Tree = {}

        # C coefficient of UCB formula
        self.C = np.sqrt(2)

    def step(self, game: TicTacGame):

        # temporarily without any memory
        self.Tree = {}
        self.pi_t = {} # tree policy
        self.pi_r = {} # rollout policy

        SS = game.clone() # starting state
        SS_h = SS.get_hash_of_state()

        start = time.time()

        SS_h = game.get_hash_of_state() # hash of the starting state

        self.Tree = Node(
            0, 0, 0, game.get_turn(), None, \
                [], game.get_available_moves()
        )

        for _ in range(self.I):
            end = time.time()
            if end - start > MAX_MOVE_TIME:
                break
            
            S = SS
            S_h = SS_h

            while len(self.Tree.children) and \
                len(self.Tree.nea) == 0:

                S.make_move(self.pi_t[S_h])
                S_h = S.get_hash_of_state()

            Sp = S.clone()
            Sp_h = Sp.get_hash_of_state()

            if len(self.not_visited[S_h]) > 0:
                idx = np.random.randint(0, len(self.not_visited[S_h]))
                action = self.not_visited[S_h][idx]
                self.not_visited[S_h].remove(action)

                Sp.make_move(action)
                Sp_h = Sp.get_hash_of_state()
                if Sp_h not in self.children.keys():
                    self.children[Sp_h] = []
                self.V[Sp_h] = [0, 0, 0, 1 - self.V[S_h][3]]
                self.not_visited[Sp_h] = Sp.get_available_moves()
                self.children[Sp_h].append([Sp_h, action])
                self.parent[Sp_h] = S_h
                S = Sp
                S_h = S.get_hash_of_state()

            Snew = S.clone()
            Snew_h = Snew.get_hash_of_state()

            while not Snew.terminal():
                moves = Snew.get_available_moves()
                idx = np.random.randint(0, len(moves))
                action = moves[idx]
                Snew.make_move(action)
                # Snew_h = Snew.get_hash_of_state()
            r = np.maximum(Snew.rewards(), [0, 0])

            while S_h is not None:

                self.V[S_h][0] += r[self.V[S_h][3]]
                self.V[S_h][1] += 1

                t = self.V[S_h][2]
                n = self.V[S_h][1]
                w = self.V[S_h][0]

                self.V[S_h][2] = w/n + self.C * np.sqrt(np.log(t + 1)/n)
                S_h = self.parent[S_h]

        max_child_idx = np.argmax([self.V[s[0]][1] for s in self.children[SS_h]])
        self.pi_t[SS_h] = self.children[SS_h][max_child_idx][1]


def main():

    game = TicTacGame(1)
    
    agent = MCTSAgent()

    action = agent.step(game)

    print(action)

if __name__ == "__main__":

    main()