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
        file_c = Path(DOCS_DIR, "EP21Chinese.sbv")
        from_file = Path(DOCS_DIR, "EP21Volunteers.sbv")
        to_file = Path(DOCS_DIR, "EP21Carsen.sbv")
        out_file = Path(CURR_DIR.parent, "tmp", "outfile_test_compare.xlsx")

        compare.compare_review(str(file_c), str(from_file), str(to_file), str(out_file))

<<<<<<< HEAD
        pd.read_excel(out_file)
=======
        file_expected = Path(CURR_DIR.parent, "resource", "test_EP21Output.xlsx")
        self.assertTrue(file_expected.is_file())

        df_out = pd.read_excel(file_out)
        df_expected = pd.read_excel(file_expected)

        self.assertTrue(df_out.equals(df_expected))
>>>>>>> More minor clean up

if __name__ == '__main__':
    unittest.main()