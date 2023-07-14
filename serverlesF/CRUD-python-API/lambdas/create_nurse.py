import json
import logging
import boto3
import uuid
import os
import re


def handler(event, context):
    print("type:",type(event))
    print("event:",event)

    data = event['body'].copy()
    
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    if "Nurse_Name" in data and "Qual" in data and "Email" in data and type(data['Nurse_Name']) == str and type(data['Qual']) == str and type(data['Email'] == str):
        valid=re.compile('[A-Za-z]{2,25}( [A-Za-z]{2,25})?')
        email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        
        # print("data", event)
        if(re.fullmatch(valid, data['Nurse_Name']) and re.fullmatch(valid, data['Qual']) and re.fullmatch(email,data['Email'])):
            
            result = table.scan()
            # print(result['Items'])
            
            if not(next((item for item in result['Items'] if item["Email"] == data['Email'].lower()),None)):
                print("not found")
                item = {
                    'id' : str(uuid.uuid1()),
                    'Nurse_Name' : data['Nurse_Name'],
                    'Qualification' : data['Qual'],
                    'Email' : data['Email'].lower(),
                    'No_of_ptnt' : 0
    
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
                "statusCode": 200,
                "body": "Please Enter valid names,email and Qualification 'Your name may contains integers in it' or 'Your Email may be Invalid' verify that and continue "
            }
    else:
        response = {
                "statusCode": 200,
                "body": "Please Review event body,you may have misspelled some parameters or entered wrong type:: required are 'Nurse_Name'(str), 'Qual'(str), 'Email'(str) "
        }
    
    return response
