import numpy as np
import json

import constants

class TicTacGame:
    def __init__(self, n_levels):
        super().__init__()
        
        self.n_levels = n_levels
        self.board_width = 3 ** self.n_levels
        self.board_height = 3 ** self.n_levels
        self.__history = []
        self.__turn = Player.CIRLCE
        self.__board = np.zeros((3 ** (self.n_levels), 3 ** (self.n_levels)), dtype=int)
        self.__board_str = None
        self.__term = False
        
        self.__tree = []
        
        self.__rewards = [None, None]
        
        for i in range(self.n_levels):
            self.__tree.append(np.zeros((3 ** (i), 3 ** (i))), dtype=int)
        self.__tree.append(self.__board)
        
        s = ''
        for y in range(self.board_height):
            for x in range(self.board_width):
                s += char_mapper[y][x]
        self.__board_str = s
    
    def get_state(self,):
        str(hash(self.__board_str + str(self.__turn)))
    
    def get_hash_of_state(self,):
        str(hash(self.__board_str + str(self.__turn)))
    
    def reset(self,):
        self.__init__(self.n_levels)
    
    def get_turn(self,):
        return self.__turn
    
    def terminal(self,) -> bool:
        return self.__term
    
    def rewards(self,) -> list:
        score = self.__result()
        return score
    
    def make_move(self, move):
        
        y, x = move
        self.__board[y, x] = self.__turn
        self.__board_str[y * self.board_height + x % self.board_width] = char_mapper[self.__turn]
        self.__history.append(move)
        
        y_origin, x_origin = y // 3, x // 3
        
        decisive = True
        level = self.n_levels
        
        while win and level > 0:
            decisive = False
            y_origin, x_origin = y // 3 ** (level - 1), x // 3 ** (level - 1)
            
            score = self.__hash_score(self.__turn, (y_origin, x_origin), level)
            
            if score is not None:
                decisive = True
                self.__tree[level - 1][y_origin, x_origin] = score
            
            level -= 1
            
        if self.__tree[0][0,0] != Field.Empty:
            self.__term = True
            
            if self.__tree[0][0,0] == Field.Cirlce:
                self.__rewards[Field.Cirlce] = WIN
                self.__rewards[Field.Cross] = LOST
                
            elif self.__tree[0][0,0] == Field.Undecided:
                self.__rewards[Field.Cirlce] = DRAW
                self.__rewards[Field.Cross] = DRAW
            
            else:
                self.__rewards[Field.Cirlce] = LOST
                self.__rewards[Field.Cross] = WIN
            
        
        self.__turn = 1 - self.__turn
    
    def undo_move(self,): 
        
        if len(self.__history) == 0:
            pass
        
        self.__board[self.__history[-1]] = Field.Empty
        self.__board_str[self.__history[-1]] =\
                char_mapper[self.__board_str[self.__history[-1]]]
        self.__history.pop()
        self.__turn = 1 - self.__turn
        
    def print_board(self,):
        for i in range(self.board_height):
            print(self.__board_str[i * self.board_height : (i + 1) * self.board_height])
    
    def __print_comp(self,):
        pass
    
    def __result(self,):
        pass
    
    def __find_next_hash(self,):
        y, x = self.__history[-1]
        y_out = 0
        x_out = 0
        for i in range(n_levels):
            y_out += ((y // (3 ** i)) % 3) * 3 ** (n_levels - 1 - i)
            x_out += ((x // (3 ** i)) % 3) * 3 ** (n_levels - 1 - i)
        
        return [(y, x)]
    
    def get_available_moves(self,) -> list:
        
        available_moves = []
        y_origin, x_origin = self.__find_next_hash()
        
        for i in range(HASH_SIZE):
            for j in range(HASH_SIZE):
                if self.__board[y_origin + i, x_origin + j] == Field.Empty:
                    available_moves.append((y_origin + i, x_origin + j))
                    
        return available_moves
    
    def __hash_score(self, last_to_move, origin, level):
        
        y_origin, x_origin = origin
        
        player = last_to_move
        
        board = self.__tree[level]
        
        for i in range(HASH_SIZE):
            if board[y_origin + i, x_origin : x_origin + HASH_SIZE].all() == player:
                return last_to_move  
            if board[y_origin : y_origin + HASH_SIZE, x_origin + i].all() == player:
                return last_to_move
            
        if board[[(i, i) for i in range(HASH_SIZE)]].all() == player:
            return last_to_move
        
        if board[[(i, HASH_SIZE - i) for i in range(HASH_SIZE)]].all() == player:
            return last_to_move
        
        if board.all() != Field.Empty:
            return Undecided
        
        return None