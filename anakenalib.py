from typing import List

import paramiko
import sys

port = 22
host = "anakena.dcc.uchile.cl"

# CONSTANTS
papel_command = "/usr/local/bin/papel"
duplex_command = "/usr/local/bin/duplex"


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


def exec_command(command: str, conn: paramiko.SSHClient) -> List[str]:
    # TODO: check command
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
