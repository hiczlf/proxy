#!/usr/bin/env python

from __future__ import unicode_literals
import re
from fabric.contrib.files import exists
from fabric.api import env, local, run, warn_only, parallel

REPO_URL = 'https://github.com/lifenglifeng001/proxy.git'

env.hosts = [
    '106.186.23.144',
    '198.58.111.202',
    '66.228.35.131',
    '106.186.112.187',
    '192.81.131.122',
    '173.255.195.118',
    '64.20.37.156',
    '173.214.169.12',
    '96.126.101.242',
    '96.126.104.22',
    '23.239.25.67',
    '96.126.102.240',
    '106.187.46.127',
    '198.58.117.241',
    '23.92.30.100',
    '96.126.104.167',
    '23.239.4.145',
    '50.116.47.220',
    '173.255.218.105',
    '106.186.27.87',
]
# env.hosts = [
#     '42.96.193.216'
# ]

@parallel
def deploy():
    proxy_folder = '/home/%s/proxy' % env.user
    _install_requirements()
    _create_directory_structure_if_necessary(proxy_folder)
    _get_latest_source(proxy_folder)
    _run_proxy()

@parallel
def kill():
    with warn_only():
        run("kill `ps -ef | grep original_TinyHTTPProxy.py | grep -v grep | awk '{print $2}'`")
        run("kill `ps -ef | grep  arrow_rs.py | grep -v grep | awk '{print $2}'`")
        run("kill `ps -ef | grep  findchips.py | grep -v grep | awk '{print $2}'`")
        run("kill `ps -ef | grep  hcr.py | grep -v grep | awk '{print $2}'`")

def _install_requirements():
    distro = run('cat /etc/issue')
    if re.search("Ubuntu", distro):
        with warn_only():
            run('sudo apt-get -y  --no-upgrade install git')
            run('sudo apt-get -y --no-upgrade install dtach')
    elif re.search("CentOS", distro):
        run('rpm -qa | grep -qw git || sudo yum install -y -q git')
        run('rpm -qa | grep -qw dtach || sudo yum install -y -q dtach')
    with warn_only():
        run("kill `ps -ef | grep proxy.py | grep -v grep | awk '{print $2}'`")

def _create_directory_structure_if_necessary(proxy_folder):
    run('mkdir -p %s' % (proxy_folder,))


def _get_latest_source(proxy_folder):
    if exists(proxy_folder + '/.git'):
        run('cd %s && git fetch' % (proxy_folder))
    else:
        run('git clone %s %s' % (REPO_URL, proxy_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (proxy_folder, current_commit))


def _run_proxy():
    cmd = "dtach -n `mktemp -u /tmp/proxy.XXXX` python /home/%s/proxy/proxy/proxy.py --port 9999" % env.user
    run(cmd)
