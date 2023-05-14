#!/usr/bin/env python3

import collections
import graderUtil
import random

grader = graderUtil.Grader()
submission = grader.load('submission')

############################################################
# Problems 1, 2, 3

# Problem 1
grader.add_manual_part('1a', max_points=2, description='optimize weighted average')
grader.add_manual_part('1b', max_points=3, description='vector norm inequalities')
grader.add_manual_part('1c', max_points=3, description='expected value of iterated game')
grader.add_manual_part('1d', max_points=3, description='derive maximum likelihood')
grader.add_manual_part('1e', max_points=3, description='manipulate conditional probabilities')
grader.add_manual_part('1f', max_points=4, description='take gradient')

# Problem 2
grader.add_manual_part('2a', max_points=2, description='counting faces')
grader.add_manual_part('2b', max_points=3, description='dynamic program')

# Problem 3
grader.add_manual_part('3a', max_points=2, description='ethics in ai scenario a negative impacts statement')
grader.add_manual_part('3b', max_points=2, description='ethics in ai scenario b negative impacts statement')
grader.add_manual_part('3c', max_points=2, description='ethics in ai scenario c negative impacts statement')
grader.add_manual_part('3d', max_points=2, description='ethics in ai scenario d negative impacts statement')

############################################################
# Problem 4a: findAlphabeticallyFirstWord

grader.add_basic_part('4a-0-basic', lambda:
                      grader.require_is_equal('alphabetically', submission.find_alphabetically_first_word(
                        'which is the first word alphabetically')),
                      description='simple test case')

grader.add_basic_part('4a-1-basic',
                      lambda: grader.require_is_equal('cat', submission.find_alphabetically_first_word('cat sun dog')),
                      description='simple test case')

grader.add_basic_part('4a-2-basic', lambda: grader.require_is_equal('0', submission.find_alphabetically_first_word(
    ' '.join(str(x) for x in range(100000)))), description='big test case')

############################################################
# Problem 4b: euclideanDistance

grader.add_basic_part('4b-0-basic', lambda: grader.require_is_equal(5, submission.euclidean_distance((1, 5), (4, 1))),
                      description='simple test case')


def test4b1():
    random.seed(42)
    for _ in range(100):
        x1 = random.randint(0, 10)
        y1 = random.randint(0, 10)
        x2 = random.randint(0, 10)
        y2 = random.randint(0, 10)
        ans2 = submission.euclidean_distance((x1, y1), (x2, y2))


grader.add_hidden_part('4b-1-hidden', test4b1, max_points=2, description='100 random trials')


############################################################
# Problem 4c: mutateSentences

def test4c0():
    grader.require_is_equal(sorted(['a a a a a']), sorted(submission.mutate_sentences('a a a a a')))
    grader.require_is_equal(sorted(['the cat']), sorted(submission.mutate_sentences('the cat')))
    grader.require_is_equal(
        sorted(['and the cat and the', 'the cat and the mouse', 'the cat and the cat', 'cat and the cat and']),
        sorted(submission.mutate_sentences('the cat and the mouse')))


grader.add_basic_part('4c-0-basic', test4c0, max_points=1, description='simple test')


def gen_sentence(alphabet_size, length):
    return ' '.join(str(random.randint(0, alphabet_size)) for _ in range(length))


def test4c1():
    random.seed(42)
    for _ in range(10):
        sentence = gen_sentence(3, 5)
        ans2 = submission.mutate_sentences(sentence)


grader.add_hidden_part('4c-1-hidden', test4c1, max_points=2, description='random trials')


def test4c2():
    random.seed(42)
    for _ in range(10):
        sentence = gen_sentence(25, 10)
        ans2 = submission.mutate_sentences(sentence)


grader.add_hidden_part('4c-2-hidden', test4c2, max_points=3, description='random trials (bigger)')


############################################################
# Problem 4d: dotProduct

def test4d0():
    grader.require_is_equal(15, submission.sparse_vector_dot_product(collections.defaultdict(float, {'a': 5}),
                                                                     collections.defaultdict(float, {'b': 2, 'a': 3})))


grader.add_basic_part('4d-0-basic', test4d0, max_points=1, description='simple test')


def randvec():
    v = collections.defaultdict(float)
    for _ in range(10):
        v[random.randint(0, 10)] = random.randint(0, 10) - 5
    return v


def test4d1():
    random.seed(42)
    for _ in range(10):
        v1 = randvec()
        v2 = randvec()
        ans2 = submission.sparse_vector_dot_product(v1, v2)


grader.add_hidden_part('4d-1-hidden', test4d1, max_points=3, description='random trials')


############################################################
# Problem 4e: incrementSparseVector

def test4e0():
    v = collections.defaultdict(float, {'a': 5})
    submission.increment_sparse_vector(v, 2, collections.defaultdict(float, {'b': 2, 'a': 3}))
    grader.require_is_equal(collections.defaultdict(float, {'a': 11, 'b': 4}), v)


grader.add_basic_part('4e-0-basic', test4e0, description='simple test')


def test4e1():
    random.seed(42)
    for _ in range(10):
        v1a = randvec()
        v1b = v1a.copy()
        v2 = randvec()
        submission.increment_sparse_vector(v1b, 4, v2)
        for key in list(v1b):
            if v1b[key] == 0:
                del v1b[key]


grader.add_hidden_part('4e-1-hidden', test4e1, max_points=3, description='random trials')


############################################################
# Problem 4f: findNonsingletonWords

def test4f0():
    grader.require_is_equal({'the', 'fox'},
                            submission.find_nonsingleton_words('the quick brown fox jumps over the lazy fox'))


grader.add_basic_part('4f-0-basic', test4f0, description='simple test')


def test4f12(num_tokens, num_types):
    import random
    random.seed(42)
    text = ' '.join(str(random.randint(0, num_types)) for _ in range(num_tokens))
    ans2 = submission.find_nonsingleton_words(text)


grader.add_hidden_part('4f-1-hidden', lambda: test4f12(1000, 10), max_points=1, description='random trials')
grader.add_hidden_part('4f-2-hidden', lambda: test4f12(10000, 100), max_points=2, description='random trials (bigger)')


############################################################
grader.grade()
