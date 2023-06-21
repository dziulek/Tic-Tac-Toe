from src import game

class ConsoleAgent:

    def __init__(self) -> None:
        
        pass

    def step(self, game: game.TicTacGame):

        move_y = 0
        move_x = 0

        moves = game.get_available_moves()

        valid = False
        wrong_input = False

        while not valid:

            move_y = 0
            move_x = 0

            for i in range(game.n_levels):
                try:
                    y, x = input("Input row and column of {0}th level: ".format(i)).split(' ')
                    move_y += 3 ** (game.n_levels - i - 1) * int(y.strip())
                    move_x += 3 ** (game.n_levels - i - 1) * int(x.strip())
                    wrong_input = False
                except ValueError:

                    print('You should input only two values:\nthe number of row and column (beginning with zero)')
                    wrong_input = True
                    break

            if wrong_input == True:
                continue

            try:
                idx = moves.index((move_y, move_x))
                valid = True
            except ValueError:
                print("Wrong input ({0}, {1}), try again.".format(move_y, move_x))
                valid = False

        return (move_y, move_x)