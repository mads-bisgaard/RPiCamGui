import tkinter as tk
from tkinter import ttk
from Communication import *

class RpiHqCamGui:
    """
    Class for handling the GUI for the RPi HQ camera
    """

    def __init__(self):
        self._root = tk.Tk()
        self._root.title = "RPi HQ Camera App"
        self._root.attributes('-fullscreen', True)
        self._tabControl = ttk.Notebook(self._root)
        self._settingsTab = ttk.Frame(self._tabControl)
        self._picTab = ttk.Frame(self._tabControl)
        self._tabControl.add(self._settingsTab, text='Settings')
        self._tabControl.add(self._picTab, text='View')
        self._tabControl.pack(expand=1, fill="both")
        
    def _addSettings(self, optionSet):

        for option in optionSet:
            lab = ttk.Label(self._settingsTab, text=option.name).pack()
            #tip = tk.tix.Balloon(self._settingsTab)
            #tk.tip.bind_widget(lab, balloonmsg = option.description)
            if isinstance(option.value, int):
                if isinstance(option.possible_vals, tuple):
                    var = tk.StringVar(self._settingsTab, value=str(option.value), name=option.name)
                    lb, ub = option.possible_vals
                    ttk.Spinbox(self._settingsTab, from_=lb, to=ub, textvariable=var).pack()
                else:
                    print('Currently we cannot handle this kind of option')


    def run(self, commObj):
        self._addSettings(commObj.getOptions())
        self._root.mainloop()


    
if __name__ == '__main__':
    cam = RpiHqCamGui()
    cam.run(commObj)

