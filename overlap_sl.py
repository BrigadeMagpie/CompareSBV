#!/usr/bin/env python

import sys
from os import path
import webvtt
from difflib import Differ

SEPARATOR = "------------------------------------------"

def merge_sbv(outdir, f1, f2):
  b1 = transform_sbv(f1)
  b2 = transform_sbv(f2)

  blocks = _pass_1(outdir, 1, b1, b2)
  blocks = _pass_2(outdir, 2, blocks)
  blocks = _pass_3(outdir, 3, blocks)

  return blocks

def transform_sbv(f):
  result = []

  for caption in f:
    lines = [line.rstrip() for line in caption.lines]
    text = "\\n".join(lines)
    result.append("%s,%s %s" % (caption.start, caption.end, text))

  return result


def _pass_1(outdir, rank, b1, b2):
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
        i1 += 1
        i2 += 1
      elif ts1 < ts2:
        block1.append(s1)
        i1 += 1
      elif ts1 > ts2:
        block2.append(s2)
        i2 += 1
    if block1 or block2:
      result.append((False, block1, block2, rank))
      block1 = []
      block2 = []

  writeBlocks(path.join(outdir, "_pass_1.txt"), result)
  return result

def _pass_2(outdir, rank, blocks):
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

    diff = differ.compare(block[1], block[2])
    diff = list(diff)

    b = []
    usable = False

    try:
      for line in diff:
        code = line[0]
        s = line[2:]

        if code == ' ':
          result.append((True, [s], [s], rank))
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
              b1, b2 = _parse_diff_to_blocks(first)
              result.append((False, b1, b2, rank))
            b1, b2 = _parse_diff_to_blocks(b[-2:])
            result.append((True, b1, b2, rank))

            usable = False
            b = []
    except Exception as e:
      import traceback
      traceback.print_tb(e.__traceback__)
      print("result: %s")
      printBlocks(result)
      print("_block: %s" % _block)
      print("usable: %s" % usable)

  writeBlocks(path.join(outdir, "_pass_2.txt"), result)
  return result

def _pass_3(outfile, rank, blocks):
  print("_pass_3")

  result = []
  for block in blocks:
    if block[0]:
      result.append(block)
      continue

    tr_vals1 = _append_tr_vals(block[1])
    tr_vals2 = _append_tr_vals(block[2])

    _lcs(tr_vals1, tr_vals2)
    #sys.exit(0)

def _append_tr_vals(b):
  result = []
  for l in b:
    tr = l[:l.index(' ')]
    ts1, ts2 = tr.split(',')
    ms1 = _parse_timestamp(ts1)
    ms2 = _parse_timestamp(ts2)

    result.append([l, (ms1, ms2)])
  return result

def _lcs(x, y):
  len_x = len(x)
  len_y = len(y)

  for _x in x:
    print(_x)
  print()

  for _y in y:
    print(_y)
  print()

  m = [[0 for _ in range(len_y + 1)]]
  for i in range(len_x):
    m.append([0 for _ in range(len_y + 1)])

  m_ = [[0 for _ in range(len_y + 1)]]
  for i in range(len_x):
    m_.append([0 for _ in range(len_y + 1)])

  for i in range(1, len_x + 1):
    for j in range(1, len_y + 1):
      try:
        score = _score(x[i-1][1], y[j-1][1])
        m_[i][j] = score
        m[i][j] = max(m[i-1][j], m[i][j-1], score + m[i-1][j-1])
      except:
        print("(%d, %d)" % (i, j))
        raise Exception()

  for _ in m_:
    print(_)
  for _ in m:
    print(_)
  print()

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
        pairs.append((x[i-1], y[j-1]))
      i -= 1
      j -= 1
    else:
      print("(%d, %d)" % (i, j))
      sys.exit(0)

  print("pairs:")
  for p in pairs:
    print(p[0])
    print(p[1])
    print()

  printSeparator()
  print()


def _score(x, y):
  xa, xb = x
  ya, yb = y

  r = abs(_mid(xa, xb) - _mid(ya, yb))
  r = r if r != 0 else .1

  return (yb - ya) * (xb - xa) / (r * r)

def _mid(x, y):
  return x + (y - x) / 2

def _parse_timestamp(ts):
  hms, ms = ts.split('.')
  h, m, s = hms.split(':')

  return (((int(h) * 60) + int(m)) * 60 + int(s)) * 1000 + int(ms)

def _parse_diff_to_blocks(diff):
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
  if not file:
    return
  with open(file, "w", encoding="utf-8") as f:
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
          f.write(l + "\n")
        f.write("\n")
        for l in b[2]:
          f.write(l + "\n")
        f.write(SEPARATOR + "\n")

def writeBlock(file, block):
  if not file:
    return
  with open(file, "w", encoding="utf-8") as f:
    for line in diff:
      f.write(line.rstrip())
      f.write('\n')

if __name__ == '__main__':
  f1 = webvtt.from_sbv(sys.argv[1])
  f2 = webvtt.from_sbv(sys.argv[2])

  outdir = sys.argv[3] if len(sys.argv) > 3 else None
  diff = merge_sbv(outdir, f1, f2)