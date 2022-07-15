'''
Every 3 seconds, generate a variable sized text file that is titled with the current date and time.
Transfer this textfile from the raspberry pi to this computer.
'''

import paramiko


'''
we're going to assume that all of the ssh commands are correct after being correctly configured 
the ssh info holds the destination of where it wishes to file transfer
'''

host = "192.168.1.127"
port = 22
username = "pi"
password = "raspberry"

command = "ls"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

stdin, stdout, stderr = ssh.exec_command(command)
lines = stdout.readlines()
print(lines)

stdin, stdout, stderr = ssh.exec_command("cd data; ls")
lines = stdout.readlines()
print(lines)

for line in lines: 
  print(line)

sftp_client = ssh.open_sftp()

# assuming we have the right file path
sftp_client.get("data/data3.txt", "data/data3-copy.txt")
#sftp_client.put("data/data4.txt", "data/data4.txt")

sftp_client.close()
