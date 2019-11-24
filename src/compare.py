import pandas as pd
import webvtt
from datetime import datetime
from difflib import SequenceMatcher

import overlap

def compare(infile_c, infile_a, infile_b, outfile):
  # print("%s, %s, %s" % (infile_a, infile_b, outfile))

  sub_c = webvtt.from_sbv(infile_c)
  sub_a = webvtt.from_sbv(infile_a)
  sub_b = webvtt.from_sbv(infile_b)

  blocks = overlap.merge(sub_a, sub_b)

  data = []
  for b in blocks:
    match, b1, b2, _ = b
    if match:
      _b1 = b1[0]
      _b2 = b2[0]

      _b2_start = _b2.start if _b1.start != _b2.start else "-"
      _b2_end = _b2.end if _b1.end != _b2.end else "-"
      wc = 1 - SequenceMatcher(None, _b1.text, _b2.text).ratio()
      data.append([_b1.start, _b1.end, _b2_start, _b2_end, _b1.text, _b2.text, wc])
    else:
      captions = []
      captions.extend([(_b, 1) for _b in b1])
      captions.extend([(_b, 2) for _b in b2])

      captions.sort(key=lambda c: c[0].start)

      for c in captions:
        _b = c[0]
        if c[1] == 1:
          data.append([_b.start, _b.end, "-", "-", _b.text, ""])
        else:
          data.append([_b.start, _b.end, _b.start, _b.end, "", _b.text])

  data_c = [[sub.start, sub.end, sub.text] for sub in sub_c]
  df_c = pd.DataFrame(data_c, columns = ["start", "end", "Chinese"])
  df_ = pd.DataFrame(data, columns = [
    "start", "end", "start (revised)", "end (revised)", "Translation", "Revised", "word change"])

  df_c = df_c.set_index(["start", "end"])
  df_ = df_.set_index(["start", "end"])

  df = df_c.join(df_, how='outer')
  df = df.reset_index(level=["start", "end"])
  df = df[["start", "end", "start (revised)", "end (revised)", "Chinese", "Translation", "Revised", "word change"]]

  df.loc[df["Translation"] == "", ["start", "end"]] = "-"

  _to_excel(outfile, df)

def _to_excel(outfile, df):
  # Output to Excel
  writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
  df.to_excel(writer, sheet_name='Sheet1', index=False)

  workbook  = writer.book
  worksheet = writer.sheets['Sheet1']

  f_wrap = workbook.add_format({'text_wrap': True})
  f_wc = workbook.add_format({'num_format': '0.00'})
  worksheet.set_column('A:D', 24)
  worksheet.set_column('E:G', 55, f_wrap)
  worksheet.set_column('H:H',12, f_wc)

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

  worksheet.conditional_format('H2:H1048576', {
    'type': 'cell',
    'criteria': '<',
    'value': 0.4,
    'format': f_green
  })

  worksheet.conditional_format('H2:H1048576', {
    'type': 'cell',
    'criteria': 'between',
    'minimum': 0.4,
    'maximum': 0.99,
    'format': f_red
  })

  worksheet.conditional_format('H2:H1048576', {
    'type': 'cell',
    'criteria': '>',
    'value': 0.99,
    'format': f_yellow})

  writer.save()

if __name__ == '__main__':
  import sys

  if len(sys.argv) < 4:
    raise Exception("Missing arguments.")

  compare(*sys.argv[1:5])
