from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.numF = 0
    self.limit = 0
    self.de = False
    self.OnumF = 0

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    #print(gameState.data.timeleft)
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invadersP = [a.getPosition() for a in enemies if a.isPacman and a.getPosition() != None]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    actions = gameState.getLegalActions(self.index)
    pos = gameState.getAgentPosition(self.index)
    if self.getPreviousObservation():
      preFood = self.getFood(self.getPreviousObservation())
      if preFood[pos[0]][pos[1]]:
        self.numF += 1
      for ax, ay in invadersP:
        ax, ay = int(ax), int(ay)
        if preFood[ax][ay]:
          self.OnumF += 1
          
    if self.red:
      if pos[0] < gameState.data.layout.width/2:
        self.numF = 0
        self.limit = random.randint(1,3)
      allBack = True
      for ax, ay in invadersP:
        if ax < gameState.data.layout.width/2:
          allBack = False
      if allBack:
        self.OnumF = 0
    if not self.red:
      if pos[0] > gameState.data.layout.width/2:
        self.numF = 0
        self.limit = random.randint(1,3)
      allBack = True
      for ax, ay in invadersP:
        if ax > gameState.data.layout.width/2:
          allBack = False
      if allBack:
        self.OnumF = 0
    foodList = self.getFood(gameState).asList() 
    if len(foodList) > 0: 
      minDistance = min([self.getMazeDistance(pos, food) for food in foodList])
      if minDistance < 5 and self.limit < 10:
        self.limit += 1
    
    if len(ghosts) > 0:
      dists = [self.getMazeDistance(pos, a.getPosition()) for a in ghosts]
      if (min(dists) < 10 and ghosts[dists.index(min(dists))].scaredTimer < 5) or gameState.data.timeleft < 150:
        self.limit = 0
        if min(dists) < 4:
          self.de = True
      if min(dists) > 7:
        self.de = False
    if self.OnumF >= 7:
      self.de = True
    if self.getScore(gameState) > 10:
      self.de = True
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
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def onOtherSide(self, gameState):
    return (self.red and gameState.getAgentPosition(self.index)[0] > gameState.data.layout.width/2-3) or (not self.red and gameState.getAgentPosition(self.index)[0] < gameState.data.layout.width/2+3)
  def aheadPos(self, a, successor):
    ix, iy = a.getPosition()
    dVector = {"North":(ix, iy-2), "South":(ix, iy+2), "West":(ix-2, iy), "East":(ix+2, iy)}
    desX, desY = dVector[a.getDirection()]
    desX, desY = int(desX), int(desY)
    iternum = 0
    while not (0<=desX<successor.data.layout.width and 0<=desY<successor.data.layout.height) or successor.hasWall(desX, desY):
        (desX, desY) = random.choice([(desX-1, desY), (desX, desY+1), (desX, desY-1), (desX+1, desY)])
        iternum += 1
        if iternum > 20:
          desX, desY = ix, iy
          break
    return (desX, desY)

    
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    if self.de:
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)

      myState = successor.getAgentState(self.index)
      myPos = myState.getPosition()
      
      # Computes whether we're on defense (1) or offense (0)
      features['OonDefense'] = 1
      if myState.isPacman: features['OonDefense'] = 0

      # Computes distance to invaders we can see
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      inAhead = [self.aheadPos(a, successor) for a in invaders]
      features['OnumInvaders'] = len(invaders)
      if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        aheadDists = [self.getMazeDistance(myPos, a) for a in inAhead]
        if min(dists) < 5:
          features['OinvaderDistance'] = min(dists)
        else:
          features['OinvaderDistance'] = min(aheadDists)
        #self.debugDraw(inAhead, [1,0,1], clear=True)
        if gameState.getAgentState(self.index).scaredTimer > 5:
          features['OinvaderDistance'] = -features['OinvaderDistance']

      if action == Directions.STOP: features['Ostop'] = 1
      rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
      if action == rev: features['Oreverse'] = 1

      if self.onOtherSide(gameState):
        desY = int(myPos[1])
        if self.red:
          desX = int(successor.data.layout.width/2 - 1)#################
          nextP = [(desX-1, desY), (desX, desY+1), (desX, desY-1)]
        else:
          desX = int(successor.data.layout.width/2 + 1)
          nextP = [(desX+1, desY), (desX, desY+1), (desX, desY-1)]
        iternum = 0
        while not (0<=desX<successor.data.layout.width and 0<=desY<successor.data.layout.height) or gameState.hasWall(desX, desY):
          (desX, desY) = random.choice(nextP)
          iternum += 1
          if iternum > 20:
            for yy in range(successor.data.layout.height):
              if not gameState.hasWall(desX, yy):
                desY = yy
                break
            break
        
        features['dHome'] = -self.getMazeDistance(myPos, (desX, desY))
      
      return features
    elif self.red and self.onOtherSide(gameState) and self.numF > self.limit:
      myPos = successor.getAgentState(self.index).getPosition()
      desY = int(myPos[1])
      desX = int(successor.data.layout.width/2 - 1)
      iternum = 0
      while not (0<=desX<successor.data.layout.width and 0<=desY<successor.data.layout.height) or gameState.hasWall(desX, desY):
        (desX, desY) = random.choice([(desX-1, desY), (desX, desY+1), (desX, desY-1)])
        iternum += 1
        if iternum > 20:
          for yy in range(successor.data.layout.height):
            if not gameState.hasWall(desX, yy):
              desY = yy
              break
          break
        
      features['dHome'] = -self.getMazeDistance(myPos, (desX, desY))

      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      if len(ghosts) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        if ghosts[dists.index(min(dists))].scaredTimer < 5:
          features['ghostDistance'] = min(dists)
        else:
          features['ghostDistance'] = -min(dists)

      if action == Directions.STOP: features['stop'] = 1
      
    elif not self.red and self.onOtherSide(gameState) and self.numF > self.limit:
      myPos = successor.getAgentState(self.index).getPosition()
      desY = int(myPos[1])
      desX = int(successor.data.layout.width/2 + 1)
      iternum = 0
      while not (0<=desX<successor.data.layout.width and 0<=desY<successor.data.layout.height) or gameState.hasWall(desX, desY):
        (desX, desY) = random.choice([(desX+1, desY), (desX, desY+1), (desX, desY-1)])
        iternum += 1
        if iternum > 20:
          for yy in range(successor.data.layout.height):
            if not gameState.hasWall(desX, yy):
              desY = yy
              break
          break
      features['dHome'] = -self.getMazeDistance(myPos, (desX, desY))

      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      if len(ghosts) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        if ghosts[dists.index(min(dists))].scaredTimer < 5:
          features['ghostDistance'] = min(dists)
        else:
          features['ghostDistance'] = -min(dists)
      
      if action == Directions.STOP: features['stop'] = 1
      
    else:
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      foodList = self.getFood(successor).asList()
      foodList += self.getCapsules(successor)
      features['successorScore'] = -len(foodList)#self.getScore(successor)
        
      # Compute distance to the nearest food

      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        myPos = successor.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
      
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      features['numInvaders'] = len(invaders)
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      if len(ghosts) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        features['ghostDistance'] = min(dists) * 0.22
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1.5, 'dHome': 20, 'ghostDistance':5.5, 'stop': -10000, 'numInvaders':-10000,
            'OnumInvaders': -1000, 'OonDefense': 10, 'OinvaderDistance': -20, 'Ostop': -100, 'Oreverse': -2}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  def onOtherSide(self, gameState):
    return (self.red and gameState.getAgentPosition(self.index)[0] > gameState.data.layout.width/2-3) or (not self.red and gameState.getAgentPosition(self.index)[0] < gameState.data.layout.width/2+3)
  
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    if len(ghosts) > 0:
        gdists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0 or min(gdists) < 5 or self.numF > self.limit:
      self.de = True
    else:
      self.de = False
    if self.de:
      
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
        if gameState.getAgentState(self.index).scaredTimer > 0 and min(dists) < 5:
          features['invaderDistance'] = -min(dists)
      if action == Directions.STOP: features['stop'] = 1
      rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
      if action == rev: features['reverse'] = 1
      
    elif self.red and self.onOtherSide(gameState) and self.numF > self.limit:
      myPos = successor.getAgentState(self.index).getPosition()
      desY = int(myPos[1])
      desX = int(successor.data.layout.width/2 - 1)
      iternum = 0
      while not (0<=desX<successor.data.layout.width and 0<=desY<successor.data.layout.height) or gameState.hasWall(desX, desY):
        (desX, desY) = random.choice([(desX-1, desY), (desX, desY+1), (desX, desY-1)])
        iternum += 1
        if iternum > 20:
          for yy in range(successor.data.layout.height):
            if not gameState.hasWall(desX, yy):
              desY = yy
              break
          break
        
      features['dHome'] = -self.getMazeDistance(myPos, (desX, desY))

      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      if len(ghosts) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        if ghosts[dists.index(min(dists))].scaredTimer < 5:
          features['ghostDistance'] = min(dists)
        else:
          features['ghostDistance'] = -min(dists)

      if action == Directions.STOP: features['stop'] = 1
      
    elif not self.red and self.onOtherSide(gameState) and self.numF > self.limit:
      myPos = successor.getAgentState(self.index).getPosition()
      desY = int(myPos[1])
      desX = int(successor.data.layout.width/2 + 1)
      iternum = 0
      while not (0<=desX<successor.data.layout.width and 0<=desY<successor.data.layout.height) or gameState.hasWall(desX, desY):
        (desX, desY) = random.choice([(desX+1, desY), (desX, desY+1), (desX, desY-1)])
        iternum += 1
        if iternum > 20:
          for yy in range(successor.data.layout.height):
            if not gameState.hasWall(desX, yy):
              desY = yy
              break
          break
      features['dHome'] = -self.getMazeDistance(myPos, (desX, desY))

      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      if len(ghosts) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        if ghosts[dists.index(min(dists))].scaredTimer < 5:
          features['ghostDistance'] = min(dists)
        else:
          features['ghostDistance'] = -min(dists)
      
      if action == Directions.STOP: features['stop'] = 1
      
    else:
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      foodList = self.getFood(successor).asList()
      foodList += self.getCapsules(successor)
      features['successorScore'] = -len(foodList)#self.getScore(successor)
        
      # Compute distance to the nearest food

      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        myPos = successor.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
      
      enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
      features['numInvaders'] = len(invaders)
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      if len(ghosts) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        features['ghostDistance'] = min(dists) * 0.22
    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -10000, 'onDefense': 15, 'invaderDistance': -35, 'reverse': -2,
            'successorScore': 100, 'distanceToFood': -1.5, 'dHome': 15, 'ghostDistance':5.5, 'stop': -10000,
            'OnumInvaders': -1000, 'OonDefense': 10, 'OinvaderDistance': -20, 'Ostop': -100, 'Oreverse': -2}
