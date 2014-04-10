import unittest
from helpers.commandparser import CommandParser

class TestCommandParser(unittest.TestCase):

    def test_creating_parser(self):
        parser = CommandParser()


if __name__ == '__main__':
    unittest.main()