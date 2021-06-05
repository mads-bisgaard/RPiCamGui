

class Option:
    """
    Class which encapsulates command line options on remote.
    """
    def __init__(self, command, name, descr, default):
        """
        :param name:    name of option
        :param command: command passed to raspistill when running it from command line
        :param pos_val: the set of possible values
        :param default: default value
        """
        self.name = name
        self.command = command
        self.description = descr
        self.value = default

        self._set_budy = None # field used to fetch identical twin in set.

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        """
        This hash ensures that a set of options only contains a single option 
        with a given name
        """        
        val = self.name == other.name
        if val:
            self._set_budy = other
            other._set_budy = self
        return val

    def __lt__(self, other):
        """
        Allows us to sort a set of options in a way consistent with __eq__
        """
        return self.name < other.name

    def getSetBudy(self):
        return self._set_budy


class IntOption(Option):
    """
    Class defining integer options
    """
    def __init__(self, command, name, descr, lb, ub, default):
        super(IntOption, self).__init__(command, name, descr, default)
        self.lb = lb
        self.ub = ub

class GenericOption(Option):
    """
    Class defining String options
    """
    def __init__(self, command, name, descr, potential_values, default):
        super(GenericOption, self).__init__(command, name, descr, default)
        self.potential_values = potential_values

