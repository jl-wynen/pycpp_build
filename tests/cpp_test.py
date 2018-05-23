import unittest
import subprocess
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent

class CppTest(unittest.TestCase):
    def test_cpp(self):
        print("\n\nTesting C++ code")
        subprocess.check_call([TEST_DIR/"bin"/"pycpp_build_test"])
        print()

if __name__ == "__main__":
    unittest.main()
