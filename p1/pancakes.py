import util

def getStartState():
    return [2,6,7,4,3,5,1]

def isGoal(state):
    return sorted(state) == state

def flip(state, n):
    toBeFlipped = state[0:n]
    toBeFlipped.reverse()
    result = toBeFlipped + state[n:len(state)]
    return result

def getSuccessors(state):
    successors = []
    for i in range(2, len(state) + 1):
      newState = flip(state, i)
      action = [i]
      cost = i
      successors.append((newState, action, cost))
    return successors

def uniformCostSearch():
    visited = []
    pq = util.PriorityQueue()
    start = (getStartState(), [], 0)
    pq.push(start, 0)
    while(pq):
        state, action, cost = pq.pop()
        if(isGoal(state)):
            print(len(visited))
            return action
        if(state not in visited):
            visited.append(state)
            for successor in getSuccessors(state):
                newState, newAction, newCost = successor[0], action + successor[1], cost + successor[2]
                pq.update((newState, newAction, newCost), newCost)
    util.raiseNotDefined()

def AStarSearch():
    visited = []
    pq = util.PriorityQueue()
    start = (getStartState(), [], 0)
    pq.push(start, 0)
    while(pq):
        state, action, cost = pq.pop()
        if(isGoal(state)):
            print(len(visited))
            return action
        if(state not in visited):
            visited.append(state)
            for successor in getSuccessors(state):
                newState, newAction, newCost = successor[0], action + successor[1], cost + successor[2]
                heuristic = len(newState) - newState.index(max(newState)) - 1
                pq.update((newState, newAction, newCost), newCost + heuristic)
    util.raiseNotDefined()

print(AStarSearch())
