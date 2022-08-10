import requests
import csv
import os
from datetime import datetime

headers = {
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,de;q=0.7',
    'Connection': 'keep-alive',
    'Origin': 'https://gradaustralia.com.au',
    'Referer': 'https://gradaustralia.com.au/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'accept': '*/*',
    'content-type': 'application/json',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}
links = []
num = 0
while True:
    params = {
        'operationName': 'OpportunitiesSearch',
        'variables': f'{{"parameters":{{"gid":"6","range":{{"offset":{num},"limit":20}},"sortBy":{{"criteria":"POPULARITY","direction":"DESC"}}}}}}',
        'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"d7f497655d4deedfcf0ffe14f865e9803130e5a0a519018eb935d57c210cc048"}}',
    }

    response = requests.get('https://prosple-gw.global.ssl.fastly.net/internal', params=params, headers=headers)
    nodes = response.json()['data']['opportunitiesSearch']['opportunities']
    if len(nodes) == 0:
        break
    for node in nodes:
        link = node['detailPageURL']
        links.append(link)
    print(len(set(links)),end=',')
    num += 20

for link in links:
    params = {
        'queryId': '542f850b108aa27e8bf1227a8bba4be0f1d43b78:49',
        'operationName': 'GroupContentCareerOpportunity',
        'variables': f'{{"path":"/group/6{link}","gid":["6"]}}',
    }

    response = requests.get('https://prosple-content-api.global.ssl.fastly.net/graphql', params=params, headers=headers)
    data = response.json()['data']['content']['entity']
    title = data['entityIdOfGroupContent']['entity']['title']
    otype = data['entityIdOfGroupContent']['entity']['fieldOpportunityTypes'][0]['entity']['entityLabel']
    try:
        sdate = data['entityIdOfGroupContent']['entity']['fieldStartDate']['startDate']['date']
    except:
        sdate = ''
    try:
        aodate = data['entityIdOfGroupContent']['entity']['fieldApplicationsOpenDate']['date']
    except:
        aodate = ''
    try:
        acdate = data['entityIdOfGroupContent']['entity']['fieldApplicationsCloseDate']['date']
    except:
        acdate = ''
    loc = data['entityIdOfGroupContent']['entity']['fieldLocationDescription']
    summary = data['entityIdOfGroupContent']['entity']['fieldOverview']['summaryProcessed']
    description = data['entityIdOfGroupContent']['entity']['fieldOverview']['processed']
    company = data['entityIdOfGroupContent']['entity']['fieldParentEmployer']['entity']['title']
    min_vacancies = data['entityIdOfGroupContent']['entity']['fieldMinNumVacancies']
    max_vacancies = data['entityIdOfGroupContent']['entity']['fieldMaxNumVacancies']
    try:
        fields = '; '.join([i['entity']['entityLabel'] for i in data['entityIdOfGroupContent']['entity']['fieldPathways'][0]['entity']['fieldRequirements'][0]['entity']['fieldStudyField']])
    except:
        fields = ''
    try:
        rows= data['entityIdOfGroupContent']['entity']['fieldWorkRights'][0]
        fieldlocation = rows['entity']['fieldLocations']['entity']['entityLabel']
        rrows = rows['entity']['fieldWorkRights']
        fwr = ', '.join([i['entity']['entityLabel'] for i in rrows])
    except:
        rows = ''
        fieldlocation =''
        rrows = ''
        fwr = ''  
    try:
        employees = data['entityIdOfGroupContent']['entity']['fieldParentEmployer']['entity']['fieldNumEmployees']['entity']['entityLabel']
    except:
        employees = ''
    link = 'https://gradaustralia.com.au'+link
    if os.path.exists('gaus.csv'):
        newfile = False
    else:
        newfile = True
    results = [[date,link,title,otype,sdate,aodate,acdate,loc,summary,description,company,min_vacancies,max_vacancies,fields,fieldlocation,fwr,employees]]
    with open('gaus.csv','a',newline='',encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if newfile:
            writer.writerows([['Date of Scrape','Link','Title','Op. Type','Starting Date','Open Date','Close Data',
                              'Location','Summary','Description','Company','Min. Vacancies',
                              'Max. Vacancies','Qualifications','Field Location','FWR','Employees']])
        writer.writerows(results)
    print('.',end='')
