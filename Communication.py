
import paramiko
import Options as op

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
    def __init__(self, ip, user, pswd, log=False):
        super(RaspiStillCommClass, self).__init(ip, user, pswd, log)
        self._options = self._generateDefaultOptions()

    def _generateDefaultOptions(self):
        """
        Generates the default options for running Raspistill on remote
        """

    def _getRunCommand(self):
        """
        Generates the command for running Raspistill on remove with currently set options.
        """
        res = ""

        return res

    def getOptions(self):
        """
        returns the current options
        """
        return self._options

    def setOptions(self, value):
        """
        sets the options
        """
        self._options = value


if __name__ == '__main__':
    import os
    import argparse
    parser = argparse.ArgumentParser(description='Run Raspberry Pi HQ camera through ultra simple GUI')
    parser.add_argument('ip', help='IP address of RPI')
    parser.add_argument('pswd', help='Password for RPi')
    parser.add_argument('user', help='Username for RPi')
    args = parser.parse_args()    
    c = BaseCommClass(args.ip, args.user, args.pswd, log=True)
    c._get('/home/pi/experiments/image.jpeg', os.path.join(os.getcwd(), 'image.jpeg'))
