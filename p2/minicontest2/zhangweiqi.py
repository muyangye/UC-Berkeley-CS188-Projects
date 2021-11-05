# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from game import Agent
import math
from util import nearestPoint

MAXDEPTH = 3
DEFEND = 0

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'InvadeAgent', second = 'DefendAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
"""
可以选择myteam：
如果选红队：python capture.py -r myTeam
如果选蓝队：python capture.py -b myTeam
如果不指定的话，那么两边用的都是同一个算法，就会平局
"""
class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
  DEFEND = 0

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    #CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start, pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

    #return random.choice(actions)


  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)

    # previousObservation = self.getPreviousObservation()
    # if previousObservation:
    #   if previousObservation.getAgentPosition(self.index) == gameState.getAgentPosition(self.index):
    #     print("I am Agnet:", self.index, "I am at: ", gameState.getAgentPosition(self.index), " score:", features * weights)
    #     print(features)
    #     print('action', action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """


    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = successor
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def amIinEnemyRegion(self, gameState):
    pos = gameState.getAgentPosition(self.index)
    if gameState.isOnRedTeam(self.index) and not gameState.isRed(pos):
      return True
    elif gameState.isOnRedTeam(self.index) and gameState.isRed(pos):
      return False
    elif not gameState.isOnRedTeam(self.index) and gameState.isRed(pos):
      return True
    elif not gameState.isOnRedTeam(self.index) and not gameState.isRed(pos):
      return False

  def isThisGuyAGhost(self, gameState, index):
    ghostList = []
    if gameState.isOnRedTeam(self.index):
      enemyList = gameState.getBlueTeamIndices()
      for enemy in enemyList:
        if not gameState.isRed(gameState.getAgentPosition(enemy)):
          ghostList.append(enemy)
    else:
      enemyList = gameState.getRedTeamIndices()
      for enemy in enemyList:
        if gameState.isRed((gameState.getAgentPosition(enemy))):
          ghostList.append(enemy)

    return index in ghostList


class InvadeAgent(DummyAgent):

  def __init__(self, index, timeForComputing = .1):
    # Agent index for querying state
    self.index = index

    # Whether or not you're on the red team
    self.red = None

    # Agent objects controlling you and your teammates
    self.agentsOnTeam = None

    # Maze distance calculator
    self.distancer = None

    # A history of observations
    self.observationHistory = []

    # Time to spend each turn on computing maze distances
    self.timeForComputing = timeForComputing

    # Access to the graphics
    self.display = None
    self.pastIsinEnemyRegion = True       # for initialization
    self.currentIsinEnemyRegion = False
    self.mode = "ChooseInvadePositionAgent"
    self.init = True

  def chooseAction(self, gameState):
    # print(self.mode)

    self.currentIsinEnemyRegion = self.amIinEnemyRegion(gameState)

    ghostList = self.getOpponents(gameState)
    trueGhostList = []
    for ghost in ghostList:
      if self.isThisGuyAGhost(gameState, ghost) != False \
              and gameState.getAgentState(ghost).scaredTimer == 0:
        trueGhostList.append(ghost)

    if not trueGhostList: minGhostDistance = 10
    else:
      minGhostDistance = min(
      [self.getMazeDistance(gameState.getAgentPosition(self.index), gameState.getAgentPosition(ghost)) for ghost in
       trueGhostList])

    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]


    if self.mode == "ChooseInvadePositionAgent":
      if invaders:
        self.mode = "DefensiveReflexAgent"
        self.init = True
        return self.chooseAction(gameState)
      if self.currentIsinEnemyRegion:
        self.mode = "AlphaBetaAgent"
        self.init = True
        return self.chooseAction(gameState)
      if self.init == True:
        self.Agent = ChooseInvadePositionAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.init = False
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      if action == Directions.STOP:
        self.mode = "AlphaBetaAgent"
        self.init = True
        return self.chooseAction(gameState)
      return action

    if self.mode == "AlphaBetaAgent":
      if self.pastIsinEnemyRegion == True and self.currentIsinEnemyRegion == False:
        if gameState.getAgentPosition(self.index) == gameState.getInitialAgentPosition(self.index):
          self.mode = "ChooseInvadePositionAgent"
          self.init = True
          return self.chooseAction(gameState)
        elif minGhostDistance <= 5:
          self.mode = "gotoAnotherPlaceAgent"
          self.init = True
          return self.chooseAction(gameState)
      elif gameState.getAgentState(self.index).numCarrying > min(minGhostDistance - 4, 10) \
              or gameState.data.timeleft < 200 and gameState.getAgentState(self.index).numCarrying != 0:
        self.mode = "goHomeAgent"
        self.init = True
        return self.chooseAction(gameState)
      if self.init == True:
        self.Agent = AlphaBetaAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.init = False
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      return action

    if self.mode == "gotoAnotherPlaceAgent":
      if invaders:
        self.mode = "DefensiveReflexAgent"
        self.init = True
        return self.chooseAction(gameState)
      elif minGhostDistance > 10 and not invaders:
        self.mode = "AlphaBetaAgent"
        self.init = True
        return self.chooseAction(gameState)
      if self.init == True:
        self.Agent = gotoAnotherPlaceAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.init = False
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      return action

    if self.mode == "DefensiveReflexAgent":
      if not invaders:
        self.mode = "gotoAnotherPlaceAgent"
        self.init = True
        return self.chooseAction(gameState)
      if self.init == True:
        self.Agent = gotoAnotherPlaceAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.init = False
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      return action

    if self.mode == "goHomeAgent":
      if not self.amIinEnemyRegion(gameState):
        self.mode = "gotoAnotherPlaceAgent"
        self.init = True
        return self.chooseAction(gameState)
      if self.init == True:
        self.Agent = goHomeAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.init = False
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      return action


