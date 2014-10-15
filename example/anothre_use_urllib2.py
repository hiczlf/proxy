import urllib2

proxy = {'http': 'http://lf:lf@192.168.0.49:9999',
         'https': 'http://lflf:lf@192.168.0.49:9999'}
proxy_support = urllib2.ProxyHandler(proxy)
opener = urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)
# url = "http://baidu.com"
url = "https://github.com"
req = urllib2.Request(url)
page = urllib2.urlopen(req, timeout=15)
hc = page.read()
print(hc)
