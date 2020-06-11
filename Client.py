import helper.ip
import requests

def CheckPing(ip):
    try:
        r = requests.get('http://{}:7875/main/ping'.format(ip),timeout=0.1)
        if r.content==b'OK':
            return True
    except:
        pass
    return False


def ServerIP():
    loip = '127.0.0.1'
    r=CheckPing(loip)
    if r:
        return loip 
    lip = helper.ip.get_ip()
    dpos = lip.rfind('.')
    lip=lip[:dpos+1]
    for i in range(1,255):
        nip = lip+str(i)
        if i%10==0:
            print('.',end='',flush=True)
        r= CheckPing(nip)
        if r:
            print()
            return nip
    print()
    return None

def startClient():
    print('Starting server(26s max.)')
    print('ServerIP: ',ServerIP())

if __name__=='__main__':
    startClient()