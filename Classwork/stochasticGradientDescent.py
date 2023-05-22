import numpy as np
import math

############################################################
# Optimization problem

trueW = np.array([1, 2, 3, 4, 5])
def generate():
    x = np.random.randn(len(trueW))
    y = trueW.dot(x) + np.random.randn()
    #print('example', x, y)
    return (x, y)

trainExamples = [generate() for i in range(1000000)]

def phi(x):
    return np.array(x)

def initialWeightVector():
    return np.zeros(len(trueW))

def trainLoss(w):
    return 1.0 / len(trainExamples) * sum((w.dot(phi(x)) - y)**2 for x, y in trainExamples)

def gradientTrainLoss(w):
    return 1.0 / len(trainExamples) * sum(2 * (w.dot(phi(x)) - y) * phi(x) for x, y in trainExamples)

def loss(w, i):
    x, y = trainExamples[i]
    return (w.dot(phi(x)) - y)**2

def gradientLoss(w, i):
    x, y = trainExamples[i]
    return 2 * (w.dot(phi(x)) - y) * phi(x)

############################################################
# Optimization algorithm

def gradientDescent(F, gradientF, initialWeightVector):
    w = initialWeightVector()
    eta = 0.1
    for t in range(500):
        value = F(w)
        gradient = gradientF(w)
        w = w - eta * gradient
        print(f'epoch {t}: w = {w}, F(w) = {value}, gradientF = {gradient}')

def stochasticGradientDescent(f, gradientf, n, initialWeightVector):
    w = initialWeightVector()
    numUpdates = 0
    for t in range(500):
        for i in range(n):
            value = f(w, i)
            gradient = gradientf(w, i)
            numUpdates += 1
            eta = 1.0 / math.sqrt(numUpdates)
            w = w - eta * gradient
        print(f'epoch {t}: w = {w}, F(w) = {value}, gradientF = {gradient}')

#gradientDescent(trainLoss, gradientTrainLoss, initialWeightVector)
stochasticGradientDescent(loss, gradientLoss, len(trainExamples), initialWeightVector)
