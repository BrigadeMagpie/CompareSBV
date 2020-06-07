import unittest
import sys
from pathlib import Path

import compare

SUB_DIR = Path('/Users/shun/code/magpie-dict/resource/subtitles/zhz')
OUT_DIR = Path('/Users/shun/code/magpie-dict/resource/data/zhz')

class TestCompare(unittest.TestCase):

    def test_compareall(self):
        dir_a = Path(SUB_DIR, 'a')
        dir_b = Path(SUB_DIR, 'b')

        for fb in dir_b.iterdir():
            fname = fb.name
            fa = Path(dir_a, fname)

            fout_name = fname.split(".")[0] + ".csv"

            fout = Path(OUT_DIR, fout_name)
            print(fa, fb, fout)
            OUT_DIR.mkdir(exist_ok=True)
            compare.compare_timeline_only(fa, fb, outfile=fout)

if __name__ == '__main__':
    unittest.main()