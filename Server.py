from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
import os,sys,io
from http import HTTPStatus

class ModifiedServer(SimpleHTTPRequestHandler):
    def ping_handler(path):
        r = ['OK']
        content_type = 'text'
        return (r, content_type)
    
    def send_head(self):
        if not self.path.startswith('/main'):
            return super().send_head()
        path = self.path[5:]
        rv = None
        if path.startswith('/ping'):
            #r=[]
            #r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                # '"http://www.w3.org/TR/html4/strict.dtd">')
            #r.append('<html>OK</html>')
            rv = self.ping_handler()
        
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