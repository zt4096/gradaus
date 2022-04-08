import requests
import csv
import os
from datetime import datetime

headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'accept': '*/*',
    'content-type': 'text/plain',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'Origin': 'https://gradaustralia.com.au',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://gradaustralia.com.au/',
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,de;q=0.7',
}
links = []
date = datetime.today().strftime('%d-%m-%Y')
page_num = 0
while True:
    params = (
        ('queryId', 'bdbf3a43ca8c5ad87479743e28be1a0ec883709d:37'),
        ('operationName', 'SearchCareerOpportunity'),
        ('variables', f'{{"gid":["6"],"index_id":"anabranch_connect_index","condition_group":{{"groups":[{{"conditions":[{{"name":"gid","operator":"=","value":"6"}},{{"name":"node_type","operator":"=","value":"career_opportunity"}},{{"name":"published","operator":"=","value":"1"}},{{"name":"expired","operator":"<>","value":"1"}},{{"name":"inactive_organisation","operator":"<>","value":"1"}},{{"name":"inactive_content","operator":"<>","value":"1"}}]}},{{"conditions":[],"conjunction":"OR","tags":["facet:study_field_tids"]}},{{"conditions":[],"conjunction":"OR","tags":["facet:opportunity_types"]}},{{"conditions":[],"conjunction":"OR","tags":["facet:locations"]}},{{"conditions":[],"conjunction":"OR","tags":["facet:industry_sectors"]}}],"conjunction":"AND"}},"range":{{"offset":{page_num},"limit":8}},"sort":[{{"field":"field_sticky","value":"desc"}},{{"field":"field_weight","value":"asc"}},{{"field":"applications_close_date","value":"asc"}}],"facets":[{{"field":"study_field_tids","limit":0,"operator":"OR","missing":false,"min_count":1}},{{"field":"opportunity_types","limit":0,"operator":"OR","missing":false,"min_count":1}},{{"field":"locations","limit":0,"operator":"OR","missing":false,"min_count":1}},{{"field":"industry_sectors","limit":0,"operator":"OR","missing":false,"min_count":1}}]}}'),
    )
    response = requests.get('https://prosple-content-api.global.ssl.fastly.net/graphql', headers=headers, params=params)
    nodes = response.json()['data']['searchAPISearch']['groupNodes']
    if len(nodes) == 0:
        break
    for node in nodes:
        links.append(node['entityUrl']['path'])
    print(len(set(links)),end=',')
    page_num += 8

for link in links:
    params = (
        ('queryId', 'bdbf3a43ca8c5ad87479743e28be1a0ec883709d:51'),
        ('operationName', 'GroupContentCareerOpportunity'),
        ('variables', f'{{"path":"{link}","gid":["6"]}}'),
    )

    response = requests.get('https://prosple-content-api.global.ssl.fastly.net/graphql', headers=headers, params=params)
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
    link = link.replace('/group/6','https://gradaustralia.com.au')
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