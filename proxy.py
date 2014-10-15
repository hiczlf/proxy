#! /usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
import argparse

__version__ = "0.1"

import BaseHTTPServer
import select, socket, SocketServer, urlparse
from socket import error as SocketError
import base64
import logging
import os

import config


def proxy_logger():
    logger = logging.getLogger(config.PROXY_NAME)
    logger_level = getattr(logging, config.LOG_LEVEL)
    logger.setLevel(logger_level)
    if config.LOG_DIR:
        log_file_path = os.path.join(config.LOG_DIR, config.LOG_FILE_NAME)
        handler = logging.FileHandler(log_file_path)
    else:
        handler = logging.StreamHandler()
    logger.addHandler(handler)
    return logger

proxy_logger = proxy_logger()


class ProxyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    __base = BaseHTTPServer.BaseHTTPRequestHandler
    __base_handle = __base.handle

    server_version = config.PROXY_NAME + config.PROXY_VERSION
    rbufsize = 0                        # self.rfile Be unbuffered

    def _connect_to(self, netloc, soc):
        i = netloc.find(':')
        if i >= 0:
            host_port = netloc[:i], int(netloc[i + 1:])
        else:
            host_port = netloc, 80
        self.log_message("connect to %s:%d" % host_port)
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
        self.log_message("connect to %s" % netloc)
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

    def log_message(self, format, *args):
        """Log an arbitrary message.

        """

        proxy_logger.info("%s - - [%s] %s" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


class AuthProxyHandler(ProxyHandler):
    ''' use basic authentication here
        The authticatin header is Proxy-Authorization， not Authorization
        The python urllib2 proxy handler also use Proxy-Authorization header.
    '''

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.auth_do(ProxyHandler.do_GET)

    def do_CONNECT(self):
        self.auth_do(ProxyHandler.do_CONNECT)

    def auth_do(self, do):
        ''' auth method '''
        proxy_auth_header = self.headers.getheader('Proxy-Authorization')
        basic_auth_key_provided = proxy_auth_header.split(' ')[-1]
        basic_auth_key = base64.b64encode(config.BASIC_AUTH_KEY)
        if not proxy_auth_header:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
        elif basic_auth_key_provided == basic_auth_key:
            do(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')


class ThreadingHTTPServer (SocketServer.ThreadingMixIn,
                           BaseHTTPServer.HTTPServer):
    pass

def parse_args():
    """get command line arguments"""
    parser = argparse.ArgumentParser(
        description=u"A simple http proxy")

    help = u"The port that listening on"
    parser.add_argument("--port", type=int,
                        help=help, default=config.DEFAULT_PORT)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    PORT = args.port
    server = ThreadingHTTPServer(('192.168.0.49', PORT), AuthProxyHandler)
    proxy_logger.info(u"HTTP代理开始工作: 监听的端口为: %s" % PORT)
    server.serve_forever()
