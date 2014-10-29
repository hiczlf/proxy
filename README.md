PoorProxy
=============

基于[Tiny HTTP Proxy](https://github.com/tkmunzwa/Tiny-HTTP-Proxy), 编写, 
修复了些小问题, 增加用户身份验证.



Requirements
==================

 * Python 2.6.x, or 2.7.x

如果需要部署自动化部署, 需要安装fabric

 * pip install fabric





Usage
==============

    $python proxy.py   --port [PROXY_PORT] 


帮助:

    $ python proxy.py -h

部署:
    
    $ fab deploy -u YOUR_SSH_PASSWORD -p YOUR_SSH_USERNAME
