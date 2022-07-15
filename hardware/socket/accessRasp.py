import paramiko

#host = "192.168.1.127"
host = "172.20.10.18"
port = 22
username = "pi"
password = "raspberry"

command = "ls"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

'''
stdin, stdout, stderr = ssh.exec_command(command)
lines = stdout.readlines()
print(lines)
'''

stdin, stdout, stderr = ssh.exec_command("cd data; ls")
files = stdout.readlines()
print(files)

# transferring all files inside of "data" folder
if files != []:
  sftp_client = ssh.open_sftp()
  for file in files: 
    print(file[:-1])
    sftp_client.get("data/" + file[:-1], "data/" + file[:-1])




#sftp_client = ssh.open_sftp()
#sftp_client.get("data/data3.txt", "data/data3-copy.txt")
#sftp_client.put("data/data4.txt", "data/data4.txt")

#sftp_client.close()
