import requests
import json

url = "http://localhost:8008/struct"
headers = {"Content-Type": "application/json"}

def struct(text:str="carcinoma de mama"):

    data = {"text": text}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = {'data': False}

    if response.status_code == 200:
        result = {'data': response.json()}
        #print(result)
    else:
        print("Error code:", response.status_code)

    return result
