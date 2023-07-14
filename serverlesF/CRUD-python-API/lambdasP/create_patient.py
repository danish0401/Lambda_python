import json
import logging
import boto3
import uuid
import os
import re

def handler(event, context):
    data = event['body'].copy()

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Danish-python-api-Patient')
    # table2 = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    if "P_Name" in data and "P_Disease" in data and "Email" in data and type(data['P_Name'] == str) and type(data['P_Disease'] == str) and type(data['Email'] == str):
        valid=re.compile('[A-Za-z]{2,25}( [A-Za-z]{2,25})?')
        email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # print("data", event)
        if(re.fullmatch(valid, data['P_Name']) and re.fullmatch(valid, data['P_Disease']) and re.fullmatch(email, data['Email'])):

            scan = table.scan()
            if not(next((item for item in scan["Items"] if item["Email"] == data['Email'].lower()),None)):
                item = {
                    'id' : str(uuid.uuid1()),
                    'Patient_Name' : data['P_Name'],
                    'Disease' : data['P_Disease'],
                    'Email' : data['Email']
                }
                table.put_item(Item=item)

                response = {
                    "statusCode": 200,
                    "body": json.dumps(item)
                }                    
            else:
                response = {
                    "statusCode": 200,
                    "body": "Err:: Seems like email is already in use try again with another email!.."
                }        
        else:
            response = {
                    "statusCode": 201,
                    "body": "Please Enter a Valid Patient Name or Disease Name"
            }
    else:
        response = {
                "statusCode": 202,
                "body": "Please Review your event body you may have misspelled some parameters orentered them with wrong type::, required are 'P_Name'(str), 'P_Disease'(str), 'Email'(str)" 
        }

    return response
