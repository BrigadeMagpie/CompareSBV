"""
Module for calculating word change percentage
"""

import math
import re
from pprint import pprint
from difflib import Differ

def normalize(t):
  """
  Strip spaces before and after
  Make everything lowercase
  Remove punctuations to avoid including them in the diff
  """
  return re.sub('[,.?!]', ' ', t.lower())


def word_change_block(added, deleted):
  """
  Calculates the number of accepted changed words for a consecutive block of change.
  The changes below comes out to be 2. Any opposite signs in the same block is reduced to 1 change instead of 2
  '-   a'
  '-   b'
  '+   c'
  '+   d'
  """
  return max(added, deleted)

def word_change(old_t, new_t):
  """
  Takes two strings and returns the ratio of changed words to the number of the words in the original string.
  """
  _old_t = normalize(old_t)
  _new_t = normalize(new_t)

  _old_t = _old_t.split()
  _new_t = _new_t.split()

  differ = Differ()
  diff = list(differ.compare(_old_t, _new_t))

  total = 0
  curr_add = 0
  curr_del = 0
  for d in diff:
    c = d[0]
    if c == '?':
      continue

    if c == ' ':
      total += word_change_block(curr_add, curr_del)
      curr_add = 0
      curr_del = 0
    elif c == '+':
      curr_add += 1
    elif c == '-':
      curr_del += 1
    else:
      raise Exception("Something went wrong")

  old_len = len(_old_t)
  if old_len == 0:
    return math.inf
  total += word_change_block(curr_add, curr_del)
  return total / len(_old_t)

"""
Tests
"""
if __name__ == '__main__':
  tests = []
  tests.append(
    ("So why aren't there the affection in your singing?",
     "So why aren't there the affection in your singing?"))
  tests.append(
    ("",
     "So why aren't there the affection in your singing?"))
  tests.append(
    ("So why aren't there the affection in your singing?",
     ""))
  tests.append(
    ("So why aren't there, the affection, in your singing?",
     "So why aren't there the affection in your singing?"))
  tests.append(
    ("So why aren't there the affection in your singing?",
     "So why aren't there the love in your singing?"))
  tests.append(
    ("So why aren't there the affection in your singing?",
     "So why aren't there the affection in your singing howdy buddy?"))
  tests.append(
    ("So why aren't there the affection in your singing?",
     "So why aren't there affection in your singing howdy buddy?"))
  
  for test in tests:
    print("old: '{}'".format(test[0]))
    print("new: '{}'".format(test[1]))
    wc = word_change(test[0], test[1])
    print("word change: {:.2%}\n".format(wc))