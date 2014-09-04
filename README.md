my proxy
=============

基于Tiny HTTP Proxy编写,

仅仅增加认证功能, 修复一些问题， 不在此一一列举了。

原版本库地址: https://github.com/tkmunzwa/Tiny-HTTP-Proxy

设置用户名密码， 请修改 BASIC_AUTH_KEY(在proxy.py中)

注意
-----------

暂时只支持： python2.7


使用方法
---------------

    $python proxy.py   --port 端口

或, 查看帮助:

    $ python proxy.py -h
