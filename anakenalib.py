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
    # TODO: check path
    sftp_conn: paramiko.SFTPClient = conn.open_sftp()
    filename = os.path.basename(path)
    mkdir_p(sftp_conn, outpath)  # create path if not exists
    sftp_conn.put(path, filename)  # write
    remote_dir = sftp_conn.getcwd()
    sftp_conn.close()
    return os.path.join(remote_dir, filename)


def pdf2ps(path: str, conn: paramiko.SSHClient, out_path: str = "printFolder/ps/") -> str:
    if not os.path.basename(path).endswith(".pdf"):
        print("Not pdf file")
        raise NotPdfFile()
    command = pdf2ps_command + " " + path + " " + out_path + os.path.basename(path)[:-4] + ".ps"  # without .pdf
    sftp_conn: paramiko.SFTPClient = conn.open_sftp()
    mkdir_p(sftp_conn, out_path)  # create directories if doesn't exists
    sftp_conn.close()
    stdin, stdout, stderr = conn.exec_command(command)
    err = stderr.readlines()
    if len(err) > 0:
        print("Error with pdf2ps")
        raise Pdf2FileException()
    return out_path + os.path.basename(path)


def printing(path: str, conn: paramiko.SSHClient, **kwargs):
    # TODO: check if exists printer and if is valid
    command = duplex_command + " " + path + " | lpr -P " + kwargs['printer']
    conn.exec_command(command)


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
