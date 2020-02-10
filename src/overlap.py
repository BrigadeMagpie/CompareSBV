#!/usr/bin/env python

import sys
from os import path
import webvtt
from webvtt.structures import Caption
from difflib import Differ

SEPARATOR = "------------------------------------------"
OUTDIR = None

class SubtitleMatcher(object):
  def match(self, pass_num, blocks):
    raise NotImplementedError

class IdenticalSubtitleMatcher(SubtitleMatcher):
  def match(self, pass_num, blocks):
    _blocks = []
    for block in blocks:
      if block[0]:
        _blocks.append(block)
      else:
        _blocks.extend(self._match(pass_num, block[1], block[2]))
    return _blocks


  def _match(self, rank, b1, b2):
    # Get first of b1, compare to first of b2
    # Start with the "later" one
    # Scan the other list for a match until it's passed

    result = []

    if not b1 and not b2:
      result = [(True, b1, b2, rank)]
    elif not b1 or not b2:
      result = [(False, b1, b2, rank)]
    else:
      l1 = len(b1)
      l2 = len(b2)
      i1 = 0
      i2 = 0

      block1 = []
      block2 = []
      while i1 < l1 and i2 < l2:
        s1 = b1[i1]
        s2 = b2[i2]
        tr1 = s1[:s1.index(' ')]
        tr2 = s2[:s2.index(' ')]
        ts1 = tr1[:tr1.index(',')]
        ts2 = tr2[:tr2.index(',')]

        if ts1 == ts2:
          if tr1 == tr2:
            if block1 or block2:
              result.append((False, block1, block2, rank))
              block1 = []
              block2 = []
            result.append((True, [s1], [s2], rank))
          else:
            block1.append(s1)
            block2.append(s2)
          i1 += 1
          i2 += 1
        elif ts1 < ts2:
          block1.append(s1)
          i1 += 1
        elif ts1 > ts2:
          block2.append(s2)
          i2 += 1
      if i1 < l1:
        block1.extend(b1[i1:])
      if i2 < l2:
        block2.extend(b2[i2:])
      if block1 or block2:
        result.append((False, block1, block2, rank))
        block1 = []
        block2 = []

    writeBlocks("_pass_1.txt", result)
    return result

class DiffSubtitleMatcher(SubtitleMatcher):
  def match(self, pass_num, blocks):
    """
    Use of single-line diff to get a general match up between the two versions of
    subtitles
    """
    differ = Differ()
    result = []

    for block in blocks:
      if block[0]:
        result.append(block)
        continue

      # print("block")
      diff = differ.compare(block[1], block[2])
      diff = list(diff)

      b = []
      usable = False

      try:
        for line in diff:
          # print(line)
          code = line[0]
          s = line[2:]

          if code == ' ':
            result.append((True, [s], [s], pass_num))
            continue
          elif code == '-' or code == '+':
            b.append(line)
          elif code == '?':
            if not b:
              continue
            usable = True

          if usable:
            # print("b: %s" % b)
            # print("line_: %s" % line)

            last_line = b[-1]
            if last_line[0] == '+':
              first = b[:-2]
              if first:
                b1, b2 = self._parse_diff_to_blocks(first)
                result.append((False, b1, b2, pass_num))
              b1, b2 = self._parse_diff_to_blocks(b[-2:])
              result.append((True, b1, b2, pass_num))

              usable = False
              b = []
        if b:
          b1, b2 = self._parse_diff_to_blocks(b)
          result.append((False, b1, b2, pass_num))
      except Exception as e:
        import traceback
        traceback.print_tb(e.__traceback__)
        print("result: %s")
        printBlocks(result)
        print("usable: %s" % usable)

    writeBlocks("_pass_2.txt", result)
    return result

  def _parse_diff_to_blocks(self, diff):
    if not diff:
      return ([], [])
    b1 = []
    b2 = []

    for d in diff:
      code = d[0]
      s = d[2:]
      if code == ' ':
        b1.append(s)
        b2.append(s)
      elif code == '-':
        b1.append(s)
      elif code == '+':
        b2.append(s)

    return (b1, b2)

