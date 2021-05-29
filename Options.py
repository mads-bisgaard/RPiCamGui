

class Option:
    """
    Class which encapsulates command line options on remote.
    """
    def __init__(self, name, command, possible_vals, default):
        """
        :param name:    name of option
        :param command: command passed to raspistill when running it from command line
        :param pos_val: the set of possible values
        :param default: default value
        """
        self.name = name
        self.command = command
        self.possible_vals = possible_vals
        self.value = default

    def __hash__(self):
        return hash(self.command)

    def __eq__(self, other):
        """
        This hash ensures that a set of options only contains a single option 
        with a given command
        """        
        return self.command == other.command

    def __lt__(self, other):
        """
        Allows os to sort a set of options in a way consistent with __eq__
        """
        return self.command < other.command


