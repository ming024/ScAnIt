import paramiko
ssh_client = paramiko.SSHClient()
ssh_client.connect(hostname='140.112.175.176',username='seasa2016',password='Mpac1234')
ftp_client=ssh_client.open_sftp()
ftp_client.put('test.jpg', '~/makeNTU/')
ftp_client.close()
