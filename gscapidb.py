import json
import webbrowser
import requests
import PySimpleGUI as sg
import pandas as pd
import csv
from pathlib import Path

sg.theme("Topanga")

#GUI for Credentials
user_input_layout = [
    [sg.Text('Enter User Parameters')],
    [sg.Text('client_id', size=(70, 1)), sg.InputText('')],
    [sg.Text('client_secret', size=(70, 1)), sg.InputText('')],
    [sg.Text('api_key', size=(70, 1)), sg.InputText('')],
    [sg.Text('site_url', size=(70, 1)), sg.InputText('')],
    [sg.Submit(), sg.Cancel()]
]
window = sg.Window('GSCAPI Userinfo', user_input_layout)    
event, user_values = window.read()    
window.close()

client_id = user_values[0]
client_secret = user_values[1]
api_key = user_values[2]
site_url = user_values[3]

#GUI / Browser add Authentification-Code
browser_link = 'https://accounts.google.com/o/oauth2/v2/auth?client_id='+client_id+'&redirect_uri=urn:ietf:wg:oauth:2.0:oob&scope=https://www.googleapis.com/auth/webmasters.readonly&response_type=code'
webbrowser.open(browser_link, new=2)
 
auth_key_layout = [
    [sg.Text('auth_key', size=(70, 1)), sg.InputText()],
    [sg.Submit()]
]
window = sg.Window('GSCAPI Authentificationkey', auth_key_layout)    
event, auth_key_values = window.read()    
window.close()
 
auth_key = auth_key_values[0]
 
#Get Accesstoken
r = requests.get('https://accounts.google.com/.well-known/openid-configuration')
rjson = r.json()
token_endpoint = rjson['token_endpoint']
access_token_data = {'code':auth_key,'client_id':client_id,'client_secret':client_secret,'redirect_uri':'urn:ietf:wg:oauth:2.0:oob','grant_type':'authorization_code'}
access_token_request = requests.post(token_endpoint, data = access_token_data)
access_token_request_json = access_token_request.json()
access_token = access_token_request_json['access_token']
refresh_token = access_token_request_json["refresh_token"]
 
#Build API Request
api_request_header = {'Authorization':'Bearer '+access_token,'Accept':'application/json','Content-Type':'application/json'}
api_request_url = 'https://searchconsole.googleapis.com/webmasters/v3/sites/'+site_url+'/searchAnalytics/query?key='+auth_key
#"""
#""" 
#Get Request Data
data_layout = [
    [sg.Text('Enter Data Parameters')],
    [sg.Input('2021-06-01',key='StartDate', size=(70,1)), sg.CalendarButton('Pick StartDate', close_when_date_chosen=True,  target='StartDate', location=(120,120), no_titlebar=False, format = "%Y-%m-%d")],
    [sg.Input('2021-06-31',key='EndDate', size=(70,1)), sg.CalendarButton('Pick EndDate', close_when_date_chosen=True,  target='EndDate', location=(120,120), no_titlebar=False, format = "%Y-%m-%d")],
    [sg.Text('dimensions (grouping):', size = (70, 1)),sg.Radio('country','dimensions',default=False,key='dimensions:country'),sg.Radio('device','dimensions',default=False,key='dimensions:device'),sg.Radio('page','dimensions',default=False,key='dimensions:page'),sg.Radio('query','dimensions',default=True,key='dimensions:query'),sg.Radio('searchAppearance','dimensions',default=False,key='dimensions:searchAppearance')],
    [sg.Text('searchType:', size = (70, 1)),sg.Radio('news','searchType',default=False,key='searchType:news'),sg.Radio('image','searchType',default=False,key='searchType:image'),sg.Radio('video','searchType',default=False,key='searchType:video'),sg.Radio('web','searchType',default=True,key='searchType:web'),],
    [sg.Text('groupType - must be "and"', size = (70, 1)), sg.InputText('and')],
    [sg.Text('dimension (filtering):', size = (70, 1)), sg.InputText('query')],
    [sg.Text('operator:', size = (70, 1)),sg.Radio('contains','operator',default=True,key='operator:contains'),sg.Radio('equals','operator',default=False,key='operator:equals'),sg.Radio('notContains','operator',default=False,key='operator:notContains'),sg.Radio('notEquals','operator',default=False,key='operator:notEquals')],
    [sg.Text('aggregationType', size = (70, 1)),sg.Radio('auto','aggregationType',default=True,key='aggregationType:auto'),sg.Radio('byProperty','aggregationType',default=False,key='aggregationType:byProperty'),sg.Radio('byPage','aggregationType',default=False,key='aggregationType:byPage')],
    [sg.Text('rowLimit', size = (70, 1)), sg.InputText('25000')],    
    [sg.Text('startRow', size = (70, 1)), sg.InputText('0')], 
    [sg.Submit()]
]       
 