class DefendAgent(DummyAgent):

  def __init__(self, index, timeForComputing = .1):
    # Agent index for querying state
    self.index = index

    # Whether or not you're on the red team
    self.red = None

    # Agent objects controlling you and your teammates
    self.agentsOnTeam = None

    # Maze distance calculator
    self.distancer = None

    # A history of observations
    self.observationHistory = []

    # Time to spend each turn on computing maze distances
    self.timeForComputing = timeForComputing

    # Access to the graphics
    self.display = None
    self.pastIsinEnemyRegion = True       # for initialization
    self.currentIsinEnemyRegion = False
    self.mode = "DefensiveReflexAgent"
    self.init = True

  def chooseAction(self, gameState):
    print(self.mode)

    self.currentIsinEnemyRegion = self.amIinEnemyRegion(gameState)
    myPos = gameState.getAgentPosition(self.index)
    width = self.getFood(gameState).width
    ghostList = self.getOpponents(gameState)
    for ghost in ghostList:
      if self.isThisGuyAGhost(gameState, ghost) == False:
        ghostList.remove(ghost)
      if not ghostList: minGhostDistance = 10
      else:
        minGhostDistance = min(
      [self.getMazeDistance(gameState.getAgentPosition(self.index), gameState.getAgentPosition(ghost)) for ghost in
       ghostList])

    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]

    if self.mode == "DefensiveReflexAgent":
      if not invaders and minGhostDistance  > 2 :
        self.mode = "LureAgent"
        self.init = True
        return self.chooseAction(gameState)
      if self.init == True:
        self.Agent = DefensiveReflexAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.init = False
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      return action

    if self.mode == "LureAgent":
      if invaders:
        self.mode = "DefensiveReflexAgent"
        self.init = True
        return self.chooseAction(gameState)
      if self.init == True:
        self.Agent = LureAgent(self.index)
        self.Agent.registerInitialState(gameState)
        self.init = False
      action = self.Agent.getAction(gameState)
      self.pastIsinEnemyRegion = self.currentIsinEnemyRegion
      return action


