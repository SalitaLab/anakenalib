import paramiko

import anakenalib
import getpass
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="path del archivo a imprimir")
    parser.add_argument("-P",
                        action="store", dest="printer", default="hp", choices=['hp', 'hp-335'],
                        help="hp [toqui][default] , hp-335 [salita]")
    parser.add_argument("-l", "--landscape",
                        action="store_true", dest="landscape", default=False,
                        help="borde corto")

    args = parser.parse_args()

    user = input("Username:")
    password = getpass.getpass("Password:")
    conn = None
    try:
        conn = anakenalib.connect(user, password)
        stdin, stdout, stderr = conn.exec_command(anakenalib.papel_command)
        print(stdout.readlines())
        remote_path = anakenalib.sftp(args.file, conn)
        ps_file = anakenalib.pdf2ps(remote_path, conn)
        anakenalib.printing(ps_file, conn, printer=args.printer, landscape=args.landscape)
    except Exception as e:
        print(e)
        if conn is paramiko.SSHClient:
            conn.close()
