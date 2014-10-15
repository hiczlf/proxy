import urllib2

proxy = urllib2.ProxyHandler({
    'http': 'http://lf:lf@192.168.0.49:9999',
    'https': 'http://lf:lf@192.168.0.49:9999',
})
auth = urllib2.HTTPBasicAuthHandler()
opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
urllib2.install_opener(opener)

conn = urllib2.urlopen('http://dc.icgoo.net')
# conn = urllib2.urlopen('https://github.com')
return_str = conn.read()
print(return_str)
