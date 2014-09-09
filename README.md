PoorProxy
=============

This proxy is based on [Tiny HTTP Proxy](https://github.com/tkmunzwa/Tiny-HTTP-Proxy), 
and has some  improvement.



Overview
===============

After use Tinyproxy some time. I find I need some authentication that use usename
and passwork, not only allow specified ips. So I write this simple proxy.

And also include some useful script:

 * An automatic deploy script 
 * some example that using proxy

Requirements
==================

 * Python 2.6.x, or 2.7.x

if you want to use the deploy script, need to install facbric.

 * pip install fabric





Usage
==============

    $python proxy.py   --port [PROXY_PORT] 


Show help message:

    $ python proxy.py -h

deploy it:
    
    $ fab deploy -u YOUR_SSH_PASSWORD -p YOUR_SSH_USERNAME
