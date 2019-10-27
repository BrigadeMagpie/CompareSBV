"""
Module for reconcilling overlaps between subtitle versions
"""

import re
from pprint import pprint
from difflib import Differ

TIMESTAMP_PATTERN_ = "(\d+)?:?(\d{2}):(\d{2})[.,](\d{3})"
TIMESTAMP_PATTERN = re.compile(TIMESTAMP_PATTERN_)
TIMESTAMP_RANGE_PATTERN = re.compile(TIMESTAMP_PATTERN_ + "," + TIMESTAMP_PATTERN_)

def reconcile(a, b):
  """
  Try to match up subtitles from a to subtitles from b.
  Possible cases to reconcile:
    - No change
    - Timeline change
    - Subtitle text change
    - Both timeline and subtitle text change
    - Removal
    - Addition
    - Splitting
    - Merging
  """

  differ = Differ()
  result = differ.compare(a, b)
  diff = list(result)

  return _reconcile(diff, a, b)

def _reconcile(diff, a, b):
  i_a = 0
  i_b = 0

  result = []
  block = []

  count = 0
  for d in diff:
    count += 1
    d = d[:-1] # strip newline

    if d == "  ":
      _result = _parse_block(block, count < 5)

      # print("block: %s, _result: %s" % (block, _result))

      if _result[0]:
        result.extend(_result[1])

      result.append([])
      block = []

      i_a += 1
      i_b += 1 

    else:
      if d[0] == '?':
        continue

      c, l = _parse_line(d)

      if c == ' ':
        i_a += 1
        i_b += 1 
      elif c == '-':
        i_a += 1
      elif c == '+':
        i_b += 1
      else:
        raise Exception("Unexpected code. c: %s, l: %s" % (c, l))

      block.append((c, l))

  print("len(a): %d, i_a: %d" % (len(a), i_a))
  print("len(b): %d, i_b: %d" % (len(b), i_b))

  return result

def _parse_block(block, debug):
  a = { "text": [] }
  b = { "text": [] }

  for i in range(len(block)):
    c, _l = block[i]
    is_tr = _is_tr(_l)

    if not ("start" in a and "end" in a and "start" in b and "end" in b):
      if not is_tr:
        raise Exception("Expected timestamps. c: %s, _l: %s, a: %s, b: %s" % (c, _l, a, b))
      if c == ' ':
        _assign_tr(a, _l)
        _assign_tr(b, _l)
      elif c == '-':
        _assign_tr(a, _l)
      elif c == '+':
        _assign_tr(b, _l)
      else:
        raise Exception("Unexpected code. c: %s, _l: %s, a: %s, b: %s" % (c, _l, a, b))
    else:
      if is_tr:
        raise Exception("Expected subtitles. c: %s, _l: %s, a: %s, b: %s" % (c, _l, a, b))

      if c == ' ':
        a["text"].append(_l)
        b["text"].append(_l)
      elif not _l: # adding or removing new line
        return (False, None)
      elif c == '-':
        a["text"].append(_l)
      elif c == "+":
        b["text"].append(_l)
      else:
        raise Exception("Unexpected code. c: %s, _l: %s, a: %s, b: %s" % (c, _l, a, b))

    if debug:
      print("block: %s, i:%d, c: '%s', _l: %s, a: %s, b: %s" % (block, i, c, _l, a, b))

  return (True, [(a, b)])


def _assign_tr(obj, tr):
  if "start" in obj or "end" in obj:
    raise Exception("obj already contains timestamps. obj: %s, tr: %s" % (obj, tr))

  start, end = tr.split(',')
  obj["start"] = start
  obj["end"] = end

def _parse_line(d):
  return (d[0], d[2:])

def _is_tr(s):
  return re.match(TIMESTAMP_RANGE_PATTERN, s) is not None


if __name__ == '__main__':
  import sys

  fn_a = sys.argv[1]
  fn_b = sys.argv[2]
  fn_out = sys.argv[3]
  
  a = []
  b = []
  with open(fn_a, "r", encoding="utf8") as f:
    a = f.readlines()

  with open(fn_b, "r", encoding="utf8") as f:
    b = f.readlines()

  res = reconcile(a, b)

  for d in res:
    print(d)