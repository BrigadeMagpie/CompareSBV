#!/usr/bin/env python

import webvtt
from difflib import Differ

def merge_sbv(file, f1, f2):
  d1 = transform_sbv(f1)
  d2 = transform_sbv(f2)

  differ = Differ()
  result = differ.compare(d1, d2)
  diff = list(result)

  #printBlock(diff) 

  blocks = _pass1(diff)
  # printBlocks(blocks)
  writeBlocks(file, blocks)

  # blocks = _pass2(blocks)

  return diff

def transform_sbv(f):
  result = []

  for caption in f:
    lines = [line.rstrip() for line in caption.lines]
    text = "\\n".join(lines)
    result.append("%s,%s %s" % (caption.start, caption.end, text))

  return result

def _pass1(diff):
  result = []
  block = []

  usable = False

  try:
    for line in diff:
      code = line[0]
      
      if code == ' ':
        result.append([line])
      elif code == '-' or code == '+':
        block.append(line)
      elif code == '?':
        if not block:
          continue
        usable = True

      if usable:
        # print("block_: %s" % block)
        # print("line_: %s" % line)

        last_line = block[-1]
        if last_line[0] == '+':
          first = block[:-2]
          if first:
            result.append(first)
          result.append(block[-2:])

          usable = False
          block = []
  except Exception as e:
    import traceback
    traceback.print_tb(e.__traceback__)
    print("result: %s")
    printBlocks(result)
    print("block: %s" % block)
    print("usable: %s" % usable)

  return result


def _pass2(blocks):
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
        a.append(line[28:])
        a.append("")
      elif code == '+':
        b.append(line[2:27])
        b.append(line[28:])
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
  with open(file, "w", encoding="utf-8") as f:
    for block in blocks:
      for line in block:
        f.write(line.rstrip() + "\n")
      f.write("------------------------------------------\n")

def writeBlock(file, block):
  with open(file, "w", encoding="utf-8") as f:
    for line in diff:
      f.write(line.rstrip())
      f.write('\n')

if __name__ == '__main__':
  import sys

  f1 = webvtt.from_sbv(sys.argv[1])
  f2 = webvtt.from_sbv(sys.argv[2])

  diff = merge_sbv(sys.argv[3], f1, f2)