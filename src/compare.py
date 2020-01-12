import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher, Differ

from sub_parser import parse_sbv
import paths
import overlap

def compare(infile_c, infile_a, infile_b, outfile):
  # print("%s, %s, %s" % (infile_a, infile_b, outfile))

  sub_c = parse_sbv(infile_c)
  sub_a = parse_sbv(infile_a)
  sub_b = parse_sbv(infile_b)

  blocks = overlap.merge(sub_a, sub_b)

  data = []
  for b in blocks:
    match, b1, b2, _ = b
    if match:
      _b1 = b1[0]
      _b2 = b2[0]

      wc = 1 - SequenceMatcher(None, _b1.text, _b2.text).ratio()
      data.append([_b2.start, _b2.end, _b1.text, _b2.text, wc])
    else:
      captions = []
      captions.extend([(_b, 1) for _b in b1])
      captions.extend([(_b, 2) for _b in b2])

      captions.sort(key=lambda c: c[0].start)

      for c in captions:
        _b = c[0]
        if c[1] == 1:
          data.append([_b.start, _b.end, _b.text, ""])
        else:
          data.append([_b.start, _b.end, "", _b.text])


  if False:
    verify_a = []
    for d in data:
      if d[2]:
        verify_a.append(d[2])

    expected_a = [cap.text for cap in sub_a]

    diff = list(Differ().compare(expected_a, verify_a))
    for d in diff:
      print(d)
    print(len(sub_a))
    print(len(verify_a))

  data_c = [[sub.start, sub.end, sub.text] for sub in sub_c]
  df_c = pd.DataFrame(data_c, columns = ["start", "end", "Chinese"])
  df_ = pd.DataFrame(data, columns = [
    "start", "end", "Translation", "Revised", "word change"])

  df_c = df_c.set_index(["start", "end"])
  df_ = df_.set_index(["start", "end"])

  df = df_c.join(df_, how='outer')
  df = df.reset_index(level=["start", "end"])
  df = df[["start", "end", "Chinese", "Translation", "Revised", "word change"]]

  _to_excel(outfile, df)

def _to_excel(outfile, df):
  # Output to Excel
  writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
  df.to_excel(writer, sheet_name='Sheet1', index=False)

  workbook  = writer.book
  worksheet = writer.sheets['Sheet1']

  f_wrap = workbook.add_format({'text_wrap': True})
  f_wc = workbook.add_format({'num_format': '0.00'})
  worksheet.set_column('A:B', 14)
  worksheet.set_column('C:E', 38, f_wrap)
  worksheet.set_column('F:F',12, f_wc)

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

  worksheet.conditional_format('F2:F1048576', {
    'type': 'cell',
    'criteria': '<',
    'value': 0.4,
    'format': f_green
  })

  worksheet.conditional_format('F2:F1048576', {
    'type': 'cell',
    'criteria': 'between',
    'minimum': 0.4,
    'maximum': 0.99,
    'format': f_red
  })

  worksheet.conditional_format('F2:F1048576', {
    'type': 'cell',
    'criteria': '>',
    'value': 0.99,
    'format': f_yellow})

  writer.save()

if __name__ == '__main__':
  import sys

  if len(sys.argv) == 5:
    compare(*sys.argv[1:5])
  else:
    compare(*paths.PATHS)
