import time
import game
import agent, random, aiAgents
import numpy as np
import cPickle as pickle
from game import Game

#g = game.Game()  # get an instance of the class

def play(players):
    g = game.Game(game.LAYOUT)
    g.new_game()
    g.playe(players, draw=True)


def test(players,numGames=100,draw=False):
    winners = [0,0]
    for _ in xrange(numGames):
        g = game.Game(game.LAYOUT)
        winner = run_game(players,g,draw)
        print "The winner is : Player %s"%players[not winner].player
        winners[not winner]+=1
        if draw:
            g.draw()
            time.sleep(10)
    print "Summary:"
    print "Player %s : %d/%d"%(players[0].player,winners[0],sum(winners))
    print "Player %s : %d/%d"%(players[1].player,winners[1],sum(winners))

def run_game(players,g,draw=False):
    g.new_game()
    playernum = random.randint(0,1)
    over = False
    while not over:
        roll = roll_dice(g)
        if draw:
            g.draw(roll)
        playernum = (playernum+1)%2
        if playernum:
            g.reverse()
        turn(players[playernum],g,roll,draw)
        if playernum:
            g.reverse()
        over = g.is_over()
        if draw:
            time.sleep(.02)
    return g.winner()

def turn(player,g,roll,draw=False):
    if draw:
        print "Player %s rolled <%d,%d>."%(player.player,roll[0],roll[1])
    moves = g.getActions(roll,g.players[0],nodups=True)
    if moves:
        move = player.getAction(moves,g)
    else:
        move = None
    if move:
        g.takeAction(move,g.players[0])

def roll_dice(g):
    return (random.randint(1,g.die), random.randint(1,g.die))

def load_weights(weights):
    if weights is None:
        try:
            import pickle
            weights = pickle.load(open('weights.bin','r'))
        except IOError:
            print "You need to train the weights to use the better evaluation function"
    return weights

def main(args=None):
    from optparse import OptionParser
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t","--train", dest="train",action="store_true",
                      default=False,help="Train TD Player")
    parser.add_option("-d","--draw",dest="draw",action="store_true",default=False,
                      help="Draw game")
    parser.add_option("-n","--num",dest="numgames",default=1,help="Num games to play")
    parser.add_option("-p","--player1",dest="player1",
                      default="human",help="Choose type of first player")
    parser.add_option("-e","--eval",dest="eval",action="store_true",default=True,
                        help="Play with the better eval function for player")

    (opts,args) = parser.parse_args(args)    

    weights = None

    if opts.train:
        weights = train()
        
    if opts.eval:
        weights = load_weights(weights)
        evalArgs = weights
        evalFn = aiAgents.nnetEval
        
    p1 = None
    if opts.player1 == 'random':
        p1 = agent.RandomAgent(game.Game.TOKENS[0])
    elif opts.player1 == 'reflex':
        p1 = aiAgents.TDAgent(game.Game.TOKENS[0],evalArgs)
    elif opts.player1 == 'expectimax':
        p1 = aiAgents.ExpectimaxAgent(game.Game.TOKENS[0],evalFn,evalArgs)
    elif opts.player1 == 'expectiminimax':
        p1 = aiAgents.ExpectiMiniMaxAsgent(game.Game.TOKENS[0],evalFn,evalArgs)
    elif opts.player1 == 'human':
        p1 = agent.HumanAgent(game.Game.TOKENS[0])

    p2=aiAgents.TDAgent(game.Game.TOKENS[1],evalArgs)
#    p2 = aiAgents.ExpectiMiniMaxAgent(game.Game.TOKENS[1],evalFn,evalArgs)
    if p1 is None:
        print "Please specify legitimate player"
        import sys
        sys.exit(1)

    else:
        play([p1,p2])
    #else:
        #test([p1,p2],numGames=int(opts.numgames),draw=opts.draw)

if __name__=="__main__":
    main()
