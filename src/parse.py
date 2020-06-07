from os import path
from pathlib import Path

import webvtt

SCIRPT_DIR = path.dirname(path.abspath(__file__))
TMP_DIR = path.join(path.dirname(SCIRPT_DIR), "tmp")
Path(TMP_DIR).mkdir(parents=False, exist_ok=True)

def parse_sbv(sbv_path):
  """
  To get around the webvtt library not supporting empty subtitles
  """
  data = None
  with open(sbv_path, "r", encoding="utf-8") as f:
    data = f.readlines()
  
  data_out = []
  lines = []
  for d in data:
    if d != "\n":
      lines.append(d)
      continue

    if len(lines) >= 2:
      data_out.extend(lines)
      data_out.append(d)
    
    lines = []
  
  if len(lines) >= 2:
    data_out.extend(lines)
    
  out_path = path.join(TMP_DIR, path.basename(sbv_path) + ".tmp")
  with open(out_path, "w", encoding="utf-8") as f:
    for d in data_out:
      f.write(d)
  
  return webvtt.from_sbv(out_path)
