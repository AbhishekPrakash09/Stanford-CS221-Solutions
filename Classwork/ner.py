"""
This file depends on submission.py from your sentiment homework.
You can run it if you plug in your submission.
"""

import submission, util
from collections import defaultdict

# Read in examples
trainExamples = util.readExamples('names.train')
validExamples = util.readExamples('names.valid')

def featureExtractor(x):
    # Example: x = "took Mauritius into"
    phi = defaultdict(float)
    tokens = x.split()
    left, entity, right = tokens[0], tokens[1:-1], tokens[-1]
    phi['entity is ' + ' '.join(entity)] = 1
    phi['left is ' + left] = 1
    phi['right is ' + right] = 1
    for word in entity:
        phi['entity contains ' + word] = 1
        phi['entity contains prefix ' + word[:4]] = 1  # first 4 characters
        phi['entity contains suffix ' + word[-4:]] = 1  # last 4 characters
    return phi

# Learn a predictor
weights = submission.learnPredictor(trainExamples, validExamples, featureExtractor)
util.outputWeights(weights, 'weights')
util.outputErrorAnalysis(validExamples, featureExtractor, weights, 'error-analysis')

# Test (only do this at the end)!
testExamples = util.readExamples('names.test')
predictor = lambda x : 1 if util.dotProduct(featureExtractor(x), weights) > 0 else -1
testError = util.evaluatePredictor(testExamples, predictor)
print(f'test error = {testError}')
