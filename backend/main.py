import sys
import os
import requests
import json



def post_fake_data(data):
    r = requests.post(
        url="https://127.0.0.1:5000/getcommits",
        data=json.dumps(data),
        headers={'Content-type': 'application/json; charset=utf-8'}
    )
    print(r)


def load_json():
    path="./json_generated"
    files = os.listdir(path)
    
    for file in files:
        if os.path.isdir(file):
            continue
        
        f = open(path + "/" + file, "r")
        data = json.load(f)
        print(data)

        post_fake_data(data)


if __name__ == "__main__":
    os.environ['FLASK_APP']="../backend"
    os.system("flask init-db")
    load_json()
    os.system("flask run")