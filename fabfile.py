#!/usr/bin/env python

from __future__ import unicode_literals
import re
from fabric.contrib.files import exists
from fabric.api import env, local, run, warn_only, parallel

REPO_URL = 'https://github.com/lifenglifeng001/proxy.git'

env.hosts = [
    'host',
]

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
        run("kill `ps -ef | grep  proxy.py | grep -v grep | awk '{print $2}'`")
        run("service proxy restart")

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
    cmd = "dtach -n `mktemp -u /tmp/proxy.XXXX` python /home/%s/proxy/proxy.py --auth --port 9999" % env.user
    run(cmd)
