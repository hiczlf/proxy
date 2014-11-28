#! /usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals

__version__ = "0.1"

from optparse import OptionParser
import BaseHTTPServer
import select, socket, SocketServer, urlparse
from socket import error as SocketError
import base64
import logging
import os

import config


def proxy_logger():
    """proxy logger

    如果指定了日志文件, 则讲日志输出到该文件中,
    否则, 输出到终端中
    """
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
    """
    代理请求处理器
    """

    debug = False
    server_version = config.PROXY_NAME + config.PROXY_VERSION

    def _connect_to(self, netloc, server_socket):
        self.log_request()
        host_port = netloc.split(':')
        if len(host_port) > 1:
            host_port = (host_port[0], int(host_port[1]))
        else:
            host_port = (host_port[0], 80)
        self.log_message("connect to %s:%d" % host_port)
        try:
            server_socket.connect(host_port)
        except socket.error as e:
            self.send_error(404, str(e))
            return False
        return True

    def do_CONNECT(self):
        """
        CONNECT method 处理https请求
        参考 https://www.ietf.org/rfc/rfc2817.txt
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(self.path, server_socket):
                self.wfile.write(self.protocol_version +
                                 " 200 Connection established\r\n")
                self.wfile.write("Proxy-agent: %s\r\n" % self.version_string())
                self.wfile.write("\r\n")
                self._read_write(server_socket, 300)
        finally:
            server_socket.close()
            self.connection.close()

    def do_GET(self):
        """处理GET请求"""
        (scm, netloc, path, params, query, fragment) = urlparse.urlparse(
            self.path, 'http')
        if scm != 'http' or fragment or not netloc:
            self.send_error(400, "bad url %s" % self.path)
            return

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(netloc, server_socket):
                if self.debug:
                    print(self.headers)
                request_message = "%s %s %s\r\n" % (
                    self.command,
                    urlparse.urlunparse(
                        ('', '', path or '/', params, query, '')),
                    self.request_version)
                self.headers['Connection'] = 'close'
                del self.headers['Proxy-Connection']
                for key_val in self.headers.items():
                    request_message += "%s: %s\r\n" % key_val
                request_message += "\r\n"
                server_socket.sendall(request_message)
                self._read_write(server_socket)
        finally:
            server_socket.close()
            self.connection.close()

    def _read_write(self, server_socket, max_select=300):
        """
        使用IO/复用将客户端发送的内容转发给所请求的服务器,
        讲服务器端发送的请求转发给客户端

        """
        client_socket = self.connection
        except_list = read_list = [client_socket, server_socket]
        # select 次数, 每select一次,加1
        select_count = 0
        while 1:
            select_count += 1
            try:
                (read_ready_sockets, _, except_ready_sockets) = \
                    select.select(read_list, [], except_list, 3)
            except socket.error:
                break

            if except_ready_sockets:
                break

            for read_ready_socket in read_ready_sockets:
                if read_ready_socket is server_socket:
                    write_socket = client_socket
                else:
                    write_socket = server_socket

                # 从读socket读取内容, 然后发送给写socket
                try:
                    data = read_ready_socket.recv(8192)
                except SocketError:
                    data = None
                finally:
                    # 如果出现异常,或读取内容为空(socket 对方已关闭), 则退出
                    if not data:
                        break
                if data:
                    write_socket.send(data)
                    select_count = 0
            # 超过了最大的select次数
            if select_count == max_select:
                break

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


class AuthProxyHandler(ProxyHandler):

    def do_CONNECT(self):
        """
        CONNECT method 处理https请求 增加用户验证
        """
        if not self.basic_auth():
            return
        super(AuthProxyHandler, self).do_CONNECT()

    def do_GET(self):
        """
        GET method 增加用户验证
        """
        if not self.basic_auth():
            return
        super(AuthProxyHandler, self).do_CONNECT()

    def basic_auth(self):
        """使用basic authentication验证请求"""
        proxy_auth_header = self.headers.getheader('Proxy-Authorization')
        if proxy_auth_header:
            basic_auth_key_provided = proxy_auth_header.split(' ')[-1]
        basic_auth_key = base64.b64encode(config.BASIC_AUTH_KEY)

        authenticated = False
        # 如果请求没有携带验证信息,则返回401, 提示需要提供验证信息
        if not proxy_auth_header:
            self.send_auth_response()
            self.wfile.write('no auth header received')
        elif basic_auth_key_provided == basic_auth_key:
            authenticated = True
        # 如果验证信息错误, 同样返回401, 并提示验证失败
        # 在已携带验证信息, 并返回401的情况下, 根据FRC2616定义, 为验证失败
        else:
            self.send_auth_response()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')
        return authenticated

    def send_auth_response(self):
        """发送basic authentication header"""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def log_message(self, format, *args):
        """log记录指定格式message"""

        proxy_logger.info("%s - - [%s] %s" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))


class ThreadingHTTPServer (SocketServer.ThreadingMixIn,
                           BaseHTTPServer.HTTPServer):
    pass


def parse_args():
    """获取命令行参数"""
    parser = OptionParser(usage="python proxy.py")
    help = u"监听的端口"
    parser.add_option("--port", dest='port', type='int',
                    help=help, default=config.DEFAULT_PORT)
    parser.add_option("--auth", action='store_true', default=False,
                    help="是否需要验证")

    parser.add_option("--debug", action='store_true', default=False,
                    help="是否需要验证")

    opts, args = parser.parse_args()
    return opts

def get_handler(auth, debug):
    handler = AuthProxyHandler if auth else ProxyHandler
    if debug:
        handler.debug = True
    return handler


if __name__ == '__main__':
    args = parse_args()
    PORT = args.port
    handler = get_handler(args.auth, args.debug)
    server = ThreadingHTTPServer(('', PORT), handler)
    proxy_logger.info("代理开始运行, 监听的端口号是: %s" % PORT)
    server.serve_forever()
