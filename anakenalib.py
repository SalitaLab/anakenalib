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


def connect(username: str, password) -> paramiko.SSHClient:
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy)
        client.connect(host, port=port, username=username, password=password)
        return client
    except Exception as e:
        print("Fail to Connect")
        raise e


def exec_wo_stdin(command: str, conn: paramiko.SSHClient) -> List[str]:
    stdin, stdout, stderr = conn.exec_command(command)
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


def sftp(path: str, conn: paramiko.SSHClient, outpath: str = "printFolder/files/"):
    # WARNING : if file exists override
    if not os.path.isfile(path):
        raise NotFileException()
    sftp_conn: paramiko.SFTPClient = conn.open_sftp()
    filename = os.path.basename(path)
    mkdir_p(sftp_conn, outpath)  # create path if not exists
    sftp_conn.put(path, filename)  # write
    remote_dir = sftp_conn.getcwd()
    sftp_conn.close()
    print(os.path.join(remote_dir, filename))
    return os.path.join(remote_dir, filename)


def pdf2ps(path: str, conn: paramiko.SSHClient, out_path: str = "printFolder/ps/") -> str:
    if not os.path.basename(path).endswith(".pdf"):
        print("Not pdf file")
        raise NotPdfFile()

    sftp_conn: paramiko.SFTPClient = conn.open_sftp()
    filename = os.path.basename(path)[:-4] + ".ps"
    mkdir_p(sftp_conn, out_path)  # create directories if doesn't exists
    remote_dir = sftp_conn.getcwd()
    sftp_conn.close()

    command = pdf2ps_command + " " + path + " " + os.path.join(remote_dir, filename)
    print(command)
    stdin, stdout, stderr = conn.exec_command(command)
    err = stderr.readlines()
    if len(err) > 0:
        print("Error with pdf2ps")
        raise Pdf2FileException(err)
    return os.path.join(remote_dir, filename)


def printing(path: str, conn: paramiko.SSHClient, **kwargs):
    """
    :param path: remote path of ps file to print
    :param conn: SSH connection
    :param kwargs: {'printer': 'hp' or 'hp-335', 'landscape': -l or ""}
    :return: None
    """
    if not os.path.basename(path).endswith(".ps"):
        print("Not ps file")
        raise NotPsFile()
    if not ('printer' in kwargs and 'landscape' in kwargs):
        raise InvalidNumberArguments()
    sftp_conn = conn.open_sftp()
    try:
        sftp_conn.stat(path)  # check if exists
    except IOError:
        raise FileNotFoundError(path)
    lpr_command = "lpr " + "-P " + kwargs['printer']
    duplex = duplex_command + " " + kwargs['landscape']
    if kwargs['landscape'] == "-l":
        duplex += " "
    duplex += path
    command = duplex + " | " + lpr_command
    print(command)
    # conn.exec_command(command) TODO: test on production


def mkdir_p(sftp_conn, remote_directory):
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


# TODO: test printing
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
