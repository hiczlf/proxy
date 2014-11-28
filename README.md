Proxy
=============


简单代理，　可以进行basic authentication验证

如开启debug模式，　可帮助查看请求头



Requirements
==================

 * Python 2.6.x, or 2.7.x


如果需要部署自动化部署, 需要安装fabric, 可能需要修改[fabfile.py](https://github.com/lifenglifeng001/proxy/blob/master/fabfile.py)

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


使用Upstart将代理作为系统服务， 参考[proxy.conf](https://github.com/lifenglifeng001/proxy/blob/master/proxy.conf)

