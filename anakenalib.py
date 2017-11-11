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
        print(type(client))
        return client
    except Exception as e:
        print("Fail to Connect")
        print(e)
        sys.exit(1)


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


def sftp(path: str, conn: paramiko.SSHClient, outpath: str = "/printFolder/files"):
    # TODO: check path
    sftp_conn: paramiko.SFTPClient = conn.open_sftp()
    try:
        sftp_conn.chdir(outpath)  # Test if remote_path exists
    except IOError:
        sftp_conn.mkdir(outpath)  # Create remote_path
        sftp_conn.chdir(outpath)
    sftp_conn.put(path, '.')  # At this point, you are in remote_path in either case
    remote_dir = sftp_conn.getcwd()
    sftp_conn.close()
    return remote_dir + os.path.basename(path)


def pdf2ps(path: str, conn: paramiko.SSHClient, out_path: str = "/printFolder/ps/") -> str:
    command = papel_command + " " + path + " " + out_path + os.path.basename(path)[:-4]  # without .pdf
    conn.exec_command(command)
    return out_path + os.path.basename(path)


def printing(path: str, conn: paramiko.SSHClient, **kwargs):
    # TODO: check if exists printer and if is valid
    command = duplex_command + " " + path + " | lpr -P " + kwargs['printer']
    conn.exec_command(command)

# TODO: test sftp, pdf2ps and printing
