import pandas as pd
import webvtt
from datetime import datetime

import overlap

def compare(infile_a, infile_b, outfile):
  # print("%s, %s, %s" % (infile_a, infile_b, outfile))

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
      data.append([_b1.start, _b1.end, _b2_start, _b2_end, _b1.text, _b2.text])

  df = pd.DataFrame(data, columns = ["start", "end", "start", "end", "old", "new"])

  # Write to Excel file with formats
  writer = pd.ExcelWriter(outfile, engine='xlsxwriter') #https://xlsxwriter.readthedocs.io/index.html
  df.to_excel(writer, sheet_name='Sheet1', index=False)
  # Get the xlsxwriter objects from the dataframe writer object.
  workbook  = writer.book
  worksheet = writer.sheets['Sheet1']
  # Set the column width and format.
  format1 = workbook.add_format({'text_wrap': True})
  worksheet.set_column('A:D', 18)
  worksheet.set_column('E:F', 55, format1)

  # Close the Pandas Excel writer and output the Excel file.
  writer.save()

if __name__ == '__main__':
  import sys

  if len(sys.argv) < 3:
    raise Exception("Missing arguments.")

  compare(*sys.argv[1:4])

"""
File paths
InOriginal = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\Youtube LeTV Published\\EP20volunteers.sbv"
InRevised = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\Youtube LeTV Published\\EP20 Sept21.sbv"
OutFile = "C:\\Users\\Jiachen\\OneDrive\\YouTube Subtitles\\测试 培训\\Carsen修改前后对比\\EP20组会20190922.xlsx"
"""