"""
Various POST payloads used for scraping realforeclose.miamidade.gov
"""
import os

import dotenv

dotenv.load_dotenv()

splash_notice = {
    'zaction': 'AJAX',
    'ZMETHOD': 'COM',
    'process': 'NOTICE',
    'func': 'ACCEPT',
    'showjson': 'false',
    'NID': 8045
}

login = {
    'ZACTION': 'AJAX',
    'ZMETHOD': 'LOGIN',
    'func': 'LOGIN',
    'USERNAME': os.getenv('foreclosure_username'),
    'USERPASS': os.getenv('foreclosure_password')
}


headers = {
    'Referer': "https://www.miamidade.realforeclose.com",
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64)'
                   ' AppleWebKit/537.36 (KHTML, like Gecko)'
                    ' Chrome/114.0.0.0 Safari/537.36')
}

cookie = {
    'cfid': 'ec7e22be-0981-4f1e-8447-33c513aa82b6',
    'cftoken':'0',
    '_ga': 'GA1.2.809838089.1572371936',
    '__utmz': ('156495143.1579813001.69.2.utmcsr=google|'
                'utmccn=(organic)|'
                'utmcmd=organic|'
                'utmctr=(not%20provided)'),
    '_gcl_au':'1.1.184605138.1580149038',
    '_gid':'GA1.2.725269267.1581437759',
    'AWSALB' : ('FSVXen2sZRjuTXKQL8u7Y28bLH0TteGiRyl7N0P5VORdZW/'
                'cfROJOpwXRlKlaqQcMQWdrsFXE5XfNbyc+Yg2A4i+aZSU6+'
                'oPuFOFHHUYFtbZ13Qecoh8FLaTXTi5'),
    'AWSALBCORS': ('I4+QwgjHmDBotcRCAjuffeVoY1kl/'
                   '03zLxTY3tgLjGiXpIGHydU2yeKgO8m/'
                   'ShtADDGUhnP2GYnZ5W3opKT07hYJ71Dygn1ikGySBo5yrhrEQ63ro1znj/d/WLmb'),
    '__utmc':'156495143',
    'CF_CLIENT_MIAMIDADE_REALFORECLOSE_TC':'1610817783764',
    '__utma':'156495143.809838089.1572371936.1581627165.1581703305.95',
    '__utmt_UA-51657054-1':'1',
    'testcookiesenabled':'enabled',
    '__utmb':'156495143.18.10.1581703305',
    'CF_CLIENT_MIAMIDADE_REALFORECLOSE_LV':'1610823164810',
    'CF_CLIENT_MIAMIDADE_REALFORECLOSE_HC':'580'
}
