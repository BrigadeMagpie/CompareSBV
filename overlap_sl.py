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

  sys.exit(0)
  blocks = _pass3(blocks)

  return diff

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
              result.append((False, first, rank))
            result.append((True, b[-2:], rank))

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


def _pass3(blocks):
  print("_pass3:")

  result = []
  for block in blocks:
    if len(block) <= 2:
      result.append(block)
      continue

    a = []
    b = []
    for line in block:
      code = line[0]
      if code == '-':
        a.append(line[2:27])
        #a.append(line[28:])
        a.append("")
      elif code == '+':
        b.append(line[2:27])
        #b.append(line[28:])
        b.append("")

    differ = Differ()
    diff = differ.compare(a, b)

    for line in diff:
      print(line.rstrip())
    printSeparator()

def printBlock(block):
  for line in block:
    print(line.rstrip())

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