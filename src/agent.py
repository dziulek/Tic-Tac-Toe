from collections import namedtuple
from hashlib import sha1
import numpy as np
import time

import scipy as sp
from src.game import TicTacGame
from src.constants import MAX_MOVE_TIME, Node
from copy import deepcopy

from src.utils import prune_tree

# ea is abbreviation from 'Explored Actions'
# nea is abbreviation from 'Not Explored Actions'

class Node:
    def __init__(self, game: TicTacGame, parent: str) -> None:
        self.n_wins = 0 # number of wins in the node
        self.n_visits = 0 # number of visits in the node
        self.ucb = 0 # Upper Confidence Bound - exploitation and exploration
        self.parent = parent # parent in the tree
        self.turn = game.get_turn() # which player to move
        self.ea = [] # list of explored actions
        self.nea = game.get_available_moves() # list of not explored actions

class MCTSAgent:
    def __init__(self) -> None:
        self.pi_t = {} # main policy
        self.I = int(1e4) # Constant, indicates how many simulations to execute
        self.Tree = {} # Structure of the searching tree

        # C coefficient of the UCB formula
        self.C = np.sqrt(2)

    def step(self, game: TicTacGame):

        self.pi_t = {} # tree policy
        self.pi_r = {} # rollout policy

        SS = game.clone() # starting state

        # use existing evaluations to speed up the search procedure
        # self.Tree = prune_tree(self.Tree, SS)
        self.Tree = {}

        start = time.time()

        SS_h = game.hash() # hash of the starting state

        self.root_node = Node(SS, None)
        
        self.Tree[SS_h] = self.root_node
        self.Tree[SS_h].n_visits += 1

        for _ in range(self.I):
            end = time.time()
            if end - start > MAX_MOVE_TIME:
                break
            
            curr_node = SS.clone()

            while len(self.Tree[curr_node.hash()].ea) and \
                len(self.Tree[curr_node.hash()].nea) == 0:

                N = self.Tree[curr_node.hash()].n_visits
                    
                for action, state in self.Tree[curr_node.hash()].ea:
                    
                    n = self.Tree[state].n_visits
                    w = self.Tree[state].n_wins

                    self.Tree[state].ucb = w/n + self.C * np.sqrt(np.log(N)/n)                    
                
                best_idx = np.argmax([self.Tree[s].ucb for _, s in self.Tree[curr_node.hash()].ea])
                
                action, state = self.Tree[curr_node.hash()].ea[best_idx]
                
                self.pi_t[curr_node.hash()] = action
                
                self.Tree[curr_node.hash()].n_visits += 1
                curr_node.make_move(self.pi_t[curr_node.hash()])

            Sp = curr_node.clone()
            Sp_h = Sp.hash()
                
            if curr_node.terminal() == False:
                # choose random actions from state 'Sp'       
                action = np.random.randint(0, len(self.Tree[Sp_h].nea))
                move = self.Tree[Sp_h].nea[action]
                Sp.make_move(move)
                self.Tree[Sp_h].ea.append((move, Sp.hash()))
                self.Tree[Sp_h].nea.pop(action)  
                        
                Sp_h = Sp.hash()            
   
            # new state that we add to the global tree
            Snew = Sp.clone()
            Snew_h = deepcopy(Sp_h)
        
            if Snew_h not in self.Tree.keys():
                self.Tree[Snew_h] = Node(game=Snew, parent=curr_node.hash())
            self.Tree[Snew_h].n_visits += 1
            
            while Sp.terminal() is False:
                moves = Sp.get_available_moves()
                action = np.random.randint(0, len(moves))
                Sp.make_move(moves[action])
            r = np.maximum(Sp.rewards(), [0,0])

            # backpropagate until visit starting state
            while Snew_h != SS_h:

                self.Tree[Snew_h].n_wins += r[(self.Tree[Snew_h].turn) % 2]            

                Snew_h = self.Tree[Snew_h].parent

                best_idx = np.argmax([self.Tree[s[1]].n_wins / self.Tree[s[1]].n_visits for s in self.Tree[Snew_h].ea])                
                self.pi_t[Snew_h] = self.Tree[Snew_h].ea[best_idx][0]                  
        
        return self.pi_t[SS_h]