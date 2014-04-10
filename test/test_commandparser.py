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
        parser.add("command", int)

    def test_level_1_match(self):
        parser = CommandParser()
        parser.add("!command", int)

        self.assertEqual(parser.parse("!command").handler, int)
        example = parser.parse("!command xxx")
        self.assertEqual(example.handler, int)
        self.assertEqual(example.arguments, "xxx")

        example = parser.parse("!command  xxx")
        self.assertEqual(example.handler, int)
        self.assertEqual(example.arguments, "xxx")

        self.assertEqual(parser.parse("x!command"), None)

    def test_adding_level_2_command(self):
        parser = CommandParser()
        parser.add("command").add("help", int)

    def test_level_2_match(self):
        parser = CommandParser()
        parser.add("command").add("help", int)

        self.assertEqual(parser.parse("command help").handler, int)
        self.assertEqual(parser.parse("command"), None)
        self.assertEqual(parser.parse("command xxx"), None)
        self.assertEqual(parser.parse("command help me"), (int, "me"))

        parser.add("command", str)
        self.assertEqual(parser.parse("command").handler, str)
        self.assertEqual(parser.parse("command help").handler, int)
        self.assertEqual(parser.parse("command xxx"), (str, "xxx"))




if __name__ == '__main__':
    unittest.main()