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


PROXY_NAME = 'poorproxy'
PROXY_VERSION = '0.1'

proxy_logger = logging.getLogger('proxy')


def prepare_proxy_logger(logfile):
    """proxy logger

    如果指定了日志文件, 则讲日志输出到该文件中,
    否则, 输出到终端中
    """
    if logfile:
        log_file_path = logfile
        handler = logging.FileHandler(log_file_path)
    else:
        handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    proxy_logger.addHandler(handler)
    proxy_logger.setLevel(logging.DEBUG)
    return proxy_logger


class ProxyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    """
    代理请求处理器
    """
    debug = False

    debug = False
    server_version = PROXY_NAME + PROXY_VERSION

    def _connect_to(self, netloc, server_socket):
        self.log_request()
        host_port = netloc.split(':')
        if len(host_port) > 1:
            host_port = (host_port[0], int(host_port[1]))
        else:
            host_port = (host_port[0], 80)
        # self.log_message("connect to %s:%d" % host_port)
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

        netloc = netloc or self.headers['Host']
        if scm != 'http' or fragment or not netloc:
            self.send_error(400, "bad url %s" % self.path)
            return

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(netloc, server_socket):
                if self.debug:
                    proxy_logger.debug(self.headers)
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

                # 处理request body里面有东西的情况，比如post请求
                if 'Content-Length' in self.headers:
                    length = int(self.headers['Content-Length'])
                    payload = self.rfile.read(length)
                    request_message += payload

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
        print(type(self.connection))
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

    def log_message(self, format, *args):
        """log记录指定格式message"""

        proxy_logger.info("%s - - [%s] %s" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET


class AuthProxyHandler(ProxyHandler):
    auth_key = ''

    def do_CONNECT(self):
        """
        CONNECT method 处理https请求 增加用户验证
        """
        if not self.basic_auth():
            return
        ProxyHandler.do_CONNECT(self)

    def do_GET(self):
        """
        GET method 增加用户验证
        """
        if not self.basic_auth():
            return
        ProxyHandler.do_GET(self)

    def basic_auth(self):
        """使用basic authentication验证请求"""

        basic_auth_key_provided = self._get_auth_key('Proxy-Authorization')

        authenticated = False
        # 如果请求没有携带验证信息,则返回401, 提示需要提供验证信息
        if not basic_auth_key_provided:
            self.send_auth_response()
            self.wfile.write('no auth header received')
        elif basic_auth_key_provided == self.auth_key:
            authenticated = True

        # 如果验证信息错误, 同样返回401, 并提示验证失败
        # 在已携带验证信息, 并返回401的情况下, 根据FRC2616定义, 为验证失败
        else:
            self.send_auth_response()
            self.wfile.write(self.headers.getheader('Porxy-Authorization'))
            self.wfile.write('not authenticated')
        return authenticated

    def _get_auth_key(self, auth_type):
        """返回base64解码后的auth key, ':' 认为是没有用户名密码"""
        auth_header = self.headers.getheader(auth_type)
        if auth_header:
            base64_key = auth_header.split('Basic')[-1].strip()
            basic_auth_key_provided = base64.b64decode(base64_key)
            if basic_auth_key_provided == ":":
                basic_auth_key_provided = ''
        else:
            basic_auth_key_provided = ''
        return basic_auth_key_provided

    def send_auth_response(self):
        """发送basic authentication header"""
        self.send_response(401)
        # self.send_header('Proxy-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Proxy-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()


class ThreadingHTTPServer (SocketServer.ThreadingMixIn,
                           BaseHTTPServer.HTTPServer):
    pass


def parse_args():
    """获取命令行参数"""
    parser = OptionParser(usage="%prog [options] args")
    help = u"监听的端口"
    parser.add_option("--port", dest='port', type='int',
                    help=help, default=9999)
    parser.add_option("--debug", action='store_true', default=False,
                    help="开启调试模式")

    # basic auth 相关
    parser.add_option("--auth_key", dest='auth_key', default="lf:lf",
                    help="basic auth key [用户名]:[密码] ")
    parser.add_option("--auth", action='store_true', default=False,
                    help="是否需要验证")

    parser.add_option("--logfile", default=False,
                    help="日志文件路径")

    opts, args = parser.parse_args()
    return opts

def get_handler(auth, debug, auth_key):
    """ 根据命令行参数,返回合适的handler"""
    handler = AuthProxyHandler if auth else ProxyHandler

    handler.debug = debug
    handler.auth_key = auth_key

    return handler


if __name__ == '__main__':
    args = parse_args()
    port = args.port
    prepare_proxy_logger(args.logfile)
    handler = get_handler(args.auth, args.debug, args.auth_key)
    server = ThreadingHTTPServer(('', port), handler)
    proxy_logger.info("代理开始运行, 监听的端口号是: %s" % port)
    server.serve_forever()
