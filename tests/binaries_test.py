"""
Run compiled unit tests.

Executes all executables in directory bin relative to this script.
"""

import unittest
import os
from pathlib import Path
import subprocess

_TEST_DIR = Path(__file__).resolve().parent
_BINARY_DIR = _TEST_DIR/"bin"

def _get_executables(path):
    "Generator iterating over all executables in path."
    for fil in Path(path).iterdir():
        if fil.is_file() and os.access(str(fil), os.X_OK):
            yield fil

class BinTest(unittest.TestCase):
    "Run all compiled tests in BINARY_DIR."

    def test_binaries(self):
        "Execute the tests."
        print("Testing C++ code")
        for exe in _get_executables(_BINARY_DIR):
            print(f"\nRunning {exe}")
            subprocess.check_call([str(exe)])

if __name__ == "__main__":
    unittest.main()