class gotoAnotherPlaceAgent(DummyAgent):


  def getFeatures(self, gameState, action):

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    height = gameState.data.layout.height
    width = gameState.data.layout.width
    actionList = gameState.getLegalActions(self.index)
    #
    # if myPos >= height // 2:
    #   features['yaxis'] = height-

    enemyIndex = self.getOpponents(successor)
    newGhostStates = []
    for index in enemyIndex:
      ghost = successor.getAgentState(index)
      if self.isThisGuyAGhost(successor, index):
        if ghost.scaredTimer < 5:
          newGhostStates.append(successor.getAgentState(index))

    if len(newGhostStates) > 0:
      minGhostDistance = min([self.getMazeDistance(myPos, ghost.getPosition()) for ghost in newGhostStates])
    else:
      minGhostDistance = 10

    features["minGhostDist"] = -1/minGhostDistance

    # Computes distance to invaders we can see

    if action == Directions.STOP: features['stop'] = 1
    if action == Directions.NORTH or action == Directions.SOUTH: features['UpDown'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    width = gameState.getWalls().width
    height = gameState.getWalls().height
    wallMatrix = gameState.getWalls()
    borderList = []
    for i in range(height):
      if not wallMatrix[width // 2][i] == True:
        borderList.append((width // 2, i))
    myPos = successor.getAgentState(self.index).getPosition()
    # if abs(myPos[0]-width//2) > 2:
    #   minDistance = min([self.getMazeDistance(myPos, border) for border in borderList])
    #   features['borderDist'] = -minDistance
    # else:
    #   features['borderDist'] = 0

    return features


  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -60, 'stop': -100, 'UpDown': 0, 'reverse': -2, 'borderDist': 0, 'minGhostDist': 100}


  def getAction(self, gameState):
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    return random.choice(bestActions)


class goHomeAgent(InvadeAgent):
  def minimaxTree_node(self, gameState, k, maxDepth, parrentNode, alpha, beta):
    n = gameState.getNumAgents()
    depth = k // n + 1

    if not depth == 1 and gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index) \
            or gameState.isOver() \
            or depth > maxDepth and k % n == self.index:
      return self.evaluate_invade(gameState, k)

    agentIndex = k % n
    actionList = gameState.getLegalActions(agentIndex)

    if agentIndex == self.index:  # pacman
      maxscore = -math.inf
      for action in actionList:
        nextState = gameState.generateSuccessor(agentIndex, action)
        # print("pacman action: ", action, "pacman position: ", gameState.getPacmanPosition())

        thisActionTreeNode = [[action], [], ['pacman']]
        score = self.minimaxTree_node(nextState, k + 1, maxDepth, thisActionTreeNode, alpha, beta)
        maxscore = max(score, maxscore)
        thisActionTreeNode[0].append(score)  # [[action, score], []]
        parrentNode[1].append(thisActionTreeNode)
      return maxscore
    elif self.isThisGuyAGhost(gameState, agentIndex):  # ghost
      pacman_Position = gameState.getAgentPosition(self.index)
      ghostPositions = []
      ghostActions = []
      for action in actionList:
        nextState = gameState.generateSuccessor(agentIndex, action)
        ghostPositions.append(nextState.getAgentPosition(agentIndex))  # [Position, Action]
        ghostActions.append(action)
        # if ghostPositions == gameState.getInitialAgentPosition(agentIndex):
        #

      distList = [manhattanDistance(pacman_Position, ghost) for ghost in ghostPositions]

      ## Pacman die

      minDistance = min(distList)
      greedyIndex = distList.index(minDistance)
      greedyAction = ghostActions[greedyIndex]
      nextState = gameState.generateSuccessor(agentIndex, ghostActions[greedyIndex])
      thisActionTreeNode = [[greedyAction], [], ['ghost']]
      score = self.minimaxTree_node(nextState, k + 1, maxDepth, thisActionTreeNode, alpha, beta)

      thisActionTreeNode[0].append(score)  # [[action, score], []]
      parrentNode[1].append(thisActionTreeNode)
      return score
    else:
      return self.minimaxTree_node(gameState, k + 1, maxDepth, parrentNode, alpha, beta)

  def findPacmanPath(self, gameState, treeNode, maxDepth, k, actions):
    n = gameState.getNumAgents()
    goDeep = k // n
    if goDeep > maxDepth:
      return
    if not treeNode[1]: return
    if treeNode[2][0]=='pacman':
      maxScore = - math.inf
      for i in range(len(treeNode[1])):
        if treeNode[1][i][0][1] > maxScore:
          maxScore = treeNode[1][i][0][
            1]  # [1]: child node list, [i]: ith child node, [0]: child node action and score, [1]: child node score
          action = treeNode[1][i][0][0]
          index = i
      actions.append(action)
    elif treeNode[2][0]=='ghost':

      index = 0
      #
      # minScore = math.inf
      # for i in range(len(treeNode[1])):
      #   if treeNode[1][i][0][1] < minScore:
      #     minScore = treeNode[1][i][0][1]
      #     index = i
    self.findPacmanPath(gameState, treeNode[1][index], maxDepth, k + 1, actions)

  def getAction(self, gameState):
    """
    Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    myPos = gameState.getAgentPosition(self.index)
    ghostList = self.getOpponents(gameState)
    for ghost in ghostList:
      if self.isThisGuyAGhost(gameState, ghost) == False:
        ghostList.remove(ghost)
    minGhostDistance = min([self.getMazeDistance(myPos, gameState.getAgentPosition(ghost)) for ghost in ghostList])
    if minGhostDistance > 5:
      maxDepth = 1
    else:
      maxDepth = 1

    tree = [["first"], [], ['pacman']]
    finalscore = self.minimaxTree_node(gameState, self.index, maxDepth, tree, -math.inf, math.inf)

    actions = []
    self.findPacmanPath(gameState, tree, maxDepth, 0, actions)

    return actions[0]

  def getWeights(self, gameState):
    return {'distanceToHome': 100, 'rDistanceToGhost': 50, 'getEaten': 10000, 'IamHome!!': 10000, 'goHomeTime': 100,\
            'distanceToCapsule': 150, 'goToEatCapsule':10000}


  def getFeatures(self, gameState, k):

    features = util.Counter()
    borderList = []
    wallMatrix = gameState.getWalls()
    height = gameState.data.layout.height
    width = gameState.data.layout.width

    if not self.amIinEnemyRegion(gameState):
      features['IamHome!!'] = 1
    else:
      features['IamHome!!'] = 0

    features['goHomeTime'] = -k

    if self.red: width -= 1
    for i in range(height):
      if not wallMatrix[width // 2][i] == True:
        borderList.append((width // 2, i))
    myPos = gameState.getAgentState(self.index).getPosition()
    minDistance = min([self.getMazeDistance(myPos, border) for border in borderList])
    features['distanceToHome'] = -minDistance

    enemyIndex = self.getOpponents(gameState)
    newGhostStates = []
    for index in enemyIndex:
      ghost = gameState.getAgentState(index)
      if self.isThisGuyAGhost(gameState, index):
        if ghost.scaredTimer < 5:
          newGhostStates.append(gameState.getAgentState(index))

    if len(newGhostStates) > 0:
      minGhostDistance = min([self.getMazeDistance(myPos, ghost.getPosition()) for ghost in newGhostStates])
    else:
      minGhostDistance = 1

    if gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index):
      features['getEaten'] = -1
    else:
      features['getEaten'] = 0
    features['rDistanceToGhost'] = - 1 / minGhostDistance

    capsulesList = self.getCapsules(gameState)
    if len(capsulesList) > 0:
      minCapsuleDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsulesList])
      features['distanceToCapsule'] = -minCapsuleDistance
    else:
      features['distanceToCapsule'] = 0
    capsulesList = self.getCapsules(gameState)
    features['goToEatCapsule'] = - len(capsulesList)

    # if len(gameState.getLegalActions(self.index)) == 2:
    #   features['inPit'] = 1
      # features['successorScore'] = self.getScore(successor)

    return features

  def evaluate_invade(self, gameState, k):
    """
    Computes a linear combination of features and feature weights
    """

    ############################
    #cache the score           #
    ############################
    features = self.getFeatures(gameState, k)
    weights = self.getWeights(gameState)

    # previousObservation = self.getPreviousObservation()
    # if previousObservation:
    #   if previousObservation.getAgentPosition(self.index) == gameState.getAgentPosition(self.index):
    #     print("I am Agnet:", self.index, "I am at: ", gameState.getAgentPosition(self.index), " score:", features * weights)
    #     print(features)
    #     print('action', action)
    # if gameState.isRed(gameState.getAgentPosition(self.index)) and not gameState.isOnRedTeam(self.index):
    #   print("I am Agnet:", self.index, "I am at: ", gameState.getAgentPosition(self.index), " score:", features * weights)
    #   print(features)
    return features * weights

class ChooseInvadePositionAgent(InvadeAgent):
  def getAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    enemyIndex = self.getOpponents(successor)
    newGhostStates = []
    for index in enemyIndex:
      ghost = successor.getAgentState(index)
      if self.isThisGuyAGhost(successor, index):

        if ghost.scaredTimer == 0:
          newGhostStates.append(successor.getAgentState(index))

    if newGhostStates:
      minGhostDistance = min([self.getMazeDistance(myPos, ghost.getPosition()) for ghost in newGhostStates])
    else:
      minGhostDistance = 10
    features['rDistanceToGhost'] = - 1/minGhostDistance

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'rDistanceToGhost': 50}

class AlphaBetaAgent(DummyAgent):
  """
  Your minimax agent with alpha-beta pruning (question 3)
  """
  def minimaxTree_node(self, gameState, k, maxDepth, parrentNode, alpha, beta):
    n = gameState.getNumAgents()
    depth = k // n + 1

    if not depth == 1 and gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index) \
            or gameState.isOver() \
            or depth > maxDepth and k % n == self.index:
      return self.evaluate_invade(gameState)

    agentIndex = k % n
    actionList = gameState.getLegalActions(agentIndex)

    if agentIndex == self.index:  # pacman
      maxscore = -math.inf
      for action in actionList:
        nextState = gameState.generateSuccessor(agentIndex, action)
        # print("pacman action: ", action, "pacman position: ", gameState.getPacmanPosition())
        thisActionTreeNode = [[action], [], ['pacman']]
        score = self.minimaxTree_node(nextState, k + 1, maxDepth, thisActionTreeNode, alpha, beta)
        maxscore = max(score, maxscore)
        thisActionTreeNode[0].append(score)  # [[action, score], []]
        parrentNode[1].append(thisActionTreeNode)
      return maxscore
    elif self.isThisGuyAGhost(gameState, agentIndex):  # ghost
      pacman_Position = gameState.getAgentPosition(self.index)
      ghostPositions = []
      ghostActions = []
      for action in actionList:
        nextState = gameState.generateSuccessor(agentIndex, action)
        ghostPositions.append(nextState.getAgentPosition(agentIndex))  # [Position, Action]
        ghostActions.append(action)
        # if ghostPositions == gameState.getInitialAgentPosition(agentIndex):
        #

      distList = [manhattanDistance(pacman_Position, ghost) for ghost in ghostPositions]

      ## Pacman die

      minDistance = min(distList)
      greedyIndex = distList.index(minDistance)
      greedyAction = ghostActions[greedyIndex]
      nextState = gameState.generateSuccessor(agentIndex, ghostActions[greedyIndex])
      thisActionTreeNode = [[greedyAction], [], ['ghost']]
      score = self.minimaxTree_node(nextState, k + 1, maxDepth, thisActionTreeNode, alpha, beta)

      thisActionTreeNode[0].append(score)  # [[action, score], []]
      parrentNode[1].append(thisActionTreeNode)
      return score
    else:
      return self.minimaxTree_node(gameState, k + 1, maxDepth, parrentNode, alpha, beta)

  def findPacmanPath(self, gameState, treeNode, maxDepth, k, actions):
    n = gameState.getNumAgents()
    goDeep = k // n
    if goDeep > maxDepth:
      return
    if not treeNode[1]: return
    if treeNode[2][0]=='pacman':
      maxScore = - math.inf
      for i in range(len(treeNode[1])):
        if treeNode[1][i][0][1] > maxScore:
          maxScore = treeNode[1][i][0][
            1]  # [1]: child node list, [i]: ith child node, [0]: child node action and score, [1]: child node score
          action = treeNode[1][i][0][0]
          index = i
      actions.append(action)
    elif treeNode[2][0]=='ghost':

      index = 0
      #
      # minScore = math.inf
      # for i in range(len(treeNode[1])):
      #   if treeNode[1][i][0][1] < minScore:
      #     minScore = treeNode[1][i][0][1]
      #     index = i
    self.findPacmanPath(gameState, treeNode[1][index], maxDepth, k + 1, actions)

  def getAction(self, gameState):
    """
    Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    myPos = gameState.getAgentPosition(self.index)
    ghostList = self.getOpponents(gameState)
    for ghost in ghostList:
      if self.isThisGuyAGhost(gameState, ghost) == False:
        ghostList.remove(ghost)

    ghostDistList = [self.getMazeDistance(myPos, gameState.getAgentPosition(ghost)) for ghost in ghostList]
    minGhostDistance = min(ghostDistList)
    minDistGhostIndex = ghostDistList.index(minGhostDistance)
    minDistGhost = ghostList[minDistGhostIndex]
    if minGhostDistance > 5:
      maxDepth = 1
    else:
      if gameState.getAgentState(minDistGhost).scaredTimer > 5:
        maxDepth = 1
      else:
        maxDepth = MAXDEPTH


    tree = [["first"], [], ['pacman']]
    finalscore = self.minimaxTree_node(gameState, self.index, maxDepth, tree, -math.inf, math.inf)

    actions = []
    self.findPacmanPath(gameState, tree, maxDepth, 0, actions)

    return actions[0]

  def getWeights(self, gameState):
    return {'successorScore': 500, 'distanceToFood': 10, 'rDistanceToGhost': 50, 'getEaten': 10000, 'distanceToCapsule': 20, \
            'goToEatCapsule': 5000 }

  def getFeatures(self, gameState):
    features = util.Counter()
    foodList = self.getFood(gameState).asList()
    myPos = gameState.getAgentState(self.index).getPosition()
    features['successorScore'] = -len(foodList)  # self.getScore(successor)
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = -minDistance
    else:
      return features

    capsulesList = self.getCapsules(gameState)
    if len(capsulesList) > 0:
      minCapsuleDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsulesList])
      features['distanceToCapsule'] = -minCapsuleDistance
    else:
      features['distanceToCapsule'] = 0
    capsulesList = self.getCapsules(gameState)
    features['goToEatCapsule'] = - len(capsulesList)



    # features["eatGhost"] = -100
    # features["getYou"] = 0
    enemyIndex = self.getOpponents(gameState)
    newGhostStates = []
    for index in enemyIndex:
      ghost = gameState.getAgentState(index)
      if self.isThisGuyAGhost(gameState, index):

        if ghost.scaredTimer == 0:
          newGhostStates.append(gameState.getAgentState(index))

    if newGhostStates:
      minGhostDistance = min([self.getMazeDistance(myPos, ghost.getPosition()) for ghost in newGhostStates])
    else:
      minGhostDistance = 10
    features['rDistanceToGhost'] = - 1 / minGhostDistance

    if gameState.getAgentPosition(self.index)==gameState.getInitialAgentPosition(self.index):
      features['getEaten'] = -1
    else:
      features['getEaten'] = 0




    return features

  def evaluate_invade(self, gameState):
    """
    Computes a linear combination of features and feature weights
    """

    ############################
    #cache the score           #
    ############################
    features = self.getFeatures(gameState)
    weights = self.getWeights(gameState)
    return features * weights

