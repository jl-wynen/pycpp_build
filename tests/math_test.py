import unittest
import pycpp_build

class MainTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(pycpp_build.add(1, 1), 2)

    def test_subtract(self):
        self.assertEqual(pycpp_build.subtract(1, 1), 0)

if __name__ == "__main__":
    unittest.main()
