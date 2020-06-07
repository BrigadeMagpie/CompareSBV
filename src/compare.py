import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher, Differ

from parse import parse_sbv
import paths
import matcher
from matcher import IdenticalTimeRangeSubtitleMatcher, DiffSubtitleMatcher, FuzzyTimeRangeSubtitleMatcher

def compare_review(from_file, to_file, ref_file=None, out_file=None, no_diff=False):
  sub_a = parse_sbv(from_file)
  sub_b = parse_sbv(to_file)

  matchers = [IdenticalTimeRangeSubtitleMatcher()]
  if not no_diff:
    matchers.append(DiffSubtitleMatcher())
  matchers.append(FuzzyTimeRangeSubtitleMatcher())
  blocks = matcher.merge(sub_a, sub_b, matchers)

  data = format_blocks_review(blocks, True)

  df = None
  df_ = pd.DataFrame(data, columns = ["start", "end", "Translation", "Revised", "word change"])
  if ref_file:
    sub_f = parse_sbv(ref_file)

    data_f = [[sub.start, sub.end, sub.text] for sub in sub_f]
    df_f = pd.DataFrame(data_f, columns = ["start", "end", "Chinese"])

    df_f = df_f.set_index(["start", "end"])
    df_ = df_.set_index(["start", "end"])

    df = df_f.join(df_, how='outer')
    df = df.reset_index(level=["start", "end"])
    df = df[["start", "end", "Chinese", "Translation", "Revised", "word change"]]
  else:
    df = df_

  to_excel(out_file, df)

def format_blocks_review(blocks, word_count=False):
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

<<<<<<< HEAD
=======
def compare_timeline_only(infile_a, infile_b, outfile=None):
  sub_a = parse_sbv(infile_a)
  sub_b = parse_sbv(infile_b)

  matchers = [IdenticalTimeRangeSubtitleMatcher(), FuzzyTimeRangeSubtitleMatcher()]
  blocks = matcher.merge(sub_a, sub_b, matchers)

  data = unwrap_blocks(blocks)

  df = pd.DataFrame(data)
  csv_str = df.to_csv(outfile, header=False, index=False)
  if not outfile:
    print(csv_str)

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

>>>>>>> Adding compareall
def to_excel(outfile, df):
  # pylint: disable=abstract-class-instantiated
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

def compare_database(from_file, to_file, out_file=None):
  sub_a = parse_sbv(from_file)
  sub_b = parse_sbv(to_file)

  matchers = [IdenticalTimeRangeSubtitleMatcher(), FuzzyTimeRangeSubtitleMatcher()]
  blocks = matcher.merge(sub_a, sub_b, matchers)

  data = format_blocks_database(blocks)
  df = pd.DataFrame(data)

  to_csv(out_file, df)

def format_blocks_database(blocks):
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

def to_csv(out_file, df):
  s = df.to_csv(out_file, header=False, index=False)
  if s:
    print(s)

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser(description="Utility for comparing different versions of subtitle files.")
  parser.add_argument('-c', '--config', metavar='CONFIG_FILE', help="configuration file with *_FILE supplied")
  parser.add_argument('-o', '--outfile', metavar='OUT_FILE', help='file to save to, prints to stdout in csv if not supplied')
  parser.add_argument('-f', '--format', default='review', choices= ['review', 'database'], help="defaults to 'review'")
  parser.add_argument('-nd', '--no-diff', action='store_const', const=True, default=False, help="compare without diff matcher, should be used when comparing different languages, only applicable to 'review' format")
  parser.add_argument('from_file', metavar='FROM_FILE', nargs='?', help='file to compare from')
  parser.add_argument('to_file', metavar='TO_FILE', nargs='?', help='file to compare to')
  parser.add_argument('ref_file', metavar='REF_FILE', nargs='?', help='file used as reference, is merged directly with no comparisons')

  args = parser.parse_args()

  FROM_FILE = None
  TO_FILE = None
  REF_FILE = None
  OUT_FILE = None

  if args.config:
    from runpy import run_path
    settings = run_path(args.config)

    REF_FILE = settings['CHINESE_FILE'] if 'CHINESE_FILE' in settings else settings['REF_FILE'] if 'REF_FILE' in settings else None
    FROM_FILE = settings['ORIGINAL_FILE'] if 'ORIGINAL_FILE' in settings else settings['FROM_FILE'] if 'FROM_FILE' in settings else None
    TO_FILE = settings['REVISED_FILE'] if 'REVISED_FILE' in settings else settings['TO_FILE'] if 'TO_FILE' in settings else None
    OUT_FILE = settings['OUT_FILE']
  else:
    REF_FILE = args.ref_file
    FROM_FILE = args.from_file
    TO_FILE = args.to_file
    OUT_FILE = args.outfile
  
  if not FROM_FILE:
    raise Exception("Missing FROM_FILE.")

  if not TO_FILE:
    raise Exception("Missing TO_FILE.")
  
  if args.format == 'review':
    compare_review(FROM_FILE, TO_FILE, ref_file=REF_FILE, out_file=OUT_FILE, no_diff=args.no_diff)
  else:
    compare_database(FROM_FILE, TO_FILE, OUT_FILE)