class DefensiveReflexAgent(DummyAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    width = gameState.getWalls().width
    height = gameState.getWalls().height
    wallMatrix = gameState.getWalls()
    borderList = []
    for i in range(height):
      if not wallMatrix[width // 2][i] == True:
        borderList.append((width // 2, i))
    myPos = successor.getAgentState(self.index).getPosition()
    if abs(myPos[0]-width//2) > 2:
      minDistance = min([self.getMazeDistance(myPos, border) for border in borderList])
      features['borderDist'] = -minDistance
    else:
      features['borderDist'] = 0
    # features["borderDist"] = -abs(successor.getAgentPosition(self.index)[0] - width//2)


    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -20, 'borderDist': 0}

class LureAgent(DummyAgent):

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[successor.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    width = gameState.getWalls().width
    height = gameState.getWalls().height
    wallMatrix = gameState.getWalls()
    borderList = []
    if self.red:
      trueWidth = width // 2
    else:
      trueWidth = width // 2 - 1
    for i in range(height):
      if not wallMatrix[trueWidth][i] == True:
        borderList.append((trueWidth, i))
    myPos = successor.getAgentState(self.index).getPosition()
    if abs(myPos[0]-trueWidth) > 1:
      minDistance = min([self.getMazeDistance(myPos, border) for border in borderList])
      features['borderDist'] = -minDistance
    else:
      features['borderDist'] = 0

    if self.amIinEnemyRegion(successor):
      features['luring'] = 1


      enemyIndex = self.getOpponents(successor)
      newGhostStates = []
      for index in enemyIndex:
        ghost = successor.getAgentState(index)
        if self.isThisGuyAGhost(successor, index):

          if ghost.scaredTimer == 0:
            newGhostStates.append(successor.getAgentState(index))

      if newGhostStates:
        minGhostDistance = min([self.getMazeDistance(myPos, ghost.getPosition()) for ghost in newGhostStates])
      else:
        minGhostDistance = 10

      if minGhostDistance <= 1:
        # features['rDistanceToGhost'] = 1 / minGhostDistance
        features['rDistanceToGhost'] = - 1 / minGhostDistance



    else:
      features['luring'] = 0



    if successor.getAgentPosition(self.index)==successor.getInitialAgentPosition(self.index):
      features['getEaten'] = -1
    else:
      features['getEaten'] = 0
    # features["borderDist"] = -abs(successor.getAgentPosition(self.index)[0] - width//2)


    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 0, 'invaderDistance': -10, 'stop': 10, 'reverse': -2, 'borderDist': 30, \
            'getEaten': 10000, 'luring': 500, 'rDistanceToGhost': 100, 'safeHome': 600, 'EAST': 100000, 'WEST': 100000}

  def getAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    myPos = gameState.getAgentState(self.index).getPosition()
    if self.red:
      mySideBorder = gameState.getWalls().width//2-1
    else:
      mySideBorder = gameState.getWalls().width // 2
    if myPos[0]==mySideBorder:
      ghostList = self.getOpponents(gameState)
      trueGhostList = []
      for ghost in ghostList:
        if self.isThisGuyAGhost(gameState, ghost) != False \
                and gameState.getAgentState(ghost).scaredTimer == 0:
          trueGhostList.append(ghost)
      if trueGhostList:
        for ghost in trueGhostList:
          if gameState.getAgentPosition(ghost) == (myPos[0]+1, myPos[1])\
                  or gameState.getAgentPosition(ghost) == (myPos[0]-1, myPos[1]):
            if self.red and Directions.WEST in actions:
              return Directions.WEST
            if not self.red and Directions.EAST in actions:
              return Directions.EAST

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    return random.choice(bestActions)




def manhattanDistance(xy1, xy2):
  "The Manhattan distance heuristic for a PositionSearchProblem"
  return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
