import sys
import util
sys.setrecursionlimit(10000)

### Model (search problem)

class TransportationProblem(object):
    def __init__(self, N, weights):
        # N = number of blocks
        # weights = specifies the costs of actions
        self.N = N
        self.weights = weights
    def startState(self):
        return 1
    def isEnd(self, state):
        return state == self.N
    def succAndCost(self, state):
        # Returns list of (action, newState, cost) triples
        result = []
        if state + 1 <= self.N:
            result.append(('walk', state + 1, self.weights['walk']))
        if 2 * state <= self.N:
            result.append(('tram', 2 * state, self.weights['tram']))
        return result

### Inference (search algorithms)

def printSolution(solution):
    totalCost, history = solution
    print(('totalCost:', totalCost))
    for item in history:
        print(item)

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

### Main

def predict(N, weights):
    # f(x)
    # Input (x): N (number of cities)
    # Output (y): path (sequence of actions)
    problem = TransportationProblem(N, weights)
    totalCost, history = dynamicProgramming(problem)
    return [action for action, newState, cost in history]

def generateExamples():
    trueWeights = {'walk': 1, 'tram': 5}
    return [(N, predict(N, trueWeights)) for N in range(1, 30)]

def structuredPerceptron(examples):
    weights = {'walk': 0, 'tram': 0}
    for t in range(100):
        numMistakes = 0
        for N, trueActions in examples:
            # Make a prediction
            predActions = predict(N, weights)
            if predActions != trueActions:
                numMistakes += 1
            # Update weights
            for action in trueActions: weights[action] -= 1
            for action in predActions: weights[action] += 1
        print(('iteration {}, numMistakes = {}, weights = {}'.format(t, numMistakes, weights)))
        if numMistakes == 0:
            break

examples = generateExamples()
print('Training dataset:')
for ex in examples:
    print(('  ', ex))

structuredPerceptron(examples)
