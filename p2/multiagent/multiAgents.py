# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util
import math

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]
    
    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.
        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.
        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.
        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFoods = [food for food in successorGameState.getFood().asList()]
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        totalScore = successorGameState.getScore()
        closestGhost = util.manhattanDistance(newPos, newGhostStates[0].getPosition())
        closestFood = min(util.manhattanDistance(newPos, food) for food in newFoods) if newFoods else 0
        
        # total score need to minus the length of the list of remaining food(it's bad to waste food)
        totalScore -= len(newFoods)
        
        # nextPos  near the ghost(be eaten)
        totalScore -= 1/closestGhost if closestGhost > 0 else 0

        # nextPos near the dot(can eat)
        totalScore += 10/closestFood if closestFood > 0 else 0

        # addtional score for eating power pellets(it's good to let ghosts be scary)
        for newScaredTime in newScaredTimes:
            totalScore += newScaredTime

        return totalScore
        

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"

        maxValue = -math.inf
        maxAction = ''
        for action in gameState.getLegalActions(0):
            nextState = gameState.generateSuccessor(0, action)
            nextValue = self.getValue(nextState, 0 ,1)
            if nextValue > maxValue:
                maxValue = nextValue
                maxAction = action
        return maxAction
        
    def getValue(self, gameState, currentDepth, agentIndex):
        if gameState.isWin() or gameState.isLose() or currentDepth == self.depth:
            return self.evaluationFunction(gameState)
        # max's turn(pacman)
        elif agentIndex == 0:
            return self.maxValue(gameState, currentDepth)
        # mins' turn(ghosts)
        else:
            return self.minValue(gameState, currentDepth, agentIndex)

    def maxValue(self, gameState, currentDepth):
        v = -math.inf
        for action in gameState.getLegalActions(0):
            v = max(v, self.getValue(gameState.generateSuccessor(0, action), currentDepth, 1))
        return v

    def minValue(self, gameState, currentDepth, ghostIndex):
        v = math.inf
        for action in gameState.getLegalActions(ghostIndex):
            # the last ghost's turn, increse depth
            if ghostIndex == gameState.getNumAgents()-1:
                v = min(v, self.getValue(gameState.generateSuccessor(ghostIndex, action), currentDepth + 1, 0))
            # pass to next ghost's turn
            else:
                v = min(v, self.getValue(gameState.generateSuccessor(ghostIndex, action), currentDepth, ghostIndex +1))
        return v

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        maxValue = -math.inf
        a = -math.inf
        b = math.inf
        maxAction = ''
        for action in gameState.getLegalActions(0):
            nextState = gameState.generateSuccessor(0, action)
            nextValue = self.getValue(nextState, 0 ,1, a, b)
            if nextValue > maxValue:
                maxValue = nextValue
                maxAction = action
            a = max(a, maxValue)
        return maxAction
        
    def getValue(self, gameState, currentDepth, agentIndex, a, b):
        if gameState.isWin() or gameState.isLose() or currentDepth == self.depth:
            return self.evaluationFunction(gameState)
        # max's turn(pacman)
        elif agentIndex == 0:
            return self.maxValue(gameState, currentDepth, a, b)
        # mins' turn(ghosts)
        else:
            return self.minValue(gameState, currentDepth, agentIndex, a, b)

    def maxValue(self, gameState, currentDepth, a, b):
        v = -math.inf
        for action in gameState.getLegalActions(0):
            v = max(v, self.getValue(gameState.generateSuccessor(0, action), currentDepth, 1, a, b))
            if(v > b):
                return v
            a = max(a, v)
        return v

    def minValue(self, gameState, currentDepth, ghostIndex, a, b):
        v = math.inf
        for action in gameState.getLegalActions(ghostIndex):
            # the last ghost's turn, increse depth
            if ghostIndex == gameState.getNumAgents()-1:
                v = min(v, self.getValue(gameState.generateSuccessor(ghostIndex, action), currentDepth + 1, 0, a, b))
            # pass to next ghost's turn
            else:
                v = min(v, self.getValue(gameState.generateSuccessor(ghostIndex, action), currentDepth, ghostIndex + 1, a, b))
            if(v < a):
                return v
            b = min(b, v)
        return v
        
class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        
        maxValue = -math.inf
        maxAction = ''
        for action in gameState.getLegalActions(0):
            nextState = gameState.generateSuccessor(0, action)
            nextValue = self.getValue(nextState, 0 ,1)
            if nextValue > maxValue:
                maxValue = nextValue
                maxAction = action
        return maxAction
        
    def getValue(self, gameState, currentDepth, agentIndex):
        if gameState.isWin() or gameState.isLose() or currentDepth == self.depth:
            return self.evaluationFunction(gameState)
        # max's turn(pacman)
        elif agentIndex == 0:
            return self.maxValue(gameState, currentDepth)
        # mins' turn(ghosts)
        else:
            return self.uniformValue(gameState, currentDepth, agentIndex)

    def maxValue(self, gameState, currentDepth):
        v = -math.inf
        for action in gameState.getLegalActions(0):
            v = max(v, self.getValue(gameState.generateSuccessor(0, action), currentDepth, 1))
        return v

    # "uniformly at random"
    def uniformValue(self, gameState, currentDepth, ghostIndex):
        probability = 1 / len(gameState.getLegalActions(ghostIndex))
        v = 0
        for action in gameState.getLegalActions(ghostIndex):
            # the last ghost's turn, increse depth
            if ghostIndex == gameState.getNumAgents()-1:
                v += self.getValue(gameState.generateSuccessor(ghostIndex, action), currentDepth + 1, 0) * probability
            # pass to next ghost's turn
            else:
                v += self.getValue(gameState.generateSuccessor(ghostIndex, action), currentDepth, ghostIndex + 1) * probability
        return v

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
