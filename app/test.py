import requests
import json

REGISTER_URL = 'http://localhost:5000/register-user'
ADDTO_INFODB_URL = 'http://localhost:5000/addto-infodb'
REMOVEFROM_INFODB_URL = 'http://localhost:5000/removefrom-infodb'
UPDATE_INFODB_URL = 'http://localhost:5000/update-infodb'
GETDATA_INFODB_URL = 'http://localhost:5000/getdata-infodb'

date = [2024, 8, 23, 19, 51, 17]
#print(f"""
#Year: {date[0]},
#Month: {date[1]},
#Day: {date[2]},
#Time: {date[3]}:{date[4]}
#""")


name = 'alex'
password = '123'
email = 'alex@example.com'
session_id = 'vncedAHgQCJnoD8Mei6I4dgORIsFEb-Ac-EBoOoljHL2_eS5S3gmIc1AWGgVqLuqHsH21uLU74vDvokRQ-Tu8ZukT_wgp2RblgpBuHcN7YXLZ_z--sF4A49EGLrBEbRI'

infotitle = "Gmail Account"
infoname = "Alex"
infomail = "Alex@gmail.com"
infopass = "222"
infodesc = "This is my Gmail account info"
website = "https://gmail.com"

id = 3

response = requests.post(ADDTO_INFODB_URL, json={'session_id': f'{session_id}', 'infotitle': f'{infotitle}', 'infoname': f'{infoname}', 'infopass': f'{infopass}', 'infomail': f'{infomail}', 'infodesc': f'{infodesc}', 'website': f'{website}'})
#response = requests.post(REMOVEFROM_INFODB_URL, json={'session_id': f'{session_id}', 'id': f'{id}'})
#response = requests.post(UPDATE_INFODB_URL, json={'session_id': f'{session_id}', 'id': f'{id}'})
# response = requests.post(GETDATA_INFODB_URL, json={'session_id': f'{session_id}'})

if response.status_code == 200:
    data = response.json()
    data_string = data['data']
    data_string = data_string.replace("'", '"')
    data_list = json.loads(data_string)
    
    for item in data_list:
        print(item)
else:
    data = response.json()
    print(data)