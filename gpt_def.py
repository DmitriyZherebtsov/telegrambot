import requests
import json
import config
import uuid

def conn_gpt(user):

    payload = 'scope=GIGACHAT_API_PERS'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': uuid.uuid4(),
        'Authorization': 'Basic ' + config.gpt_auth
    }

    response = requests.request("POST", config.gpt_url_auth, headers=headers, data=payload, verify=False)
    response_json = response.json()


    payload = json.dumps({
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": "Подготовь поздравление на день рождения для человека возрастом" + user[1] + "с описанием:" +
                           user[2] + ". Имя человека:" + user[0]
            }
        ],
        "stream": False,
        "repetition_penalty": 1
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + response_json['access_token']
    }

    response = requests.request("POST", config.gpt_url_result, headers=headers, data=payload, verify=False)
    response_json = response.json()
    return (response_json['choices'][0]['message']['content'])