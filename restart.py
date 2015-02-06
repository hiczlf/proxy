#! /usr/bin/env python
import urllib2
import subprocess
from time import sleep

pip = 'http://lf:lf@0.0.0.0:9999'

def is_good_proxy():
    try:
        proxy_handler = urllib2.ProxyHandler({'http': pip})
        opener = urllib2.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        req = urllib2.Request('http://www.baidu.com')  # change the URL to test here
        urllib2.urlopen(req)
    except:
        return False
    return True

def restart_program():
    args = ['python', '/home/root/proxy/proxy.py', '--auth', '--port=9999']
    subprocess.Popen(args, stdin=None, stdout=None, stderr=None)

def main():
    while True:
        if is_good_proxy():
            sleep(5)
        else:
            restart_program()
            sleep(5)

if __name__ == '__main__':
    main()
