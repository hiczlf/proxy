PoorProxy
=============

基于[Tiny HTTP Proxy](https://github.com/tkmunzwa/Tiny-HTTP-Proxy), 编写, 
修复了些小问题, 增加用户身份验证.

增加了个自动化部署脚本, 和简单的测试脚本



Requirements
==================

 * Python 2.6.x, or 2.7.x

如果需要部署自动化部署, 需要安装fabric

 * pip install fabric





Usage
==============

默认在项目根目录:

    $python proxy.py   --port [PROXY_PORT] 


帮助:

    $ python proxy.py -h

部署:
    
    $ fab deploy -u YOUR_SSH_PASSWORD -p YOUR_SSH_USERNAME

测试(需要根据具体情况更改测试用例):

    $ python tests/test_visit_supplier_by_proxy.py

