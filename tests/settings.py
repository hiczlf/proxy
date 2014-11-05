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
    'Roch': {
        'url': "https://www.rocelec.com/parts/details/?part=54596ff1e4b0c7fe4500beb8&build=0",
        'check_regex': r"<strong>Part Number</strong>.*?<span.*?>(.*?)</span>",
        'name': "Roch",
    },
}


PROXYS = ['106.186.23.144:9999',
          '198.58.111.202:9999',
          '66.228.35.131:9999',
          '106.186.112.187:9999',
          '192.81.131.122:9999',
          '173.255.195.118:9999',
          '64.20.37.156:9999',
          '173.214.169.12:9999',
          '42.96.193.216:9999']
PROXYS = ['42.96.193.216:9999', ]

AUTH_KEY = "lf:lf"
