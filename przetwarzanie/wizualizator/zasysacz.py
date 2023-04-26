from subprocess import Popen, PIPE
import base64
import paramiko
import re
import os
def znajdź_ip(polecenie):
    print(polecenie.split(" "))
    proc = Popen(polecenie.split(" "), stdout=PIPE, stderr=PIPE)
    #stdout, stderr = process.communicate()
    #print(stdout.read())
    while line:=proc.stdout.readline():
        line = line.strip().decode("utf-8")#print(line.strip().decode("utf-8"))
        print('+++',line)
        if re.match("^(\d{1,3}\.){3}\d{1,3}$",line):
            return line
    return None
#Zawsze zwraca jakieś ip, nie wiadomo, czy dobre
def znajdź_ip_():
    if os.name == 'posix':
        print('system zgodny z POSIX, używam sh')
        polecenie = './szukaj.sh'
    if os.name == 'nt':
        print('Windows, używam .bat')
        polecenie = 'win_szukaj.bat'
    piip = znajdź_ip(polecenie)
    if not piip:
        print('Nie znaleziono ip urządzenia! Wpisz go proszę.')
        piip = input()
    return piip

def nasluch_ssh(blokujacy=False,excmd=True,flush=True):
    piip = znajdź_ip_()
    print(f'piip:{piip}')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(piip, username='ms', password='Bimawen!',look_for_keys=False)
    if not excmd:
        channel = client.invoke_shell()
        stdin = channel.makefile('wb',1)
        stdout = channel.makefile('r')
        #"ps axo 'pid comm' | grep nagrywaj | awk '{print $1}'"
        stdin.write('echo "RSTART";cd ~/smacz/rejestrator; ./eksportuj -c -e 2>/dev/null' + ' -l' if flush else '' +'\n')
        stdin.flush()
        
        while not re.match("[^\"]*RSTART[^\"]*", line:=next(stdout)):
            print('-+-',line)
        #if not blokujacy:
        #    stdin.channel.setblocking(0)
        #yield line
    if excmd:
        stdin, stdout, stderr = client.exec_command('cd ~/smacz/rejestrator; ./eksportuj -c -e' + ' -l' if flush else '')
    if blokujacy:
        for line in stdout:
            yield line.strip('\n') if line else None#print('... ' + line.strip('\n'))
    else:
        while not stdout.channel.closed:
            if stdout.channel.recv_ready():
                yield next(stdout)
            else:
                yield None
    client.close()
    
if __name__ == '__main__':
    gen = nasluch_ssh()#start_connection()
    for li in gen:
        print('...',li)
