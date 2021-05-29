import subprocess
import os
from tkinter import *
from PIL import ImageTk, Image

def piIsAvaliable(ip):
    """
    Ping RPi to make sure it is available on network.
    """
    cmd = 'ping -c 1 ' + ip
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    if res.returncode == 0:
        return True
    else:
        return False

class FotoHandler:

    def __init__(self, ip, user, pswd, root):
        self._ip = ip
        self._user = user
        self._pswd = pswd
        self._root = root
        self._label = Label(root, image="")
        self._img_path = os.path.join(os.path.dirname(__file__), 'image.jpeg')
        self._img = None

    def _takeFoto(self):
        """
        Takes foto and scps it back. Returns path to new foto
        """
        image_name = os.path.split(self._img_path)[1]
        base = "sshpass -p '" + self._pswd + "' "
        takepic = "ssh " + self._user + "@" + self._ip + " \"cd experiments; raspistill -o " + image_name
        takepic += " -co 50 -br 30" + "\""
        getpic = "scp " + self._user + "@" + self._ip + ":~/experiments/" + image_name + " " + self._img_path
        res = subprocess.run(base + takepic, shell=True)
        if res.returncode != 0:
            raise Exception("Could not take pic using RPi")
        res = subprocess.run(base + getpic, shell=True)
        if res.returncode != 0:
            raise Exception("Could not get pic from RPi")        


    def openNewFoto(self, event=''):
        self._label.config(image="")
        self._label.image = None

        self._takeFoto()

        img = Image.open(self._img_path)
        factor = min(self._root.winfo_screenwidth() / img.size[0], self._root.winfo_screenheight() / img.size[1])
        img = img.resize((int(factor * img.size[0]), int(factor * img.size[1])), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self._label.config(image=img)
        self._label.image = img
        self._label.pack(fill=BOTH, expand=1) 

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run Raspberry Pi HQ camera through ultra simple GUI')
    parser.add_argument('ip', help='IP address of RPI')
    parser.add_argument('pswd', help='Password for RPi')
    parser.add_argument('user', help='Username for RPi')
    args = parser.parse_args()

    available = piIsAvaliable(args.ip)
    if not available:
        raise Exception("RPi is not available. Check the IP address.")

    root = Tk()
    root.title("Raspberry Pi HQ camera")
    fh = FotoHandler(args.ip, args.user, args.pswd, root)
    #btn = Button(root, text='take foto', command=fh.openNewFoto).pack()
    key_handler = lambda event : fh.openNewFoto()
    root.bind("<Key>", key_handler)
    root.mainloop()    
    
