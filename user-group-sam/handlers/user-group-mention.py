import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt import App
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import datetime
import time
import urllib3

http = urllib3.PoolManager()
pakistan_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=0))

dynamodb = boto3.resource('dynamodb')
table_name = os.environ["DYNAMODB_TABLE_NAME"]
table = dynamodb.Table(table_name)
USER_GROUP_NAME = os.environ["USER_GROUP_NAME"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
FORWARD_MESSAGE_CHANNEL_WEBHOOK_URL = os.environ["FORWARD_MESSAGE_CHANNEL_WEBHOOK_URL"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_client = WebClient(token=SLACK_BOT_TOKEN)

slack_app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)
handler = SlackRequestHandler(slack_app)

def get_simple_template( text):
    empty_data = {"text":text, "blocks": []}
    empty_data["blocks"].append(get_single_template("section", "mrkdwn", text , False))
    return empty_data
    
def get_single_template(templateType="section", textType="plain_text", textContent="",  isEmoji=True ):
    body= {
            "type": templateType,
            "text": {
                "type": textType,
                "text": textContent
            }
            }
    if isEmoji:
        body["text"]["emoji"] = True
    return body

def item_exists(message_ts):
    response = table.query(
        KeyConditionExpression=Key('MESSAGE_TS').eq(message_ts)
    )
    items = response['Items']
    if items:
        return True
    else:
        return False
        
def create_item(message_ts):
    current_epoch_time = int(time.time())
    one_day_from_now = current_epoch_time + 86400
    table.put_item(Item={'MESSAGE_TS': message_ts, "ttl": one_day_from_now})

    
def get_message_format(user, channel, link, message_text):
    pakistan_time = datetime.datetime.now(pakistan_tz)
    message = """ *Posted By:* <@{user}>\n*Channel:* <#{channel}|general>\n*Message Time:* {messag_time}\n*Link:* {link}Click to open message> """.format(user=user, channel=channel, messag_time=str(pakistan_time).split(".")[0], link=link, message_text=message_text) 
    return message
    
@slack_app.event("message")
def handle_mention(event, client):
    print("Verifying for first time.")

# Define the Lambda function
def lambda_handler(event, context):
    print("Incomming Event : ", event)
    # for verification 
    if "challenge" in event["body"] and "url_verification" in event["body"]:
        print("Verifying for first time")
        return handler.handle(event, context)
        
    json_body= event['body']
    event_str=json.loads(json_body)
    body = event_str['event']
    
    print("Handling mentions")    
    try:
        print("App text event : ", body)
        print("Text : ", body["text"])
        print("Event TS : ", body["event_ts"])
        print("Channel :", body["channel"])
        
        user_group_mention = USER_GROUP_NAME
        if user_group_mention in body["text"]:
            event_ts = body["event_ts"]

            if not item_exists(event_ts):
                create_item(event_ts)
                message_text = body["text"].replace(user_group_mention, "")
                response = slack_client.chat_getPermalink(channel=body["channel"], message_ts=event_ts  )
                permalink = response["permalink"]
                permalink = "<" + permalink +"|"
                message_format = get_message_format(body["user"], body["channel"], permalink, message_text)
                message_to_send = get_simple_template(message_format +"\n")
                print("Message to send :", message_to_send)
                # slack_client.chat_postMessage(**message_to_send)
                encoded_msg = json.dumps(message_to_send).encode('utf-8')
                resp = http.request('POST', FORWARD_MESSAGE_CHANNEL_WEBHOOK_URL, body=encoded_msg)
    except SlackApiError as e:
        print("Error getting permalink: {}".format(e))
    return ""
    

    

