#! coding=utf-8

import urllib2
import unittest
import re
import settings


all = ['suite', ]


class ParametrizeTestCase(unittest.TestCase):
    """可以接受参数的测试用例"""

    def __init__(self, methodName='runTest', param=None):
        super(ParametrizeTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_class, param):
        """
        讲param传给testcase_class类中每个测试方法，
        然后都添加到一个test suite中
        """
        test_loader = unittest.TestLoader()
        test_names = test_loader.getTestCaseNames(testcase_class)
        suite = unittest.TestSuite()
        for test_name in test_names:
            suite.addTest(testcase_class(test_name, param))
        return suite

class ProxyVisitTestCase(ParametrizeTestCase):
    def test_visit_supplier(self):
        pattern = re.compile(self.param['check_regex'], re.I)
        content = self.visit_supplier(self.param['url'], self.param['proxy'])
        result = pattern.findall(content)
        print(self.param['proxy'], self.param['name'])
        self.assertTrue(len(result) > 0)

    def visit_supplier(self, url, proxy):
        proxy_dict = self.generate_proxy_dict(proxy)
        proxy = urllib2.ProxyHandler(proxy_dict)
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        conn = urllib2.urlopen(url)
        content = conn.read()
        content = content.replace('\n', '').replace('\r', '').\
            replace('\t', '').replace('&amp;', '&').replace('&nbsp;', ' ')
        return content

    def generate_proxy_dict(self, proxy):
        # settings.AUTH_KEY = 'l:l'
        proxy_dict = {
            'http': "http://" + settings.AUTH_KEY +  "@" + proxy + ":9999",
            'https': "https://" + settings.AUTH_KEY + "@" + proxy,
        }
        return proxy_dict


suite = unittest.TestSuite()
for supplier in settings.SUPPLIER.values():
    for proxy in settings.PROXYS:
        test_param = dict(supplier, proxy=proxy)
        suite.addTest(ParametrizeTestCase.parametrize(
            ProxyVisitTestCase, test_param))
unittest.TextTestRunner(verbosity=2).run(suite)
