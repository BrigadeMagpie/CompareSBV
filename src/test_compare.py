import unittest
import sys
from pathlib import Path
import filecmp

import pandas as pd

import compare

CURR_DIR = Path(__file__).resolve().parent
DOCS_DIR = Path(CURR_DIR.parent, "docs")

class TestCompare(unittest.TestCase):

    def test_compare(self):
        file_c = Path(DOCS_DIR, "EP21 Original.sbv")
        file_a = Path(DOCS_DIR, "EP21 Volunteers.sbv")
        file_b = Path(DOCS_DIR, "EP21 Carsen.sbv")
        file_out = Path(CURR_DIR.parent, "tmp", "outfile_test_compare.xlsx")

        compare.compare(str(file_c), str(file_a), str(file_b), str(file_out))

        file_expected = Path(CURR_DIR.parent, "resource", "outfile_test_compare_expected.xlsx")
        self.assertTrue(file_expected.is_file())

        df_out = pd.read_excel(file_out)
        df_expected = pd.read_excel(file_expected)

        self.assertTrue(df_out.equals(df_expected))

if __name__ == '__main__':
    unittest.main()