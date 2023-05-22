import sys
import util
sys.setrecursionlimit(10000)

### Model (search problem)

class TransportationProblem(object):
    def __init__(self, N):
        # N = number of blocks
        self.N = N
    def startState(self):
        return 1
    def isEnd(self, state):
        return state == self.N
    def succAndCost(self, state):
        # Returns list of (action, newState, cost) triples
        result = []
        if state + 1 <= self.N:
            result.append(('walk', state + 1, 1))
        if 2 * state <= self.N:
            result.append(('tram', 2 * state, 2))
        return result

### Inference (search algorithms)

def printSolution(solution):
    totalCost, history = solution
    print('totalCost:', totalCost)
    for item in history:
        print(item)

def backtrackingSearch(problem):
    # Best found so far
    # (technicality: using array because of Python scoping)
    bestTotalCost = [float('+inf')]
    bestHistory = [None]
    def recurse(state, history, totalCost):
        # At |state| having undergone |history|, accumulated |totalCost|.
        # Explore the rest of the subtree under |state|.
        if problem.isEnd(state):
            # Update the best solution so far
            if totalCost < bestTotalCost[0]:
                bestTotalCost[0] = totalCost
                bestHistory[0] = history
            return

        # Recurse on children
        for action, newState, cost in problem.succAndCost(state):
            recurse(newState, history + [(action, newState, cost)], totalCost + cost)

    recurse(problem.startState(), history=[], totalCost=0)
    return (bestTotalCost[0], bestHistory[0])

def dynamicProgramming(problem):
    cache = {}  # state => futureCost(state), action, newState, cost
    def futureCost(state):
        # Base case
        if problem.isEnd(state):
            return 0
        if state in cache:  # Exponential savings!
            return cache[state][0]
        # Actually do work
        result = min((cost + futureCost(newState), action, newState, cost) \
            for action, newState, cost in problem.succAndCost(state))
        cache[state] = result
        return result[0]

    state = problem.startState()
    totalCost = futureCost(state)

    # Recover history
    history = []
    while not problem.isEnd(state):
        _, action, newState, cost = cache[state]
        history.append((action, newState, cost))
        state = newState

    return (totalCost, history)

def uniformCostSearch(problem):
    frontier = util.PriorityQueue()
    frontier.update(problem.startState(), 0)
    while True:
        # Move from frontier to explored
        state, pastCost = frontier.removeMin()
        if problem.isEnd(state):
            # Note: don't compute history
            return (pastCost, [])
        # Push out on the frontier
        for action, newState, cost in problem.succAndCost(state):
            frontier.update(newState, pastCost + cost)

### Main

problem = TransportationProblem(N=40)
print(problem.succAndCost(3))
print(problem.succAndCost(9))
printSolution(backtrackingSearch(problem))
printSolution(dynamicProgramming(problem))
printSolution(uniformCostSearch(problem))
