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

        self.assertEqual(parser.parse("!command\n").handler, int)

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

    def test_level_3_match(self):
        parser = CommandParser()
        parser.add("c1").add("c2").add("c3", int)
        parser.add("c1").add("c2", str)

        self.assertEqual(parser.parse("c1 c2 c3 xxx"), (int, "xxx"))
        self.assertEqual(parser.parse("c1 c2 c3 "), (int, ""))
        self.assertEqual(parser.parse("c1 c2 xxx"), (str, "xxx"))
        self.assertEqual(parser.parse("c1"), None)

    def test_adding_level_1_map(self):
        parser = CommandParser()
        parser.add({
            "command" : int,
            "another" : float
        })

        self.assertEqual(parser.parse("command").handler, int)
        self.assertEqual(parser.parse("command xxx"), (int, "xxx"))

        self.assertEqual(parser.parse("another").handler, float)

    def test_adding_level_2_map(self):
        parser = CommandParser()
        parser.add({
            "command" : {
                None : int,
                "add" : float
            }
        })

        self.assertEqual(parser.parse("command xxx"), (int, "xxx"))
        self.assertEqual(parser.parse("command add xxx"), (float, "xxx"))


    def test_adding_level_3_map(self):
        parser = CommandParser()
        parser.add({
            "command" : {
                None : int,
                "add" : float,
                "sub" : {
                    "add" : str,
                    "remove" : int
                }
            },
            "command2" : str
        })

        self.assertEqual(parser.parse("command xxx"), (int, "xxx"))
        self.assertEqual(parser.parse("command2 xxx"), (str, "xxx"))
        self.assertEqual(parser.parse("command add xxx"), (float, "xxx"))
        self.assertEqual(parser.parse("command sub add xxx"), (str, "xxx"))
        self.assertEqual(parser.parse("command sub remove xxx"), (int, "xxx"))


if __name__ == '__main__':
    unittest.main()