
import paramiko
import Options as op
import os
from datetime import datetime

class BaseCommClass:
    """
    Class for handling communication between RPi and host.
    An object of this class manages an ssh connection along with SFTP file transfer between host and RPi
    """
    def __init__(self, ip, user, pswd, log=False):
        """
        :param log:     If set True the remote log will be written rpi_stdout and rpi_stderr
        """
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(hostname=ip, username=user, password=pswd)
        self._sftp = self._ssh.open_sftp()
        self._rpi_stdout = None
        self._rpi_stderr = None
        if log:
            self._rpi_stdout = open('rpi_stdout', 'w+')
            self._rpi_stderr = open('rpi_stderr', 'w+')
    
    def __del__(self):
        self._ssh.close()
        self._sftp.close()
        if self._rpi_stdout is not None:
            self._rpi_stdout.close()
        if self._rpi_stderr is not None:
            self._rpi_stderr.close()

    def _runCommand(self, command, stdin=None):
        """
        Runs a command on the remote machine and logs if requested

        :param command:     Command to run on remote machine
        :param stdin:       Command to pass to stdin on remote if needed
        """
        ssh_stdin, ssh_stdout, ssh_stderr = self._ssh.exec_command(command)
        if stdin is not None:
            ssh_stdin.channel.send(stdin)
        if self._rpi_stdout is not None:
            out = ssh_stdout.read().decode(encoding='UTF-8')
            self._rpi_stdout.write(out)
        if self._rpi_stderr is not None:
            self._rpi_stderr.write(ssh_stderr.read().decode(encoding='UTF-8'))
    
    def _get(self, remote_pth, local_pth):
        """
        Get a file from remote to local

        :param remote_pth:  path on remote
        :param local_pth:   path on local machine
        """
        self._sftp.get(remote_pth, local_pth)

    def _put(self, remote_pth, local_pth):
        """
        Put a file from local to remote

        :param remote_pth:  path on remote
        :param local_pth:   path on local machine
        """    
        self._sftp.put(local_pth, remote_pth)


