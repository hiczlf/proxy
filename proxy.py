#!/usr/bin/env python
# coding=utf-8

import argparse
from twisted.internet import reactor
from twisted.web import proxy, http

IP_LIST = ['113.108.68.162', '113.89.9.136']


def parse_args():
    parser = argparse.ArgumentParser(
        description=u"This is a proxy implemented by twisted")

    help = "The port tot listen on. "
    parser.add_argument("--port", type=int, help=help, default=9999)

    args = parser.parse_args()
    return args


args = parse_args()
IP = args.ip
PORT = args.port


class RestrictIPProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        print(addr.host)
        if addr.host in IP_LIST:
            return proxy.Proxy()
        return None


reactor.listenTCP(PORT, RestrictIPProxyFactory())
reactor.run()
