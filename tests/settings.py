#! coding=utf-8


SUPPLIER = {
    'Mouser': {
        'url': "http://cn.mouser.com/ProductDetail/Bourns/SRN4026-101M/?qs=sGAEpiMZZMv126LJFLh8ywD646ogI6tZbpfoPxKICYc%3d",
        'check_regex': r"<b>Mouser (?:零件编号：|Part #:)</b></td><td.*?><div.*?>(.*?)</div></td>",
        'name': "Mouser",
    },
    'Digikey': {
        'url': "http://www.digikey.cn/product-detail/zh/TMS320F243PGEA/296-10756-ND/381880",
        'check_regex': r"<tr><th.*>Digi-Key (?:零件编号|Part Number)</th><td.*><meta.*>(.*?)</td>",
        'name': "Digikey",
    },
}


PROXYS = [
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

AUTH_KEY = "lf:lf"
