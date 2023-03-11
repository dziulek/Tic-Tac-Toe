from copy import deepcopy
# from arcade import has_line_of_sight
from matplotlib.style import available
import numpy as np
import json

from src.constants import Player, char_mapper, Field, HASH_SIZE, WIN, LOSS, DRAW

class TicTacGame:
    def __init__(self, n_levels):
        super().__init__()

        self.n_levels = n_levels
        self.board_width = 3 ** self.n_levels
        self.board_height = 3 ** self.n_levels
        self.__history = []
        self.__turn = Player.CIRLCE.value
        self.__board = np.zeros((3 ** (self.n_levels), 3 ** (self.n_levels)), dtype=int)
        self.__board_str = None
        self.__term = False
        
        self.__tree = []
        
        self.__rewards = [None, None]
        
        for i in range(self.n_levels):
            self.__tree.append(np.zeros((3 ** (i), 3 ** (i)), dtype=int))
        self.__tree.append(self.__board)

        s = [char_mapper[Field.Empty.value] for _ in range(self.board_height * self.board_width)]
        self.__board_str = s
    
    def clone(self,):

        out_game = TicTacGame(self.n_levels)
        out_game.n_levels = self.n_levels
        out_game.board_width = self.board_width
        out_game.board_height = self.board_height
        out_game.__history = deepcopy(self.__history)
        out_game.__turn = self.__turn
        out_game.__board = np.copy(self.__board)
        out_game.__board_str = deepcopy(self.__board_str)
        out_game.__term = self.__term
        out_game.__tree = [np.copy(leaf) for leaf in self.__tree[:-1]]
        out_game.__tree.append(out_game.__board)
        out_game.__rewards = deepcopy(self.__rewards)

        return out_game

    def get_state(self,):        
        return str(hash(''.join(self.__board_str) + str(self.__turn)))
    
    def hash(self,):
        return str(hash(''.join(self.__board_str) + str(self.__turn)))
    
    def reset(self,):
        self.__init__(self.n_levels)
    
    def get_turn(self,):
        return self.__turn
    
    def terminal(self,) -> bool:
        return self.__term
    
    def rewards(self,) -> list:
        return self.__rewards
    
    def make_move(self, move):
        
        y, x = move
        self.__board[y, x] = self.__turn
        self.__board_str[y * self.board_height + x % self.board_width] = char_mapper[self.__turn]
        self.__history.append(move)
        
        decisive = True
        level = self.n_levels
        y_origin, x_origin = y // HASH_SIZE, x // HASH_SIZE
        y_origin, x_origin = y_origin * HASH_SIZE, x_origin * HASH_SIZE  

        while decisive and level > 0:
            decisive = False

            score = self.__hash_score(self.__turn, (y_origin, x_origin), level)
            y_origin //= HASH_SIZE
            x_origin //= HASH_SIZE
            if score is not None:
                decisive = True
                self.__tree[level - 1][y_origin, x_origin] = score
            y_origin = (y_origin // HASH_SIZE) * HASH_SIZE
            x_origin = (x_origin // HASH_SIZE) * HASH_SIZE
            level -= 1

            
        if self.__tree[0][0,0] != Field.Empty.value:
            self.__term = True
            
            if self.__tree[0][0,0] == Field.Cirlce.value:
                self.__rewards[Field.Cirlce.value - 1] = WIN
                self.__rewards[Field.Cross.value - 1] = LOSS
                
            elif self.__tree[0][0,0] == Field.Undecided.value:
                self.__rewards[Field.Cirlce.value - 1] = DRAW
                self.__rewards[Field.Cross.value - 1] = DRAW
            
            else:
                self.__rewards[Field.Cirlce.value - 1] = LOSS
                self.__rewards[Field.Cross.value - 1] = WIN
            
        
        if self.__turn == Player.CIRLCE.value:
            self.__turn = Player.CROSS.value
        else:
            self.__turn = Player.CIRLCE.value
    
    def undo_move(self,): 
        
        if len(self.__history) == 0:
            pass

        y, x = self.__history.pop()
        self.__board[y, x] = Field.Empty.value
        self.__board_str[y * self.board_height + x % self.board_width] = char_mapper[Field.Empty.value]
        

        y_origin, x_origin = y // HASH_SIZE, x // HASH_SIZE
        level = self.n_levels - 1
        
        while level >= 0 and self.__tree[level][y_origin, x_origin] != Field.Empty.value:
            self.__tree[level][y_origin, x_origin] = Field.Empty.value
            level -= 1
            y_origin //= HASH_SIZE
            x_origin //= HASH_SIZE
        
        if self.__tree[0][0,0] == Field.Empty.value:
            self.__rewards = (None, None)

        if self.__turn == Player.CIRLCE.value:
            self.__turn = Player.CROSS.value
        else:
            self.__turn = Player.CIRLCE.value

    def __calculate_bar_len(self, level):
        
        if level == self.n_levels - 1:
            return 1
        if level == self.n_levels - 2:
            return 5
        
        return 3 * self.__calculate_bar_len(level + 1) + 2 * (1 + 2 * (self.n_levels - 2 - level))

    def __assemble_str_repr(self, level_borders, input_arr, level, x, y) -> np.ndarray:
        if level == self.n_levels:
            return np.array([[input_arr[y][x]]])

        bar_len = self.__calculate_bar_len(level)

        b, r, c = level_borders[self.n_levels - 1 - level]

        if level == self.n_levels - 1:
            cross = np.array([[c]], dtype=np.uint8)
            bar = np.ones((bar_len, 1), dtype=np.uint8) * b
            row = np.ones((1, bar_len), dtype=np.uint8) * r
        else:
            sep_width = 2* (self.n_levels - level - 1) + 1
            mid = sep_width//2
            cross = np.zeros((sep_width, sep_width), dtype=np.uint8)
            cross[mid,:] = c
            cross[:,mid] = c
            bar = np.zeros((bar_len, sep_width), dtype=np.uint8)
            row = np.zeros((sep_width, bar_len), dtype=np.uint8)
            bar[:,mid] = b
            row[mid, :] = r
        row = np.concatenate([row, cross, row, cross, row], axis=1)    

        tmp = []
        for i in range(3):
            tmp.append([])        
            for j in range(3):
                tmp[-1].append(self.__assemble_str_repr(level_borders, input_arr, \
                        level + 1, 3 * x + j, 3 * y + i))    

            tmp[-1] = np.concatenate([tmp[-1][0], bar, tmp[-1][1], bar, tmp[-1][2]], axis=1)

        tmp = np.concatenate([tmp[0], row, tmp[1], row, tmp[2]], axis=0)

        if level != 0:
            if self.__tree[level][y][x] == Field.Cirlce.value:
                tmp[:,:] = Field.Cirlce.value
            elif self.__tree[level][y][x] == Field.Cross.value:
                tmp[:,:] = Field.Cross.value

        return tmp
        
        
    def __str__(self,) -> str:

        char_array = self.__board.copy()

        level_borders = [
            [ord('|'), ord('-'), ord('+')],
            [ord('@'), ord('@'), ord('@')],            
            [ord('#'), ord('#'), ord('#')],
            [ord('$'), ord('$'), ord('$')],
        ]
        
        ass_arr = self.__assemble_str_repr(level_borders, self.__board.copy(), 0, 0, 0)
        l_chars = []
        for i in range(ass_arr.shape[0]):
            for j in range(ass_arr.shape[1]):
                if ass_arr[i][j] < 4:
                    l_chars.append(char_mapper[ass_arr[i][j]])
                else:
                    l_chars.append(chr(ass_arr[i][j]))

            l_chars.append('\n')

        return ''.join(l_chars)
        
    
    def __print_comp(self,):
        pass
    
    def __result(self,):
        pass
    
    def __find_next_hash(self,):

        if len(self.__history) == 0 or len(self.__tree) == 2:
            return (None, None)
        

        y, x = self.__history[-1]
        
        y = y % HASH_SIZE
        x = x % HASH_SIZE

        if self.__tree[1][y, x] != Field.Empty.value:
            return (None, None)

        return (y, x)
    
    def __dfs_tree(self, y, x, level, empty_fields_list):

        if self.__tree[level][y, x] != Field.Empty.value:
            return

        if level == self.n_levels:
            empty_fields_list.append((y, x))
            return 
        
        for i in range(HASH_SIZE):
            for j in range(HASH_SIZE):
                self.__dfs_tree(3 * y + i, 3 * x + j, level + 1, empty_fields_list)

    def get_available_moves(self,) -> list:
        
        available_moves = []
        y_origin, x_origin = self.__find_next_hash()

        level = 1

        if y_origin is None:
            level = 0
            y_origin, x_origin = 0, 0

        if self.__term:
            return []


        if len(self.__tree) == 2:

            for i in range(HASH_SIZE):
                for j in range(HASH_SIZE):
                    if self.__board[i,j] == Field.Empty.value:
                        available_moves.append((i, j))
            return available_moves 

        self.__dfs_tree(y_origin, x_origin, level, available_moves)
                    
        return available_moves
    
    def __hash_score(self, last_to_move, origin, level):
        
        y_origin, x_origin = origin
        
        player = last_to_move
        
        board = self.__tree[level]
        
        for i in range(HASH_SIZE):
            if (board[y_origin + i, x_origin : x_origin + HASH_SIZE] == player).all():
                return last_to_move  
            if (board[y_origin : y_origin + HASH_SIZE, x_origin + i] == player).all():
                return last_to_move
            
        if (board[tuple([i for i in range(HASH_SIZE)]), tuple([i for i in range(HASH_SIZE)])] == player).all():
            return last_to_move
        
        if (board[tuple([i for i in range(HASH_SIZE)]), tuple([HASH_SIZE - 1 - i for i in range(HASH_SIZE)])] == player).all():
            return last_to_move
        
        if (board[y_origin : y_origin + HASH_SIZE, x_origin : x_origin + HASH_SIZE] != Field.Empty.value).all():
            return Field.Undecided.value
        
        return None

def main():
    
    game = TicTacGame(1)

    moves = game.get_available_moves()
    it = 0

    while game.terminal() == False:
        it += 1
        moves = game.get_available_moves()
        move = moves[np.random.randint(0, len(moves))]
        game.make_move(move)

    print(game.rewards())
    game.print_board()

    while it > 0:
        it -= 1
        game.undo_move()
    
    print(game.rewards())
    game.print_board()

if __name__ == "__main__":
    main()