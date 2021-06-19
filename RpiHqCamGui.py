import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
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
        self._pic = tk.Label(self._picFrame, image=None)
        self._settingsFrame.pack()
        self._picFrame.pack()
        self._comObj = RaspiStillCommClass(ip, user, pswd, remote_dir, log=log)
        self._img = None
        # Every setting corresponds to one variable in GUI.
        # self._optVars establishes this pairing
        options = self._comObj.getOptions()
        vars = [tk.IntVar(self._settingsFrame, name=opt.name) if isinstance(opt, op.IntOption) else tk.StringVar(self._settingsFrame, name=opt.name) for opt in options]
        self._optVars = list(zip(options, vars))
        self._buttons = [ ttk.Button(self._settingsFrame, width=82) for _ in range(2) ]
    
    def __del__(self):
        del self._comObj

    def _copyCaptureCommand(self):
        """
        Copies command line input in RPi to clipboad
        """
        cmd = self._comObj.getCaptureCommand()
        self._root.clipboard_clear()
        self._root.clipboard_append(cmd)

    def _savePic(self):
        """
        Callback for saving picture
        """
        if self._img is None:
            return
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".jpeg")
        if not filename:
            return
        self._img.save(filename)

    def _constructSettings(self):
        """
        Build the settings user interface
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
        r += 2
        btn1 = ttk.Button(self._settingsFrame, width=82, text='Copy capture command to clipboard')
        btn1.grid(row=r, column=0, columnspan=2)
        btn1.bind("<Button-1>", lambda event: self._copyCaptureCommand())
        r += 2
        btn2 = ttk.Button(self._settingsFrame, width=82, text='Save picture')
        btn2.grid(row=r, column=0, columnspan=2)
        btn2.bind("<Button-1>", lambda event: self._savePic())

    def _showSettings(self):
        self._settingsFrame.pack()
        self._picFrame.pack_forget()

    def _getAndShowFoto(self, event=''):
        self._pic.config(image="")
        self._pic.image = None
        self._comObj.capture()
        img = Image.open(self._comObj._local_img)
        factor = min(self._picFrame.winfo_screenwidth() / img.size[0], self._picFrame.winfo_screenheight() / img.size[1])
        self._img = img.resize((int(factor * img.size[0]), int(factor * img.size[1])), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(self._img)
        self._pic.config(image=img)
        self._pic.image = img
        self._picFrame.pack(fill='both', expand=1)
        self._pic.pack(fill='both', expand=1)
        self._settingsFrame.pack_forget()

    def run(self):
        """
        Runs GUI. Note the RpiHqCamGui object is deleted after running this fcn.
        """
        self._constructSettings()
        self._root.bind("<Return>", lambda event: self._getAndShowFoto(event))
        self._root.bind('<BackSpace>', lambda event: self._showSettings())
        self._root.mainloop()
        del self

    
if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description='Run Raspberry Pi HQ camera through ultra simple GUI')
    parser.add_argument('ip', help='IP address of RPI')
    parser.add_argument('pswd', help='Password for RPi')
    parser.add_argument('user', help='Username for RPi')
    parser.add_argument('remote_dir', help='Workspace for this program')
    args = parser.parse_args()    
    cam = RpiHqCamGui(args.ip, args.user, args.pswd, args.remote_dir, log=False)
    cam.run()

