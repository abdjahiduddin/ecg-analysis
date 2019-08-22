import json
import requests
from mongodb import connections

# Define cloud url an users authentications
url = "http://api.iotapps.belajardisini.com"
authentications = {}


# Login to cloud
def login(label):
    user_auth = authentications[label]

    # Send login request
    response = requests.post(
        url + "/user/login",
        data={
            'token': user_auth["token_key"],
            'secret': user_auth["secret_key"]
        }
    )

    # Save authentication token
    content = json.loads(response.content)
    user_auth["auth_token"] = content['token']


# Login all registered user
def authenticate_users():
    except_admin = {"username": {"$ne": "admin"}}
    for user in connections["user"].find(except_admin):
        label = user["username"] + "(" + user["device"] + ")"
        authentications[label] = {}
        user_auth = authentications[label]
        user_auth["age"] = user["age"]
        user_auth["topic"] = user["topic"]
        user_auth["token_key"] = user["token_key"]
        user_auth["secret_key"] = user["secret_key"]
        login(label)
    print("[Cloud] Cloud Authentications: " + str(authentications))


# Check authentication by label
def check_authentication(label):
    if label in authentications.keys():
        return True, authentications[label]["age"]
    else:
        return False, None


# Upload data to cloud
def upload_data(label, data):
    user_auth = authentications[label]

    # Send data to cloud with POST request
    response = requests.post(
        url + "/topic" + user_auth["topic"],
        data={
            'data': json.dumps(data)
        },
        headers={
            'Authorization': "Bearer {}".format(user_auth["auth_token"])
        }
    )