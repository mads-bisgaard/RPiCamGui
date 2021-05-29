import tkinter as tk

def getRangeList(lb, ub):
    """
    Construct a list of strings with given range
    """
    return [ str(elm) for elm in range(lb, ub) ]

def getCenterVal(li):
    """
    Get the center value of a list
    """
    return li[ int(len(li)/2) ]



class RpiHqCamGui:
    """
    Class for handling the GUI for the RPi HQ camera
    """

    def __init__(self):
        self._app = tk.Tk()
        self._app.title = "RPi HQ Camera App"
        self._app.attributes('-fullscreen', True)
        
        var = tk.StringVar(self._app)
        var.set()
        var.trace()
        
