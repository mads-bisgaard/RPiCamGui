

class Option:
    """
    Class which encapsulates command line options on remote.
    """
    def __init__(self, name, command, type, pos_val, default):
        """
        :param name:    name of option
        :param command: command passed to raspistill when running it from command line
        :param type:    type of this option (int, string etc)
        :param pos_val: the set of possible values
        :param default: default value
        """
        self.name = name
        self.command = command
        self.type = type
        self.pos_val = pos_val
        self.value = default
