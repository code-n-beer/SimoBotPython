import unittest
from helpers.commandparser import CommandParser

class TestCommandParser(unittest.TestCase):

    def test_creating_parser(self):
        parser = CommandParser()

    def test_no_matches(self):
        parser = CommandParser()
        self.assertEqual(parser.parse("command"), None)

    def test_adding_level_1_command(self):
        parser = CommandParser()
        parser.add("command", None)

    def test_level_1_match(self):
        parser = CommandParser()
        parser.add("!command", int)

        self.assertEqual(parser.parse("!command").function, int)
        example = parser.parse("!command xxx")
        self.assertEqual(example.function, int)
        self.assertEqual(example.arguments, "xxx")

        example = parser.parse("!command  xxx")
        self.assertEqual(example.function, int)
        self.assertEqual(example.arguments, "xxx")

        self.assertEqual(parser.parse("x!command"), None)



if __name__ == '__main__':
    unittest.main()