class RaspiStillCommClass(BaseCommClass):
    """
    Class for run raspistill on RPi
    """
    def __init__(self, ip, user, pswd, remote_dir, log=False):
        super().__init__(ip, user, pswd, log)
        self._options = self._generateDefaultOptions()
        self._sftp.chdir(remote_dir) #make sure we are in correct remote dir
        self._local_img = None        
        self._remote_img = 'img.jpeg'

    def __del__(self):
        if self._remote_img is not None:
            self._sftp.remove(self._remote_img)
        if self._local_img is not None:
            os.remove(self._local_img)
        super().__del__()

    def _generateDefaultOptions(self):
        """
        Generates the default options for running Raspistill on remote
        """
        res = []
        fi = lambda cmd, name, descr, lb, ub, d: res.append( op.IntOption(cmd, name, descr, lb, ub, d) ) 
        fg = lambda cmd, name, descr, ran, d: res.append( op.GenericOption(cmd, name, descr, ran, d) ) 
        fi("-sh", "sharpness", "Set image sharpness", -100, 100, 0)
        fi( "-co", "contrast", "Set image contrast", -100, 100, 0 )
        fi( "-br", "brightness", "Set image brightness", 0, 100, 50 )
        fi( "-sa", "saturation", "Set image saturation", -100,100, 0)
        fi( "-ISO", "ISO", "Set capture ISO" , 100, 800, 400)
        # this one is not working on RPi (probably only for raspivid)
        #f( "-vs", "vidstab", "Turn on video stabilisation", [0, 1], 0)
        fi( "-ev", "EV", "Set EV compensation", -10, 10, 0 )
        fg( "-ex", "exposure", "Set exposure mode", ["off", "auto", "night", "nightpreview", "backlight", "spotlight", "sports", "snow", "beach", "verylong", "fixedfps", "antishake", "fireworks"], "off")
        fg("-fli", "flicker", "Set flicker avoid mode", ["off", "auto", "50hz", "60hz"], "off")
        fg("-awb", "awb", "Set AWB mode", ["off", "auto", "sun", "cloud", "shade", "tungsten", "fluorescent", "incandescent", "flash", "horizon", "greyworld"], "off")
        fg("-ifx", "imxfx", "Set image effect", ["none", "negative", "solarise", "sketch", "denoise", "emboss", "oilpaint", "hatch", "gpen", "pastel", "watercolour", "film", "blur", "saturation", "colourswap", "washedout", "posterise", "colourpoint", "colourbalance", "cartoon"], "none")
        # Currently  colour effect is not dealt with because it requires a pair of numbers
        # f("-cfx", "colfx", "Set colour effect" (U:V)
        fg("-mm", "metering", "Set metering mode", ["average", "spot", "backlit", "matrix"], "average")
        fg("-rot", "rotation", "Set image rotation", [0, 90, 180, 270], 0)
        #f("-hf", "hflip", "Set horizontal flip", [0, 1], 0)
        #f("-vf", "vflip", "Set vertical flip", [0, 1], 0)
        # Currently roi is not dealt with because it requires a quadruple of numbers
        # f("-roi", "roi", "Set region of interest (x,y,w,d as normalised coordinates [0.0-1.0])
        # f("-ss", "shutter", "Set shutter speed in microseconds", (0, 200000000)
        # -awbg, --awbgains	: Set AWB gains - AWB mode must be off
        fg("-drc", "DRC", "Set DRC Level", ["off", "low", "med", "high"], "off")
        #-st, --stats	: Force recomputation of statistics on stills capture pass
        #-a, --annotate	: Enable/Set annotate flags or text
        #-3d, --stereo	: Select stereoscopic mode
        #-dec, --decimate	: Half width/height of stereo image
        #-3dswap, --3dswap	: Swap camera order for stereoscopic
        #-ae, --annotateex	: Set extra annotation parameters (text size, text colour(hex YUV), bg colour(hex YUV), justify, x, y)
        #-ag, --analoggain	: Set the analog gain (floating point)
        #-dg, --digitalgain	: Set the digital gain (floating point)
        #f("-set", "log settings", "Log camera settings", [0, 1], 0)
        #-fw, --focus	: Draw a window with the focus FoM value on the image.
        return set(res)

    def getCaptureCommand(self):
        """
        Generates the command for running Raspistill on remove with currently set options.
        """
        s = " "
        res = "raspistill -o" + s + self._remote_img + s + "-v"
        for option in self._options:
            res += s + option.command + s + str(option.value)
        return res

    def setOption(self, name, value):
        """
        Sets a named option to a given value
        """
        tmp = op.Option(None, name, None, None)
        if tmp in self._options:
            option = tmp.getSetBudy()
            option.value = value
        else:
            raise Exception('Received non-existing option.')

    def getOptions(self):
        """
        returns the current options
        """
        return sorted(list(self._options))

    def setOptions(self, value):
        """
        sets the options
        """
        self._options = value

    def capture(self):
        """
        Capture image.
        Immediately transfers captured image to host machine and deletes it on remote.
        """
        if self._local_img is not None:
            os.remove(self._local_img)
            self._local_img = None

        im_name = "img_" + str(datetime.now()).replace(" ", "_").replace(":", "-") + ".jpeg"
        self._local_img = os.path.join(os.getcwd(), im_name)
        cmd = self.getCaptureCommand()
        self._runCommand(cmd)
        self._get(self._remote_img, self._local_img)


if __name__ == '__main__':
    import os
    import argparse
    parser = argparse.ArgumentParser(description='Run Raspberry Pi HQ camera through ultra simple GUI')
    parser.add_argument('ip', help='IP address of RPI')
    parser.add_argument('pswd', help='Password for RPi')
    parser.add_argument('user', help='Username for RPi')
    parser.add_argument('remote_dir', help='Workspace for this program')
    args = parser.parse_args()    
    c = RaspiStillCommClass(args.ip, args.user, args.pswd, args.remote_dir, log=True)
    try:
        c.capture()
        del c
    except:
        del c