import time
import game
import agent, random, aiAgents
import numpy as np
import cPickle as pickle

NUM=0

def saveGames(gameData,fileNum):
    feats = np.hstack(gameData['feats'])
    info = np.vstack([np.array(gameData['winners']), np.array(gameData['length'])]).T
    featId = open('gameData/gameFeats.%d.%d'%(NUM,fileNum),'w')
    infoId = open('gameData/gameInfo.%d.%d'%(NUM,fileNum),'w')
    feats.astype(np.float32).tofile(featId)
    featId.close()
    info.astype(np.int32).tofile(infoId)
    infoId.close()

# This function trains an agent and outputs the network weights
# weighss = [ First layer weights matrix, Second layer weights vector]
def train(numGames=100000):
#def train(numGames=10):
    alpha = 1.0
    lamda = 1
    numFeats = (game.NUMCOLS*4+3)*2
    numHidden = 50
    scales = [np.sqrt(6./(numFeats+numHidden)), np.sqrt(6./(1+numHidden))]
    weights = [scales[0]*np.random.randn(numHidden,numFeats),scales[1]*np.random.randn(1,numHidden),
               np.zeros((numHidden,1)),np.zeros((1,1))]
    players = [aiAgents.TDAgent(game.Game.TOKENS[0],weights),
               aiAgents.TDAgent(game.Game.TOKENS[1],weights)]

    gameData = {'winners':[],'length':[],'feats':[]}
    for it in xrange(numGames):
        g = game.Game(game.LAYOUT)
        g.new_game()
        playernum = random.randint(0,1)
        featsP = aiAgents.extractFeatures((g,players[playernum].player))
        if it==500:
            alpha=.1

        over = False
        nt = 0
        while True:
            roll = (random.randint(1,g.die), random.randint(1,g.die))
            # Si le deuxieme joueur joue on inverse l'odre des positions
            if playernum:
                g.reverse()
            # On calcule les mouvements possibles "moves"
            moves = g.getActions(roll,g.players[0],nodups=True)
            # S'il y a des mouvement possibles, le joueur en choisit un
            # mouvement
            if moves:
                move = players[playernum].getAction(moves,g)
            else:
                move = None
            # S'il y a eu un mouvement l'objet game g applique les changements
            # associes a ce mouvement
            if move:
                g.takeAction(move,g.players[0])
            # Si c'est le deuxieme joueur qui a joue, alors on inverse encore une
            # fois l'ordre des positions
            if playernum:
                g.reverse()
            # maintenant on change de joueur
            playernum = (playernum+1)%2
            # Lire les nouvelles features
            featsN = aiAgents.extractFeatures((g,players[playernum].player))
            # Mettre a jour les poids "weights" selon le changement de features featsP
            # et featsN
            updateWeights(featsP,featsN,weights,lamda,alpha)
            # Sortir de la boucle si la partie est finie
            if g.is_over():
                break
            # !!!!
            nt += 1
            # Mise a jour des features
            featsP = featsN

        winner = g.winner()
        gameData['feats'].append(featsP)
        gameData['winners'].append(winner)
        gameData['length'].append(nt)
        # Si le nombre de parties jouee est multiple de 10000 !?
        # Enregister les donnees relatives au jeu
        #if (it+1)%10000==0:
        saveGames(gameData,it)
        gameData = {'winners':[],'length':[],'feats':[]}
        print "Game : %d/%d in %d turns"%(it,numGames,nt)
        updateWeights(featsP,featsN,weights,alpha,lamda,w=winner)

        #if it%10000 == 0:
        # save weights
        #fid = open("weights%d.bin"%NUM,'w')
        fid = open("weightsHistory/weights%d.bin"%it,'w')
        pickle.dump(weights,fid)
        fid.close()

    fid = open("weights.bin",'w')
    pickle.dump(weights,fid)
    return weights

def backprop(weights,a1,fpropOnly=False):
    w1,w2,b1,b2 = weights

    a2 = 1/(1+np.exp(-(w1.dot(a1)+b1)))
    v = 1/(1+np.exp(-(w2.dot(a2)+b2)))

    if fpropOnly:
        return v

    del2 = v*(1-v)
    del1 = w2.T*del2*a2*(1-a2)
    return v,[del1*a1.T,del2*a2.T,del1,del2]

def updateWeights(featsP,featsN,weights,alpha,lamda,w=None):
    # compute vals and grad
    e = [np.zeros((50,198)),np.zeros ((1,50))]

    vP,grad = backprop(weights,featsP)

    #print grad[0].shape
    #print grad[1].shape
    if w is None:
        vN = backprop(weights,featsN,fpropOnly=True)
    else:
        vN = w
    
    e[0] = lamda * e[0]  + grad[0]
    e [1] = lamda * e[1]  + grad[1]
 
    #print e1.shape
    #print e2.shape
    #print type(e1)

    et = np.append(e[0],e[1])

    scale = alpha*(vN-vP)
    for w,e in zip(weights,e):
        w += scale*e
def load_weights(weights):
    if weights is None:
        try:
            import pickle
            weights = pickle.load(open('weights.bin','r'))
        except IOError:
            print "You need to train the weights to use the better evaluation function"
    return weights

if __name__=="__main__":
    weights = train()

