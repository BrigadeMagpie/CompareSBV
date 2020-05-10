import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher, Differ

from parse import parse_sbv
import paths
import matcher
from matcher import IdenticalTimeRangeSubtitleMatcher, DiffSubtitleMatcher, FuzzyTimeRangeSubtitleMatcher

def compare(infile_a, infile_b, infile_f=None, outfile=None):
  sub_a = parse_sbv(infile_a)
  sub_b = parse_sbv(infile_b)

  matchers = [IdenticalTimeRangeSubtitleMatcher(), DiffSubtitleMatcher(), FuzzyTimeRangeSubtitleMatcher()]
  blocks = matcher.merge(sub_a, sub_b, matchers)

  data = unwrap_blocks_with_diff(blocks, True)

  df = None
  df_ = pd.DataFrame(data, columns = ["start", "end", "Translation", "Revised", "word change"])
  if infile_f:
    sub_f = parse_sbv(infile_f)

    data_f = [[sub.start, sub.end, sub.text] for sub in sub_f]
    df_f = pd.DataFrame(data_f, columns = ["start", "end", "Chinese"])

    df_f = df_f.set_index(["start", "end"])
    df_ = df_.set_index(["start", "end"])

    df = df_f.join(df_, how='outer')
    df = df.reset_index(level=["start", "end"])
    df = df[["start", "end", "Chinese", "Translation", "Revised", "word change"]]
  else:
    df = df_

  to_excel(outfile, df)

def unwrap_blocks_with_diff(blocks, word_count=False):
  data = []
  for b in blocks:
    match, b1, b2, _ = b
    if match:
      _b1 = b1[0]
      _b2 = b2[0]

      if word_count:
        wc = 1 - SequenceMatcher(None, _b1.text, _b2.text).ratio()
        data.append([_b2.start, _b2.end, _b1.text, _b2.text, wc])
      else:
        data.append([_b2.start, _b2.end, _b1.text, _b2.text])
    else:
      captions = []
      captions.extend([[_b.start, _b.end, _b.text, ""] for _b in b1])
      captions.extend([[_b.start, _b.end, "", _b.text] for _b in b2])
      captions.sort(key=lambda c: c[0] + c[1])

      data.extend(captions)
  return data

def compare_timeline_only(infile_a, infile_b, outfile=None):
  sub_a = parse_sbv(infile_a)
  sub_b = parse_sbv(infile_b)

  matchers = [IdenticalTimeRangeSubtitleMatcher(), FuzzyTimeRangeSubtitleMatcher()]
  blocks = matcher.merge(sub_a, sub_b, matchers)

  data = unwrap_blocks(blocks)

  if outfile:
    with open(outfile, "w", encoding="utf-8") as f:
      for d in data:
        f.write(";".join([item.replace("\n", "\\n") for item in d]))
        f.write("\n")
  else:
    for d in data:
      print(d)

def unwrap_blocks(blocks):
  data = []
  for block in blocks:
    match, b1, b2, _ = block
    if match:
      _b1 = b1[0]
      _b2 = b2[0]

      data.append([_b1.start, _b1.end, _b1.text, _b2.start, _b2.end, _b2.text])
    else:
      captions = []
      captions.extend([[b.start, b.end, b.text, "", "", ""] for b in b1])
      captions.extend([["", "", "", b.start, b.end, b.text] for b in b2])
      captions.sort(key=lambda c: c[0] + c[1])

      data.extend(captions)
  return data

def to_excel(outfile, df):
  # Output to Excel
  writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
  df.to_excel(writer, sheet_name='Sheet1', index=False)

  workbook  = writer.book
  worksheet = writer.sheets['Sheet1']

  num_cols = len(df.columns)
  sub_cols = num_cols - 3

  sub_col_start = ord('C')
  sub_col_end = sub_col_start + (sub_cols - 1)
  wc_col = sub_col_end + 1

  f_wrap = workbook.add_format({'text_wrap': True})
  f_wc = workbook.add_format({'num_format': '0.00'})

  f_green = workbook.add_format({
    'bg_color': '#C6EFCE',
    'font_color': '#006100'
  })
  f_red = workbook.add_format({
    'bg_color': '#FFC7CE',
    'font_color': '#9C0006'
  })
  f_yellow = workbook.add_format({
    'bg_color': '#FFEB9C',
    'font_color': '#9C6500'
  })

  worksheet.set_column('A:B', 10)
  worksheet.set_column('%s:%s' % (chr(sub_col_start), chr(sub_col_end)), 38, f_wrap)
  worksheet.set_column('%s:%s' % (chr(wc_col), chr(wc_col)),8, f_wc)

  all_rows = '%s2:%s1048576'
  wc_col_format = all_rows % (chr(wc_col), chr(wc_col))
  worksheet.conditional_format(wc_col_format, {
    'type': 'cell',
    'criteria': 'between',
    'minimum': 0.001,
    'maximum': 0.399,
    'format': f_green
  })
  
  worksheet.conditional_format(wc_col_format, {
    'type': 'cell',
    'criteria': 'between',
    'minimum': 0.4,
    'maximum': 0.99,
    'format': f_red
  })

  worksheet.conditional_format(wc_col_format, {
    'type': 'cell',
    'criteria': '>',
    'value': 0.99,
    'format': f_yellow})

  writer.save()

if __name__ == '__main__':
  # pylint: disable=no-value-for-parameter

  import argparse

  parser = argparse.ArgumentParser(description="Utility for comparing different subtitle files.")
  parser.add_argument('original', metavar='original_file', nargs='?', help='original file')
  parser.add_argument('revised', metavar='revised_file', nargs='?', help='revised file')
  parser.add_argument('-f', '--foreign', metavar='foreign_file', help='foreign file')
  parser.add_argument('-o', '--outfile', metavar='out_file', help='file to save to, prints to stdout in csv by default')
  parser.add_argument('-c', '--config', metavar='config_file', help="File with input file paths defined")
  parser.add_argument('--timeline-only', action='store_const', const=True, default=False, help='compare using timelines only')

  args = parser.parse_args()

  print(args)

  FOREIGN_FILE = None
  ORIGINAL_FILE = None
  REVISED_FILE = None
  OUT_FILE = None

  if args.config:
    from runpy import run_path
    settings = run_path(args.config)

    FOREIGN_FILE = settings["CHINESE_FILE"]
    ORIGINAL_FILE = settings["ORIGINAL_FILE"]
    REVISED_FILE = settings["REVISED_FILE"]
    OUT_FILE = settings["OUT_FILE"]
  else:
    FOREIGN_FILE = args.foreign
    ORIGINAL_FILE = args.original
    REVISED_FILE = args.revised
    OUT_FILE = args.outfile
  
  if not args.timeline_only:
    compare(ORIGINAL_FILE, REVISED_FILE, infile_f=FOREIGN_FILE, outfile=OUT_FILE)
  else:
    compare_timeline_only(ORIGINAL_FILE, REVISED_FILE, outfile=OUT_FILE)
