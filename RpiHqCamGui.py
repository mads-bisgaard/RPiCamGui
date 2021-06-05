import tkinter as tk
from tkinter import ttk
from Communication import *
import Options as op
from PIL import ImageTk, Image

class RpiHqCamGui:
    """
    Class for handling the GUI for the RPi HQ camera
    """

    def __init__(self):
        self._root = tk.Tk()
        self._root.title = "RPi HQ Camera App"
        self._root.geometry('10000x3000')
        self._tabControl = ttk.Notebook(self._root)
        self._settingsTab = ttk.Frame(self._tabControl)
        self._picTab = ttk.Frame(self._tabControl)
        self._pic = tk.Label(self._picTab, image='')
        self._tabControl.add(self._settingsTab, text='Settings')
        self._tabControl.add(self._picTab, text='View')
        self._tabControl.pack(expand=1, fill="both")
        
    def _addSettings(self, commObj):

        for option in commObj.getOptions():
            lab = ttk.Label(self._settingsTab, text=option.name).pack()
            #tip = tk.tix.Balloon(self._settingsTab)
            #tk.tip.bind_widget(lab, balloonmsg = option.description)
            if isinstance(option, op.IntOption):
                var = tk.StringVar(self._settingsTab, name=option.name)
                var.set(str(option.value))
                #var.trace('w', lambda : commObj.setOption(option.name, int(var.get())))
                sb = ttk.Spinbox(self._settingsTab, width=40, from_=option.lb, to=option.ub, textvariable=var)
                sb.bind('<<SpinboxSelected>>', lambda event: commObj.setOption(event.widget['textvariable'], int(event.widget.get())))
                sb.pack()
                #sb.pack(ipadx=20, pady=20)
            elif isinstance(option, op.GenericOption):
                var = tk.StringVar(self._settingsTab, name=option.name)
                var.set(str(option.value))
                #var.trace('w', lambda : commObj.setOption(option.name, var.get()))
                cb = ttk.Combobox(self._settingsTab, width=40, value=str(option.value), textvariable=var)
                cb['values'] = tuple([str(elm) for elm in option.potential_values])
                cb.bind('<<ComboboxSelected>>', lambda event: commObj.setOption(event.widget['textvariable'], event.widget.get()))
                cb.pack()
                #cb.pack(ipadx=20, pady=20)
            else:
                raise Exception('Encountered invalid type of option in RpiHqCamGui')

    def _getNewFoto(self, commObj, event=''):
        self._pic.config(image="")
        self._pic.image = None
        commObj.capture()
        img = Image.open(commObj._local_img)
        factor = min(self._picTab.winfo_screenwidth() / img.size[0], self._picTab.winfo_screenheight() / img.size[1])
        img = img.resize((int(factor * img.size[0]), int(factor * img.size[1])), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self._pic.config(image=img)
        self._pic.image = img
        self._pic.pack(fill='both', expand=1) 

    def run(self, commObj):
        self._addSettings(commObj)
        self._picTab.bind('<Return>', lambda event: self._getNewFoto(commObj, event))
        self._root.mainloop()


    
if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description='Run Raspberry Pi HQ camera through ultra simple GUI')
    parser.add_argument('ip', help='IP address of RPI')
    parser.add_argument('pswd', help='Password for RPi')
    parser.add_argument('user', help='Username for RPi')
    parser.add_argument('remote_dir', help='Workspace for this program')
    args = parser.parse_args()    
    commObj = RaspiStillCommClass(args.ip, args.user, args.pswd, args.remote_dir, log=True)    
    cam = RpiHqCamGui()
    cam.run(commObj)

