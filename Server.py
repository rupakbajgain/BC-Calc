from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
import os,sys,io
from http import HTTPStatus
import urllib.parse
import shutil
import helper

def getFiles(dir=''):
    files = os.listdir(dir)
    return files

sgiven = []
class ModifiedServer(SimpleHTTPRequestHandler):
    def log_message(self,*args,**kargs):
        pass
    def ping_handler(self):
        r = ['OK']
        content_type = 'text'
        return (r, content_type)
    
    def get_handler(self):
        global sgiven
        r=[]
        files = getFiles('.\\datas\\unprocessed')
        given = None
        for i in files:
            if not i in sgiven:
                given = i
                sgiven.append(i)
                break
        if given:
            r=[given]
        else:
            if len(sgiven)==0:
                r=['done']
        content_type = 'file_name'
        return (r, content_type)

    def done_handler(self):
        query = urllib.parse.urlparse(self.path).query
        #print(urllib.parse.parse_qsl(query))
        qd = urllib.parse.parse_qs(query)
        #need fname,location,depth[3],terzaghi[3],meyerhof[3],hansen[3],vesic[3],teng[3],plasix[3]
        filename = qd['fname'][0]
        location = qd['location'][0]
        depth = qd['depth']
        terzaghi = qd['terzaghi']
        meyerhof = qd['meyerhof']
        hansen = qd['hansen']
        vesic = qd['vesic']
        teng = qd['teng']
        plasix = qd['plasix']
        r=['OK']
        content_type = 'text'
        data = []
        data.append(['Location', location])
        data.append(['depth'])
        data.append(['terzaghi'])
        data.append(['meyerhof'])
        data.append(['hansen'])
        data.append(['vesic'])
        data.append(['teng'])
        data.append(['plasix'])
        for i in range(3):
            data[1].append(depth[i])
            data[2].append(terzaghi[i])
            data[3].append(meyerhof[i])
            data[4].append(hansen[i])
            data[5].append(vesic[i])
            data[6].append(teng[i])
            data[7].append(plasix[i])
        helper.write_csv(filename+'.csv',data,'.\\datas\\result\\')
        return (r, content_type)
    
    def done_file_handler(self):
        global sgiven
        query = urllib.parse.urlparse(self.path).query
        qd = urllib.parse.parse_qs(query)
        filename = qd['fname'][0]
        r=['OK']
        print('Done:', filename)
        try:
            shutil.move('.\\datas\\unprocessed\\'+filename,'.\\datas\\processed\\')
        except:
            try:
                os.unlink('.\\datas\\unprocessed\\'+filename)
            except:
                pass
        try:
            sgiven.remove(filename)
        except:
            pass
        content_type = 'text'
        return (r, content_type)
    
    def error_handler(self):
        global sgiven
        query = urllib.parse.urlparse(self.path).query
        qd = urllib.parse.parse_qs(query)
        filename = qd['fname'][0]
        etype = qd['err_type'][0]
        print('Err:', filename,':-',etype)
        try:
            shutil.move('.\\datas\\unprocessed\\'+filename,'.\\datas\\error\\')
        except:
            try:
                os.unlink('.\\datas\\unprocessed\\'+filename)
            except:
                pass
        sgiven.remove(filename)
        r=['OK']
        content_type = 'text'
        return (r, content_type)
    
    def send_head(self):
        if not self.path.startswith('/main'):
            return super().send_head()
        path = self.path[5:]
        rv = None
        if path.startswith('/ping'):
            rv = self.ping_handler()
        elif path.startswith('/get'):
            rv = self.get_handler()
        elif path.startswith('/donefile'):
            rv = self.done_file_handler()
        elif path.startswith('/done'):
            rv = self.done_handler()
        elif path.startswith('/error'):
            rv = self.error_handler()
        if rv:
            enc = sys.getfilesystemencoding()
            encoded = '\n'.join(rv[0]).encode(enc, 'surrogateescape')
            f = io.BytesIO()
            f.write(encoded)
            f.seek(0)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "text/html; charset=%s" % enc)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            return f
        else:
            super().send_head()

def startServer():
    ServerClass=ThreadingHTTPServer
    HandlerClass=handler_class = partial(ModifiedServer,
                                directory=os.getcwd()+'\\datas')
    HandlerClass.protocol_version = 'HTTP/1.0'
    server_address = ("", 7875)
    with ServerClass(server_address, HandlerClass) as httpd:
        sa = httpd.socket.getsockname()
        serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
        print(serve_message.format(host=sa[0], port=sa[1]))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)

if __name__=='__main__':
    startServer()