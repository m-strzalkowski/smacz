import paramiko

def start_connection():
    u_name = 'ms'
    pswd = 'Bimawen!'
    port = 22
    r_ip = '198.168.1.142'
    sec_key = '/mycert.ppk'

    myconn = paramiko.SSHClient()
    #myconn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #my_rsa_key = paramiko.RSAKey.from_private_key_file(sec_key)

    #session = myconn.connect(r_ip, username =u_name, password=pswd, port=port,pkey=my_rsa_key)
    session = myconn.connect(r_ip, username =u_name, password=pswd, port=port)

    remote_cmd = 'ifconfig'
    (stdin, stdout, stderr) = myconn.exec_command(remote_cmd)
    print("{}".format(stdout.read()))
    print("{}".format(type(myconn)))
    print("Options available to deal with the connectios are many like\n{}".format(dir(myconn)))
    myconn.close()

def nasluch_ssh():
    import base64
    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('192.168.1.142', username='ms', password='Bimawen!',look_for_keys=False)
    stdin, stdout, stderr = client.exec_command('cd ~/smacz/rejestrator; ./eksportuj -c -e')
    for line in stdout:
        print('... ' + line.strip('\n'))
    client.close()
if __name__ == '__main__':
    nasluch_ssh()#start_connection()
