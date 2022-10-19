from collections import namedtuple
from hashlib import sha1
import numpy as np
import time

import scipy as sp
from src.game import TicTacGame
from src.constants import MAX_MOVE_TIME
from copy import deepcopy

Node = namedtuple('Node', ['n_visits' ,'n_wins', 'ucb', 'turn', \
    'parent', 'ea', 'nea'])

# ea is abbreviation from 'Explored Actions'
# nea is abbreviation from 'Not Explored Actions'

class Node:
    def __init__(self, game: TicTacGame, parent: str) -> None:
        self.n_wins = 0
        self.n_visits = 0
        self.ucb = 0
        self.parent = parent
        self.turn = game.get_turn()
        self.ea = []
        self.nea = game.get_available_moves()

class MCTSAgent:
    def __init__(self) -> None:
        self.pi_t = {}
        self.I = int(1e4)
        self.Tree = {}

        # C coefficient of UCB formula
        self.C = np.sqrt(2)

    def step(self, game: TicTacGame):

        # temporarily without any memory
        self.Tree = {}
        self.pi_t = {} # tree policy
        self.pi_r = {} # rollout policy

        SS = game.clone() # starting state

        start = time.time()

        SS_h = game.get_hash_of_state() # hash of the starting state

        self.root_node = Node(SS, None)
        
        self.Tree[SS_h] = self.root_node
        self.Tree[SS_h].n_visits += 1

        for _ in range(self.I):
            end = time.time()
            if end - start > MAX_MOVE_TIME:
                break
            
            curr_node = SS.clone()

            while len(self.Tree[curr_node.get_hash_of_state()].ea) and \
                len(self.Tree[curr_node.get_hash_of_state()].nea) == 0:

                N = self.Tree[curr_node.get_hash_of_state()].n_visits
                    
                for action, state in self.Tree[curr_node.get_hash_of_state()].ea:
                    
                    n = self.Tree[state].n_visits
                    w = self.Tree[state].n_wins
                    
                    # if n > N:
                    #     print('o')

                    self.Tree[state].ucb = w/n + self.C * np.sqrt(np.log(N)/n)                    
                
                best_idx = np.argmax([self.Tree[s].ucb for a, s in self.Tree[curr_node.get_hash_of_state()].ea])
                
                action, state = self.Tree[curr_node.get_hash_of_state()].ea[best_idx]
                
                self.pi_t[curr_node.get_hash_of_state()] = action
                
                self.Tree[curr_node.get_hash_of_state()].n_visits += 1
                curr_node.make_move(self.pi_t[curr_node.get_hash_of_state()])

            # if 'curr_node' is a terminal state then no more
            # states remain to be explored

                
                # Sp is a state that has not visited actions
            Sp = curr_node.clone()
            Sp_h = Sp.get_hash_of_state()
                
            if curr_node.terminal() == False:
                # choose random actions from state 'Sp'       
                action = np.random.randint(0, len(self.Tree[Sp_h].nea))
                move = self.Tree[Sp_h].nea[action]
                Sp.make_move(move)
                self.Tree[Sp_h].ea.append((move, Sp.get_hash_of_state()))
                self.Tree[Sp_h].nea.pop(action)  
                        
                Sp_h = Sp.get_hash_of_state()            
            
            # if Sp.terminal() and Sp_h == SS_h:
            #     return move
            

            
            # new state that we add to the global tree
            Snew = Sp.clone()
            Snew_h = deepcopy(Sp_h)
        
            if Snew_h not in self.Tree.keys():
                self.Tree[Snew_h] = Node(game=Snew, parent=curr_node.get_hash_of_state())
            self.Tree[Snew_h].n_visits += 1
            
            while Sp.terminal() is False:
                moves = Sp.get_available_moves()
                action = np.random.randint(0, len(moves))
                Sp.make_move(moves[action])
            r = np.maximum(Sp.rewards(), [0,0])

            # backpropagate until visit starting state
            while Snew_h != SS_h:

                self.Tree[Snew_h].n_wins += r[(self.Tree[Snew_h].turn) % 2]
                
                # N = self.Tree[self.Tree[Snew_h].parent]
                # n = self.Tree[Snew_h].n_visits
                # w = self.Tree[Snew_h].n_wins

                # self.Tree[Snew_h].ucb = w/n + self.C * np.sqrt(np.log(N)/n)
                Snew_h = self.Tree[Snew_h].parent
                
                # best_idx = np.argmax([self.Tree[s[1]].ucb for s in self.Tree[Snew_h].ea])
                
                
                
                # self.pi_t[Snew_h] = self.Tree[Snew_h].ea[best_idx][0]
                
        tmp = [(s[0], self.Tree[s[1]].ucb, self.Tree[s[1]].n_visits, self.Tree[s[1]].n_wins, self.Tree[SS_h].n_visits) for s in self.Tree[SS_h].ea]
        
        return self.pi_t[SS_h]


def main():

    game = TicTacGame(1)
    
    agent = MCTSAgent()

    action = agent.step(game)

    print(action)

if __name__ == "__main__":

    main()