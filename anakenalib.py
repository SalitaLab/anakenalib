import os
import sys
from typing import List

import paramiko

port = 22
host = "anakena.dcc.uchile.cl"

# CONSTANTS
papel_command = "/usr/local/bin/papel"
duplex_command = "/usr/local/bin/duplex"
pdf2ps_command = "/usr/bin/pdf2ps"


class Anakena:
    def __init__(self):
        self.client: paramiko.SSHClient = None

    def connect(self, username: str, password):
        """
        Connect to a server with a user and password ans throw error if fails
        :param username: username string
        :param password: password of username
        :return: None
        """
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy)
            client.connect(host, port=port, username=username, password=password)
            self.client = client
        except Exception as e:
            print("Fail to Connect")
            raise e

    def exec_wo_stdin(self, command: str) -> List[str]:
        """
        Execute command without more params in stdin
        :param command: command to be executed
        :return: list with response message string
        """
        stdin, stdout, stderr = self.client.exec_command(command)
        stdin.close()
        err = stderr.readlines()
        msg = stdout.readlines()
        stdout.close()
        stderr.close()
        if len(err) > 0:
            print('Fail to Exec ' + command)
            print(err)
        else:
            return msg

    def sftp(self, path: str, outpath: str = "printFolder/files/"):
        """
        Put a file from local machine into a connected server,
        (WARNING) if file exists override
        :param path: local path of file
        :param outpath: path where would it be
        :return: server path to uploaded file
        """
        if not os.path.isfile(path):
            print("File not found")
            raise NotFileException()
        sftp_conn: paramiko.SFTPClient = self.client.open_sftp()
        filename = os.path.basename(path)
        print(filename)
        mkdir_p(sftp_conn, outpath)  # create path if not exists
        sftp_conn.put(path, filename)  # write
        remote_dir = sftp_conn.getcwd()
        sftp_conn.close()
        print(remote_dir + "/" + filename)
        return remote_dir + "/" + filename  # TODO: check

    def pdf2ps(self, path: str, out_path: str = "printFolder/ps/") -> str:
        """
        Create a ps file from pdf file specified on path (server)
        :param path: server path of pdf file
        :param out_path: path where would it be new ps file
        :return: path to ps file
        """
        print(os.path.basename(path))
        if not os.path.basename(path).endswith(".pdf"):
            print("Not pdf file")
            raise NotPdfFile()

        sftp_conn: paramiko.SFTPClient = self.client.open_sftp()
        filename = os.path.basename(path)[:-4] + ".ps"
        mkdir_p(sftp_conn, out_path)  # create directories if doesn't exists
        remote_dir = sftp_conn.getcwd()
        sftp_conn.close()

        command = pdf2ps_command + ' \'' + path + '\' ' + remote_dir + "/\'" + filename + "\'"
        print(command)
        stdin, stdout, stderr = self.client.exec_command(command)
        err = stderr.readlines()
        if len(err) > 0:
            print("Error with pdf2ps")
            raise Pdf2FileException(err)
        return remote_dir + "/" + filename

    def printing(self, path: str, **kwargs):
        """
        :param path: remote path of ps file to print
        :param kwargs: {'printer': 'hp' or 'hp-335', 'landscape': -l or ""}
        :return: None
        """
        if not os.path.basename(path).endswith(".ps"):
            print("Not ps file")
            raise NotPsFile()
        if not ('printer' in kwargs and 'landscape' in kwargs):
            raise InvalidNumberArguments()
        sftp_conn = self.client.open_sftp()
        try:
            sftp_conn.stat(path)  # check if exists
        except IOError:
            raise FileNotFoundError(path)
        lpr_command = "lpr " + "-P " + kwargs['printer']
        duplex = duplex_command + " "
        if kwargs['landscape']:
            duplex += "-l "
        duplex += '\'' + path + '\''
        command = duplex + " | " + lpr_command
        print(command)
        self.client.exec_command(command)  # TODO: test printing after refactoring


def mkdir_p(sftp_conn, remote_directory):
    """
    Create a remote directory recursive
    :param sftp_conn: object of reference object to server
    :param remote_directory: remote directory that will be created
    :return: None
    """
    if remote_directory == '/':
        print('root')
        sys.exit(-1)
    if remote_directory == '':
        return
    try:
        sftp_conn.chdir(remote_directory)  # sub-directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp_conn, dirname)  # make parent directories
        sftp_conn.mkdir(basename)  # sub-directory missing, so created it
        sftp_conn.chdir(basename)
        return True


class NotPdfFile(Exception):
    pass


class Pdf2FileException(Exception):
    pass


class NotFileException(Exception):
    pass


class InvalidNumberArguments(Exception):
    pass


class NotPsFile(Exception):
    pass
