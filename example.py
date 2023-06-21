from src.agent import MCTSAgent
from src.game import TicTacGame

def main():
    
    game = TicTacGame(1)
    
    agent_cirlce = MCTSAgent()
    agent_cross = MCTSAgent()
    
    it = 0
    
    while game.terminal() == False:
        
        if it % 2 == 0:
            action = agent_cirlce.step(game)
        else:
            action = agent_cross.step(game)
        
        game.make_move(action)
        print(game)
        it += 1

    print(game.rewards())
    
if __name__ == "__main__":
    
    main()