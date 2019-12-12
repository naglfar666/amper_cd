import paramiko
import os
import sys


class ReleaseTransfer():
    def __init__(self, hostname, username, password):
        self.hostname = hostname 
        self.username = username
        self.password = password

    # Очищаем на сервере директорию
    def start(self, path):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.hostname, username=self.username, password=self.password, port=22)
        stdin, stdout, stderr = self.client.exec_command('cd ' + path + ' && rm -rf *')

        transport = paramiko.Transport((self.hostname, 22))
        transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(transport)
    
    # Сканируем директорию рекурсивно
    def scan_dir(self, local_path, remote_path):
        print('>> SCANNING ' + local_path + ' TO ' + remote_path + '\n')
        release_files = os.listdir(local_path)
        for single_file in release_files:
            print('>> FILE SCANNED ' + single_file + '\n')
            if (os.path.isdir(local_path + '/' + single_file) == True):
                print('>> FILE IS DIR ' + single_file + '\n')
                self.client.exec_command('mkdir ' + remote_path + '/' + single_file)
                self.scan_dir(local_path + '/' + single_file + '/', remote_path + '/' + single_file + '/')
            else:
                print('>> FILE IS NOT DIR ' + local_path + '/' + single_file + '\n')
                if '/' in remote_path[-1]:
                    if '/' in local_path[-1]:
                        self.send(local_path + single_file, remote_path + single_file)
                    else:
                        self.send(local_path + '/' + single_file, remote_path + single_file)
                else:
                    if '/' in local_path[-1]:
                        self.send(local_path + single_file, remote_path + '/' + single_file)
                    else:
                        self.send(local_path + '/' + single_file, remote_path + '/' + single_file)
                    
                
        

    # Отправляем файл на сервер
    def send(self, local_path, remote_path):
        print('>> SENDING ' + local_path + ' TO ' + remote_path)
        self.sftp.put(local_path, remote_path)

    def close(self):
        self.sftp.close()
        self.client.close()

test = ReleaseTransfer(sys.argv[2], sys.argv[1], sys.argv[3])
test.start(sys.argv[5])
test.scan_dir(sys.argv[4], sys.argv[5])