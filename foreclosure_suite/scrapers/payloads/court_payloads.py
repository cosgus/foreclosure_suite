"""
Various POST payloads used in scraping miami dade court systems
"""
import os

import dotenv

dotenv.load_dotenv()

court_form = {
    '__EVENTTARGET': r'ctl00$ContentPlaceHolder1$btnlocalCaseTab',
    '__VIEWSTATE': r'',
    '__VIEWSTATEGENERATOR': r'AA43A225',
    '__EVENTVALIDATION': r'',
    'ctl00$ContentPlaceHolder1$txtLCNYearSTD_localCaseContent': '',
    'ctl00$ContentPlaceHolder1$txtLCNSeqSTD_localCaseContent': '',
    'ctl00$ContentPlaceHolder1$localCaseCodesSelect_localCaseContent': '',
    'ctl00$ContentPlaceHolder1$txtLCNLocSTD_localCaseContent': '',
    }

login = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': '',
    '__VIEWSTATEGENERATOR': '54B42DA6',
    '__EVENTVALIDATION': '',
    'ctl00$cphPage$txtUserName': os.getenv('court_username'),
    'ctl00$cphPage$txtPassword': os.getenv('court_password'),
    'ctl00$cphPage$btnLogin': 'Login',
    'ctl00$cphPage$registrationEmail': ''
}

headers = {
    'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,' 
            'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7,es-US;q=0.6,es;q=0.5',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '1232',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': ('ASP.NET_SessionId=xabja4cwyyrgkpdrcl5n5lu4;'
                ' __AntiXsrfToken=a8dadbfb6e774ab2831a9ed2f8feffef;' 
                ' _gid=GA1.2.964453547.1691256342;' 
                ' NSC_xxx2.njbnjebefdmfsl.hpw_TTM=ffffffff09303f1645525d5f4f58455e445a4a42378b;' 
                ' _ga_RYBB2RRWJF=GS1.1.1691260350.4.1.1691261737.0.0.0;' 
                ' _ga=GA1.1.152267289.1691121245'),
    'Host': 'www2.miamidadeclerk.gov',
    'Origin': 'https://www2.miamidadeclerk.gov',
    'Referer': 'https://www2.miami-dadeclerk.gov/PremierServices/login.aspx',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                ' AppleWebKit/537.36 (KHTML, like Gecko)'
                ' Chrome/86.0.4240.198 Safari/537.36')
    }
