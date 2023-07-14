import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def add_users(chanel_Id, List_of_users):
    response = client.conversations_invite(channel=chanel_Id, users= List_of_users)
    return response

def remove_users(chanel_Id, List_of_users):
    response=""
    for user in List_of_users:
        response = client.conversations_kick(channel=chanel_Id, user= user)    
    return response

def List_members_in_channel(chanel_Id, Lead_Id):
    response=client.conversations_members(channel=chanel_Id)
    response= response["members"][:-1]
    response.remove(Lead_Id)
    return response


try:
    # slack_token = os.environ["slack_token"]
    client = WebClient(token="xoxb-497707237954-4406681876644-U0ddOcSvBtwGbYkertryaula")

    Users_on_call=['U03QTU888CQ','U039016GG0K', 'U03LJ0KDM5W']
    Lead_Id="UFN7Q9S04"

    current_members=List_members_in_channel("C04MCE18PPD", Lead_Id)
    print("Current users:",current_members)


    List_of_users_rem=[]

    for obj in current_members:
        if obj not in Users_on_call:
            List_of_users_rem.append(obj)

    print("Users to add/remain:",Users_on_call)
    print("Users to remove:", List_of_users_rem)

    # Add User to private channel
    # here you can pass list of users to invite in a channel using this API
    add_users("C04MCE18PPD", Users_on_call)
    remove_users("C04MCE18PPD", List_of_users_rem)

except SlackApiError as e:
    print("error:", e.response["error"])
    assert e.response["error"]

finally:
    remove_users("C04MCE18PPD", List_of_users_rem)