#Enter GSCAPI Request Data
window = sg.Window('GSCAPI Data', data_layout)    
event, values = window.read()    
window.close()
startDate = values['StartDate']
endDate = values['EndDate']
if(values['dimensions:query'] == True):
    dimensions = 'query'
elif(values['dimensions:country'] == True):
    dimensions = 'country',
elif(values['dimensions:device'] == True):
    dimensions = 'device'
elif(values['dimensions:page'] == True):
    dimensions = 'page'
elif(values['dimensions:searchAppearance'] == True):
    dimensions = 'searchAppearance'

if(values['searchType:news'] == True):
    searchType = 'news'
elif(values['searchType:image'] == True):
    searchType = 'image'
elif(values['searchType:video'] == True):
    searchType = 'video'
elif(values['searchType:web'] == True):
    searchType = 'web'

if(values['operator:contains'] == True):
    operator = 'contains'
elif(values['operator:equals'] == True):
    operator = 'equals'
elif(values['operator:notContains'] == True):
    operator = 'notContains'
elif(values['operator:notEquals'] == True):
    operator = 'notEquals'

if(values['aggregationType:auto'] == True):
    aggregationType = 'auto'
elif(values['aggregationType:byPage'] == True):
    aggregationType = 'byPage'
elif(values['aggregationType:byProperty'] == True):
    aggregationType = 'byProperty'

groupType = values[0]
dimension = values[1]
rowLimit = values[2]
startRow = values[3]

df = pd.read_csv('query.csv')

for index, row in df.iterrows():
    #Build GSCAPI Request Data
    gsc_request = '''
    {
    "startDate":"'''+startDate+'''",
    "endDate":"'''+endDate+'''",
    "dimensions":["'''+dimensions+'''"],
    "searchType":"'''+searchType+'''",
    "dimensionFilterGroups": [
    {
    "groupType":"'''+groupType+'''",
    "filters": [
            {
            "dimension":"'''+dimension+'''",
            "operator":"'''+operator+'''",
            "expression":"'''+row['query']+'''",
        }
        ]
    }
    ],
    "aggregationType":"'''+aggregationType+'''",
    "rowLimit":"'''+rowLimit+'''",
    "startRow":"'''+startRow+'''",
    }
    '''

    #Call GSCAPI
    gsc_api_request = requests.post(api_request_url, data = gsc_request, headers = api_request_header)
    gsc_answer_json = gsc_api_request.json()
    if "rows" in gsc_answer_json:
        gsc_rows = gsc_answer_json["rows"]
                        
        gsc_df = pd.json_normalize(gsc_rows)
        
        gsc_df.to_csv('rows'+startDate+'|'+endDate+'.csv',mode = 'a' , index = False, encoding='utf-8')
        print(index)
        print(row)

gsc_rows_df = pd.read_csv('rows'+startDate+'|'+endDate+'.csv')
gsc_rows_df.drop_duplicates(keep = 'first', inplace = True)
gsc_rows_df.to_csv('rows'+startDate+'|'+endDate+'.csv',mode = 'w' , index = False, encoding='utf-8')