class FuzzyTimeRangeSubtitleMatcher(SubtitleMatcher):
  def match(self, pass_num, blocks):
    """
    Use a modified Longest Common Subsequence algorithm to fuzzy match the timestamps
    """

    result = []
    for block in blocks:
      if block[0]:
        result.append(block)
        continue

      b1 = block[1]
      b2 = block[2]
      tr_vals1 = self._append_tr_vals(b1)
      tr_vals2 = self._append_tr_vals(b2)

      pairs = self._lcs(tr_vals1, tr_vals2)
      
      i1 = 0
      i2 = 0
      for pair in pairs:
        j1, j2 = pair
        _b1 = b1[i1:j1]
        _b2 = b2[i2:j2]

        if _b1 or _b2:
          result.append((False, _b1, _b2, pass_num))

        result.append((True, [b1[j1]], [b2[j2]], pass_num))
        i1, i2 = pair
        i1 += 1
        i2 += 1

      l1 = len(b1)
      l2 = len(b2)

      _b1 = b1[i1:l1]
      _b2 = b2[i2:l2]

      if _b1 or _b2:
        result.append((False, _b1, _b2  , pass_num))

    writeBlocks("_pass_3.txt", result)
    return result

  def _append_tr_vals(self, b):
    result = []
    for l in b:
      tr = l[:l.index(' ')]
      ts1, ts2 = tr.split(',')
      ms1 = _parse_timestamp(ts1)
      ms2 = _parse_timestamp(ts2)

      result.append([l, (ms1, ms2)])
    return result

  def _lcs(self, x, y):
    len_x = len(x)
    len_y = len(y)

    # for _x in x:
    #   print(_x)
    # print()

    # for _y in y:
    #   print(_y)
    # print()

    m = [[0 for _ in range(len_y + 1)]]
    for i in range(len_x):
      m.append([0 for _ in range(len_y + 1)])

    m_ = [[0 for _ in range(len_y + 1)]]
    for i in range(len_x):
      m_.append([0 for _ in range(len_y + 1)])

    for i in range(1, len_x + 1):
      for j in range(1, len_y + 1):
        try:
          score = self._score(x[i-1][1], y[j-1][1])
          m_[i][j] = score
          m[i][j] = max(m[i-1][j], m[i][j-1], score + m[i-1][j-1])
        except:
          print("(%d, %d)" % (i, j))
          raise Exception()

    # for _ in m_:
    #   print(_)
    # for _ in m:
    #   print(_)
    # print()

    pairs = []
    i = len_x
    j = len_y
    while i > 0 and j > 0:
      m_score = m[i][j]
      if m_score == m[i-1][j]:
        i -= 1
      elif m_score == m[i][j-1]:
        j -= 1
      elif m_score == (m[i-1][j-1] + m_[i][j]):
        if m_[i][j] >= 1:
          pairs.insert(0, (i-1, j-1))
        i -= 1
        j -= 1
      else:
        print("(%d, %d)" % (i, j))
        sys.exit(0)

    # print("pairs:")
    # for p in pairs:
    #   print(p)

    # printSeparator()
    # print()

    return pairs

  def _score(self, x, y):
    xa, xb = x
    ya, yb = y

    dx = xb - xa
    dy = yb - ya

    top = min(dx, dy) / max(dx, dy)

    r = abs(self._mid(xa, xb) - self._mid(ya, yb)) + 1

    return top * 10000 / r

  def _mid(self, x, y):
    return x + (y - x) / 2

def merge(f1, f2, matchers):
  b1 = sbv_to_block(f1)
  b2 = sbv_to_block(f2)
  b = (False, b1, b2, 0)
  blocks = [b]

  for i, matcher in enumerate(matchers, start=1):
    blocks = matcher.match(i, blocks)

  blocks = blocks_to_sbv_blocks(blocks)

  return blocks

def sbv_to_block(f):
  result = []

  for caption in f:
    lines = [line.rstrip() for line in caption.lines]
    text = "\\n".join(lines)
    result.append("%s,%s %s" % (caption.start, caption.end, text))

  return result

def block_to_sbv(b):
  i_tsr = b.index(' ')
  tsr = b[:i_tsr]
  _text = b[i_tsr+1:]

  ts1, ts2 = tsr.split(',')
  text = _text.split("\\n")

  return Caption(start = ts1, end = ts2, text = text)

def blocks_to_sbv_blocks(blocks):
  result = []

  for b in blocks:
    match, b1, b2, pass_num = b

    _b1 = []
    _b2 = []

    for _b in b1:
      _b1.append(block_to_sbv(_b))
    for _b in b2:
      _b2.append(block_to_sbv(_b))

    result.append((match, _b1, _b2, pass_num))

  writeBlocks("final.txt", result)
  return result

def _parse_timestamp(ts):
  hms, ms = ts.split('.')
  h, m, s = hms.split(':')

  return (((int(h) * 60) + int(m)) * 60 + int(s)) * 1000 + int(ms)

def printBlock(block):
  for line in block:
    print(line.rstrip())

  print("")

def printBlocks(blocks):
  for block in blocks:
    if len(block) <= 2:
      continue
    printBlock(block)
    printSeparator()

def printSeparator():
  print("------------------------------------------")

def writeBlocks(file, blocks):
  if not OUTDIR:
    return
  with open(path.join(OUTDIR, file), "w", encoding="utf-8") as f:
    for b in blocks:
      len_b = len(b)
      if len_b == 3:
        f.write("%s %d\n" % (b[0], b[2]))
        for l in b[1]:
          f.write(l + "\n")
        f.write(SEPARATOR + "\n")
      elif len_b == 4:
        f.write("%s %d\n" % (b[0], b[3]))
        for l in b[1]:
          f.write(str(l))
          f.write("\n")
        f.write("\n")
        for l in b[2]:
          f.write(str(l))
          f.write("\n")
        f.write(SEPARATOR + "\n")
