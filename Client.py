import requests
import time
import socket
from test import get_result_from_file_data

def get_ip():
    s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255',1))
        IP=s.getsockname()[0]
    except Exception:
        IP='127.0.0.1'
    finally:
        s.close()
    return IP
    
server_ip = None
def failProofSend(path, params={}):
    while(True):
        try:
            r = requests.get(path,params)
            content = r.content
            return content
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print('Reconnecting')
            pass

def getAndProcessFile(name):
    print(name)
    #download that file
    content = failProofSend('http://{}:7875/unprocessed/{}'.format(server_ip,name))
    res = get_result_from_file_data(content, name)
    if type(res)==str:
        #it failed
        try:
            r = requests.get('http://{}:7875/main/error'.format(server_ip),params={'fname':name,'err_type': res})
        except:
            pass
        return
    #else we know the result
    #let's send it
    for i in res:
        location=i[1]
        tdata=i[2]
        depth = [1.5,3,4.5]
        terzaghi=[]
        meyerhof=[]
        hansen=[]
        vesic=[]
        teng=[]
        plasix=[]
        for j in range(3):
            terzaghi.append(tdata[j][0])
            meyerhof.append(tdata[j][1])
            hansen.append(tdata[j][2])
            vesic.append(tdata[j][3])
            teng.append(tdata[j][4])
            plasix.append(tdata[j][5])
            
        dpos = name.rfind('.')
        fnm = name[:dpos]
        query = {
            'fname': fnm+'['+i[0]+']',
            'location': location,
            'depth': depth,
            'terzaghi': terzaghi,
            'meyerhof': meyerhof,
            'hansen': hansen,
            'vesic': vesic,
            'teng': teng,
            'plasix': plasix
        }
        try:
            r = requests.get('http://{}:7875/main/done'.format(server_ip),params=query)
        except:
            return
    try:
        r = requests.get('http://{}:7875/main/donefile'.format(server_ip),params={'fname':name})
    except:
        return

def mainLoop():
    while(True):
        try:
            file=failProofSend('http://{}:7875/main/get'.format(server_ip)).decode()
            if file=='done':
                print('done')
                time.sleep(2)
            elif file:
                getAndProcessFile(file)
            else:
                print('wait')
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nKeyboard interrupt received, exiting.')
            break

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
    lip = get_ip()
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
    global server_ip
    print('Starting server(6s max.)')
    sip = ServerIP()
    if sip:
        print('ServerIP: ',sip)
        server_ip=sip
    else:
        return
    mainLoop()

if __name__=='__main__':
    startClient()