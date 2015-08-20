#! coding=utf-8


SUPPLIER = {
    'Digikey': {
        'url': "http://www.digikey.cn/product-detail/zh/TMS320F243PGEA/296-10756-ND/381880",
        'check_regex': r"<tr><th.*>Digi-Key (?:零件编号|Part Number)</th><td.*><meta.*>(.*?)</td>",
        'name': "Digikey",
    },
}


PROXYS = ['host']

AUTH_KEY = "username:pasword"
