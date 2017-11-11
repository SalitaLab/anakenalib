import sys

import anakenalib
import getpass

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print('La cantidad de argumentos es 1 usted ingreso ' + str(len(args)))
        print('uso <filepath>')
        sys.exit(1)
    file_path = args[0]
    user = input("Username:")
    password = getpass.getpass("Password:")
    conn = anakenalib.connect(user, password)
    stdin, stdout, stderr = conn.exec_command(anakenalib.papel_command)
    name = anakenalib.sftp(file_path, conn)
    print(name)
    anakenalib.pdf2ps(name, conn)
