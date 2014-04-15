import unittest
import sys


tests = unittest.defaultTestLoader.discover("test", top_level_dir=".")
unittest.TextTestRunner(stream=sys.stdout).run(tests)