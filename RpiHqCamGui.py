import tkinter as tk
from tkinter import ttk
from Communication import *
import Options as op
from PIL import ImageTk, Image
from ToolTip import CreateToolTip

class RpiHqCamGui:
    """
    Class for handling the GUI for the RPi HQ camera
    """

    def __init__(self, ip, user, pswd, remote_dir, log=False):
        self._root = tk.Tk()
        self._root.title("RPi HQ Camera")
        self._root.geometry('10000x3000')
        self._settingsFrame = ttk.Frame(self._root)
        self._picFrame = ttk.Frame(self._root)
        self._pic = tk.Label(self._picFrame, image='')
        self._settingsFrame.pack()
        self._picFrame.pack()
        self._comObj = RaspiStillCommClass(ip, user, pswd, remote_dir, log=log)
        # Every setting corresponds to one variable in GUI.
        # self._optVars establishes this pairing
        options = self._comObj.getOptions()
        vars = [tk.IntVar(self._settingsFrame, name=opt.name) if isinstance(opt, op.IntOption) else tk.StringVar(self._settingsFrame, name=opt.name) for opt in options]
        self._optVars = list(zip(options, vars))
    
    def _copyCaptureCommand(self):
        """
        Copies command line input in RPi to clipboad
        """
        cmd = self._comObj.getCaptureCommand()
        self._root.clipboard_clear()
        self._root.clipboard_append(cmd)

    def _addSettings(self):
        """
        Add all setting widgets in settings frame
        """
        length = len(self._optVars)
        r = 0
        c = 0
        for ii, optVar in enumerate(self._optVars):
            option, var = optVar
            if ii == int(length/2) + 1:
                r = 0
                c = 1
            lab = ttk.Label(self._settingsFrame, text=option.name)
            lab.grid(row=r, column=c)
            r += 1
            if isinstance(option, op.IntOption):
                var.set(option.value)
                sb = ttk.Spinbox(self._settingsFrame, width=40, from_=option.lb, to=option.ub, textvariable=var)
                sb.bind('<<SpinboxSelected>>', lambda event: self._comObj.setOption(event.widget['textvariable'], event.widget.get()))
                CreateToolTip(sb, option.description)
                sb.grid(row=r, column=c)
                r += 1
            elif isinstance(option, op.GenericOption):
                var.set(str(option.value))
                cb = ttk.Combobox(self._settingsFrame, width=40, textvariable=var)
                cb['values'] = tuple([str(elm) for elm in option.potential_values])
                cb.bind('<<ComboboxSelected>>', lambda event: self._comObj.setOption(event.widget['textvariable'], event.widget.get()))
                CreateToolTip(cb, option.description)
                cb.grid(row=r, column=c)
                r += 1
            else:
                raise Exception('Encountered invalid type of option in RpiHqCamGui')
        r += 4
        btn = ttk.Button(self._settingsFrame, width=82, text='Copy capture command to clipboard')
        btn.grid(row=r, column=0, columnspan=2)
        btn.bind("<Button-1>", self._copyCaptureCommand())
            
    def _getNewFoto(self, event=''):
        self._pic.config(image="")
        self._pic.image = None
        self._comObj.capture()
        img = Image.open(self._comObj._local_img)
        factor = min(self._picFrame.winfo_screenwidth() / img.size[0], self._picFrame.winfo_screenheight() / img.size[1])
        img = img.resize((int(factor * img.size[0]), int(factor * img.size[1])), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self._pic.config(image=img)
        self._pic.image = img
        self._pic.pack(fill='both', expand=1) 

    def run(self):
        self._addSettings()
        self._picFrame.bind('<Return>', lambda event: self._getNewFoto(event))
        self._root.mainloop()


    
if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description='Run Raspberry Pi HQ camera through ultra simple GUI')
    parser.add_argument('ip', help='IP address of RPI')
    parser.add_argument('pswd', help='Password for RPi')
    parser.add_argument('user', help='Username for RPi')
    parser.add_argument('remote_dir', help='Workspace for this program')
    args = parser.parse_args()    
    cam = RpiHqCamGui(args.ip, args.user, args.pswd, args.remote_dir, log=True)
    cam.run()

