import collections

_ParseResult = collections.namedtuple('ParseResult', ['handler', 'arguments'])

class CommandParser:
    """Stores information on commands and parses messages"""
    
    def __init__(self):
        self.commands = {}

    def add(self, command, action=None):
        """Add command to parser.

        Examples:
           >>> parser.add("!command", myaction)
           >>> parser.add("!command").add("help", myhelp)
        """
        if isinstance(command, collections.Mapping):
            self._addmap(command)
        else:
            return self._add(command, action)

    def _add(self, command, action=None):
        if command not in self.commands:
            self.commands[command] = CommandParser()

        if action == None:
            return self.commands[command]

        self.commands[command].commands[None] = action

    def _addmap(self, mappable):
        for (key, value) in mappable.iteritems():
            if isinstance(value, collections.Mapping):
                self.commands[key] = CommandParser()
                self.commands[key]._addmap(value)
            else:
                if key is None:
                    self.commands[key] = value
                else:
                    self.commands[key] = CommandParser()
                    self.commands[key].commands[None] = value

    def default(self, action):
        """Add default action"""
        self.commands[None] = action

    def parse(self, msg):
        """Take message and return applicable command.

        Returns:
           Named tuple with fields handler and arguments if successful,
           otherwise None.
        """
        partition = msg.rstrip().partition(" ")
        command = partition[0]
        rest = partition[2].lstrip()

        if command in self.commands:
            return self.commands[command].parse(rest)
        elif None in self.commands:
            return _ParseResult(self.commands[None], msg)
        return None
