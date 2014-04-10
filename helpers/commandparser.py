import collections

_ParseResult = collections.namedtuple('ParseResult', ['function', 'arguments'])

class CommandParser:
    """Stores information on commands and parses messages"""
    
    def __init__(self):
        self.commands = {}

    def add(self, command, action):
        """Add command to parser."""
        self.commands[command] = action

    def parse(self, msg):
        """Take message and return applicable command.

        Returns:
           Named tuple with fields function and arguments if successful,
           otherwise None.
        """
        partition = msg.partition(" ")
        command = partition[0]
        rest = partition[2].lstrip()
        if command in self.commands:
            return _ParseResult(self.commands[command], rest)
        return None
