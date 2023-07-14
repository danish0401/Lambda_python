import json
import os
import boto3
import base64
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = os.environ['SECRET_NAME']
chanel_Id = os.environ['chanel_Id']




def lambda_handler(event, context):

    try:
        slack_id = getSecret()
        client = WebClient(token=slack_id)   

        pg_users_oncall = get_pagerduty_oncall_users()
        pg_users_oncall_slack_ids = get_pagerduty_users_slack_ids(pg_users_oncall)
        oncall_watchers = get_oncall_watchers()
        current_oncall_clack_channel =  get_members_in_channel(client, chanel_Id)
        add_users_oncall_slack_group(client, pg_users_oncall_slack_ids, oncall_watchers, current_oncall_clack_channel)

    except SlackApiError as e:
        print("error:", e.response["error"])
        assert e.response["error"]    
    
    return {
    "statusCode": 200,
    "body": json.dumps({
        "message": "PagerDuty-slack",
    }),
}

def get_pagerduty_oncall_users():
    return ['Danish Hafeez', 'Faisal Nawaz']

def get_oncall_watchers():
    watcher_IDs = os.environ['watcher_IDs']
    watcher_IDs= watcher_IDs.split(",")
    return watcher_IDs

def get_pagerduty_users_slack_ids(users):
    
    slack_mapping = {}
    slack_mapping  ={
        'Wajahat Chaudhry' : 'UFN7Q9S04',
        'Junaid Malik' : 'U039016GG0K',
        'Danish Hafeez' : 'U03LJ0KDM5W',
        'Akbar Alam' : 'U03QTU888CQ',
        'Faisal Nawaz' : 'U0413TQ3G1G'
    }

    slack_ids = []

    for user in users:
        slack_ids.append(slack_mapping[user])

    return slack_ids

def add_users_oncall_slack_group(client, oncall_users, oncall_watchers, current_slack_group_users):
    # 1 - Add oncall_watchers if not exists in current_slack_group_users
    # 2 -  Add oncall_users if not exists in current_slack_group_users
    # 3 - Remove current_slack_group_users if they are not in oncall_users and oncall_watchers
    # case 1
    for user in oncall_watchers:
        if user not in current_slack_group_users:
            add_users(client, chanel_Id, user)
    
    # case 2
    for user in oncall_users:
        if user not in current_slack_group_users:
            add_users(client, chanel_Id, user)
    
    # case 3
    for user in current_slack_group_users:
        if user not in oncall_users and user not in oncall_watchers:
            remove_users(client, chanel_Id, user)


# client = WebClient(token=slack_token)
def get_members_in_channel(client, chanel_Id):
    response=client.conversations_members(channel=chanel_Id)
    response= response["members"][:-1]
    return response

def add_users(client, chanel_Id, List_of_users):
    response = client.conversations_invite(channel=chanel_Id, users= List_of_users)
    return response

def remove_users(client, chanel_Id, user):
    response = client.conversations_kick(channel=chanel_Id, user= user)    
    return response



def getSecret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="us-east-1" )
    get_secret_value_response = client.get_secret_value(
            SecretId=slack_token )
    if 'SecretString' in  get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return secret
    else:
        decode_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return decode_binary_secret