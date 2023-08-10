import requests
from bs4 import BeautifulSoup



# THIS .py INCLUDES FORMS AND FUNCTIONS NECESSARY FOR ACCESSING MIAMI DADE CIRCUIT COURT DATE - ASPX SCRAPING


def getViewState(url):

    r = requests.post(url, cookies=header)
    soup = BeautifulSoup(r.text, features='lxml')

    viewState = soup.select("#__VIEWSTATE")[0]['value']
    eventValidation = soup.select('#__EVENTVALIDATION')[0]['value']

    return [viewState, eventValidation]

courtForm = {
    '__EVENTTARGET': r'ctl00$ContentPlaceHolder1$btnlocalCaseTab',
    '__VIEWSTATE': r'',
    '__VIEWSTATEGENERATOR': r'AA43A225',
    '__EVENTVALIDATION': r'',
    'ctl00$ContentPlaceHolder1$txtLCNYearSTD_localCaseContent': '',
    'ctl00$ContentPlaceHolder1$txtLCNSeqSTD_localCaseContent': '',
    'ctl00$ContentPlaceHolder1$localCaseCodesSelect_localCaseContent': '',
    'ctl00$ContentPlaceHolder1$txtLCNLocSTD_localCaseContent': '',
    }

loginForm = {
    '__EVENTTARGET': '',
    '__EVENTARGUMEN': '',
    '__VIEWSTATE': '58ndqrx71N0Hwpg5CnIy1/uFsvDRPy/fDKyu0hfAQACsrDWd0lJTbe/JBNH+WhVmv4fteKkGmL9G4L9Gx8OyTq/IxWre/dxsJ+BPDWvW4QKOnj0mHBWUX8ZLOnJS+QzcUK3yTxwl6rm6hGvYqfnICkqGR/WCQVl1ZYqk/kdcypp7n6oRuf40bXTAYU1kGAJEtTV5Zgz7Vwx7QN+zwnfGAyu1/xGKH/NNm+tQr6N6w9uS7TIelR/AOtO0rKyXOC5g8ewqk5bUOU7ZLyiM5dutzVJKLJ1YCM7KO7tsKcMD3rhxiEFRMrhFZH7c6ywVbhSt5XpGkcIw/Eo9eiKW2al+F9ajMua/K/IXMAgBJj8j3QdynlVU/1/YdpusvN60ZoA0PVZrqbhL1rSlHpVR0LTnee2k84t3fnAtQEZlRd0UfaJRuylG+Qb00PgCeKIyOYjw9YSf3XITWNTFciYV8Gq5LahMqXELoTr6Iu8wqHe1038bOg9ZfPKRK+j/q9Eg9o7YZA26OwyfmMtb6h/ShukqH+vX6JlIGZ8ALMJGqEwVzU2Bt9rbN62LMoU0A2Ez5W2RFSCRjJCdUNG8mENFFaK1//j7joTYGgkuDDgX6N8fZRYvco7LLJU53AAshyFr5Jcf1zpbrr05rpObabHSgJNXf2K/CCjCyuIYiQMrJ/RgVdOYOZ99v37+zTMocNnRcL8C3SCHAA==',
    '__VIEWSTATEGENERATOR': '54B42DA6',
    '__EVENTVALIDATION': '9tHjxFEPTTwTUVt1Gg0suNnf54V+3SFUaVV5R3kFiUIK1y8AspU6wywGQM4iKc1RvamKYkym7VZQIv7M8HxtoX7EIewoQ4MZKLMtQ478Nf7RhPI5Y6TisemE46MBUch40SqpdkwmC8XkC2hIMAvVu9uKy6ZEm1EOu79jSojZMY7idXrnpg/YxAfzNfqtL5og5B6XfQ==',
    'ctl00$cphPage$txtUserName': 'GusCosta',
    'ctl00$cphPage$txtPassword': 'Capital161531',
    'ctl00$cphPage$btnLogin': 'Login'
}

header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7,es-US;q=0.6,es;q=0.5',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '1232',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '_ga=GA1.2.1638197099.1589566988; ASP.NET_SessionId=5fdphz4neqqbqqoad5ftlma0; __RequestVerificationToken_L0RldmVsb3BlcnM1=-gt0LY9usvVp97TyuxB1p447xI5cD8-HsW42cj0bWkvSEM1xmqq5jKsyy7CCG_RE4JgOTLXF5X4GH4jho_ur-lQ3FAU1; .COCDEVELOPERS=777723C51D5A0CA790EAA09E4C44F0CB5F376D392AD5D7B8882A8AC6F115019B6CA16DB965E664EF05BBD7BC78BC9C2B61A52BABF587DE87D081FC1CE899E843BCBDC8EA3B326B5531D9A25BFCD8AA42039B95C2EE6F887EFE4DD07A0C73BACE00F74A3468ED33E73203AF0E9E99B0D384135B7A232DD65DD77E8C5468AB556D67A51F2D; NSC_xxx2.njbnj-ebefdmfsl.dpn_TTM=ffffffff09303f1745525d5f4f58455e445a4a42378b; __AntiXsrfToken=87eed7b3f7484bf7be45228ca6446b8b; _gid=GA1.2.1675938187.1606156764; _gat_gtag_UA_2461186_13=1',
    'Host': 'www2.miami-dadeclerk.com',
    'Origin': 'https://www2.miami-dadeclerk.com',
    'Referer': 'https://www2.miami-dadeclerk.com/PremierServices/login.aspx',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}