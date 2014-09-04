#! /usr/bin/env python
# coding=utf-8

import argparse

__version__ = "0.2.1"

import BaseHTTPServer, select, socket, SocketServer, urlparse
from socket import error as SocketError
import base64

# ############### 代理设置  ######################
BASIC_AUTH_KEY = base64.b64encode("lf:lf")


class ProxyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    __base = BaseHTTPServer.BaseHTTPRequestHandler
    __base_handle = __base.handle

    server_version = "EasyProxy/" + __version__
    rbufsize = 0                        # self.rfile Be unbuffered

    def _connect_to(self, netloc, soc):
        i = netloc.find(':')
        if i >= 0:
            host_port = netloc[:i], int(netloc[i + 1:])
        else:
            host_port = netloc, 80
        print("\t" "connect to %s:%d" % host_port)
        try:
            soc.connect(host_port)
        except socket.error as arg:
            try:
                msg = arg[1]
            except:
                msg = arg
            self.send_error(404, msg)
            return 0
        return 1

    def do_CONNECT(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(self.path, soc):
                self.log_request(200)
                self.wfile.write(self.protocol_version +
                                 " 200 Connection established\r\n")
                self.wfile.write("Proxy-agent: %s\r\n" % self.version_string())
                self.wfile.write("\r\n")
                self._read_write(soc, 300)
        finally:
            soc.close()
            self.connection.close()

    def do_GET(self):
        (scm, netloc, path, params, query, fragment) = urlparse.urlparse(
            self.path, 'http')
        if scm != 'http' or fragment or not netloc:
            self.send_error(400, "bad url %s" % self.path)
            return
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not path:
            path = '/'
        try:
            if self._connect_to(netloc, soc):
                self.log_request()
                soc.send("%s %s %s\r\n" % (
                    self.command,
                    urlparse.urlunparse(('', '', path, params, query, '')),
                    self.request_version))
                self.headers['Connection'] = 'close'
                del self.headers['Proxy-Connection']
                for key_val in self.headers.items():
                    soc.send("%s: %s\r\n" % key_val)
                soc.send("\r\n")
                self._read_write(soc)
        finally:
            soc.close()
            self.connection.close()

    def _read_write(self, soc, max_idling=100):
        iw = [self.connection, soc]
        ow = []
        count = 0
        while 1:
            count += 1
            (ins, _, exs) = select.select(iw, ow, iw, 3)
            if exs:
                break
            if ins:
                for i in ins:
                    if i is soc:
                        out = self.connection
                    else:
                        out = soc
                    try:
                        data = i.recv(8192)
                    except SocketError:
                        pass
                    if data:
                        out.send(data)
                        count = 0
            else:
                pass
            if count == max_idling:
                break

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


class AuthProxyHandler(ProxyHandler):
    ''' 认证类: 使用basic authentication认证
        此处验证 Proxy-Authorization 头， 而不是Authorization头
        使代理验证和网站验证互补干扰。
        而且 python urllib2 代理验证也发送的是Proxy-Authorization头
    '''

    def do_AUTHHEAD(self):
        print("send header")
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.auth_do(ProxyHandler.do_GET)

    def do_CONNECT(self):
        self.auth_do(ProxyHandler.do_CONNECT)

    def auth_do(self, do):
        ''' 认证方法， 包装各种do_COMMAND方法 '''
        if not self.headers.getheader('Proxy-Authorization'):
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
        elif self.headers.getheader('Proxy-Authorization') == 'Basic ' + BASIC_AUTH_KEY:
            do(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')


class ThreadingHTTPServer (SocketServer.ThreadingMixIn,
                           BaseHTTPServer.HTTPServer):
    pass

def parse_args():
    """获取命令行参数"""
    parser = argparse.ArgumentParser(
        description=u"一个简单的http代理")

    help = u"监听的端口"
    parser.add_argument("--port", type=int, help=help, default=8000)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    PORT = args.port
    server = ThreadingHTTPServer(('', PORT), AuthProxyHandler)
    print(u"HTTP代理开始工作: 监听的端口为: %s" % PORT)
    server.serve_forever()
