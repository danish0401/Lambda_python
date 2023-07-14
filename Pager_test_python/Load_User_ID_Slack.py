import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


pager_duty_metadata={
  "users": [
    {
      "id": "PAM4FGS",
      "type": "user",
      "summary": "Kyler Kuhn",
      "self": "https://api.pagerduty.com/users/PAM4FGS",
      "html_url": "https://subdomain.pagerduty.com/users/PAM4FGS",
      "name": "Akbar Alam",
      "email": "126_dvm_kyler_kuhn@beahan.name",
      "time_zone": "Asia/Hong_Kong",
      "color": "red",
      "role": "admin",
      "avatar_url": "https://secure.gravatar.com/avatar/47857d059adacf9a41dc4030c2e14b0a.png?d=mm&r=PG",
      "description": "Engineer based in HK",
      "invitation_sent": False,
      "contact_methods": [
        {
          "id": "PVMGSML",
          "type": "email_contact_method_reference",
          "summary": "Work",
          "self": "https://api.pagerduty.com/users/PAM4FGS/contact_methods/PVMGSMLL"
        }
      ],
      "notification_rules": [
        {
          "id": "P8GRWKZ",
          "type": "assignment_notification_rule_reference",
          "summary": "Default",
          "self": "https://api.pagerduty.com/users/PAM4FGS/notification_rules/P8GRWKZ",
          "html_url": ""
        }
      ],
      "job_title": "Senior Engineer",
      "teams": [
        {
          "id": "PQ9K7I8",
          "type": "team_reference",
          "summary": "Engineering",
          "self": "https://api.pagerduty.com/teams/PQ9K7I8",
          "html_url": "https://subdomain.pagerduty.com/teams/PQ9K7I8"
        }
      ]
    },
    {
      "id": "PXPGF42",
      "type": "user",
      "summary": "Earline Greenholt",
      "self": "https://api.pagerduty.com/users/PXPGF42",
      "html_url": "https://subdomain.pagerduty.com/users/PXPGF42",
      "name": "Danish",
      "email": "125.greenholt.earline@graham.name",
      "time_zone": "America/Lima",
      "color": "green",
      "role": "admin",
      "avatar_url": "https://secure.gravatar.com/avatar/a8b714a39626f2444ee05990b078995f.png?d=mm&r=PG",
      "description": "I'm the boss",
      "invitation_sent": False,
      "contact_methods": [
        {
          "id": "PTDVERC",
          "type": "email_contact_method_reference",
          "summary": "Default",
          "self": "https://api.pagerduty.com/users/PXPGF42/contact_methods/PTDVERC"
        }
      ],
      "notification_rules": [
        {
          "id": "P8GRWKK",
          "type": "assignment_notification_rule_reference",
          "summary": "Default",
          "self": "https://api.pagerduty.com/users/PXPGF42/notification_rules/P8GRWKK",
          "html_url": ""
        }
      ],
      "job_title": "Director of Engineering",
      "teams": [
        {
          "id": "PQ9K7I8",
          "type": "team_reference",
          "summary": "Engineering",
          "self": "https://api.pagerduty.com/teams/PQ9K7I8",
          "html_url": "https://subdomain.pagerduty.com/teams/PQ9K7I8"
        }
      ]
    }
  ]
}

on_call_users = [items["name"] for items in pager_duty_metadata["users"]]
print(on_call_users )
on_call_users=["Wajahat", "Akbar Alam", "Danish Hafeez", "Faisal Nawaz", "Junaid Malik"]

try:

    # slack_token = os.environ["slack_token"]
    client = WebClient(token="xoxb-497707237954-4406681876644-U0ddOcSvBtwGbYkertryaula")

    # Script to Load names and Id of all users
    response = client.users_list()
    users = response["members"]
    user_names = list(map(lambda u: u["profile"]["real_name"], users))
    user_ids = list(map(lambda u: u["id"], users))
    is_bot = list(map(lambda u: u["is_bot"], users))
    Users_Dict=[]
    for name,ids,isbot in zip(user_names,user_ids,is_bot):
        if isbot == False:
            Users_Dict.append({"Name":name,"ID":ids})

    List_of_users_add=[]
    for items in Users_Dict:
        for obj in on_call_users:
            if obj in items['Name']:
                List_of_users_add.append(items)
    
    print(List_of_users_add)

except SlackApiError as e:
    print("error:", e.response["error"])
    assert e.response["error"]
