import json
import boto3
import os
import re
from lambdasP import decimalencoder

def handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Danish-python-api-Patient')
    data = event['body'].copy()

    valid=re.compile('[A-Za-z]{2,25}( [A-Za-z]{2,25})?')

    if "New_Name" in data and "New_Dis" in data and "id" in data and type(data['New_Name'] == str) and type(data['New_Dis'] == str) and type(data['id'] == str):   
        if(re.fullmatch(valid, data['New_Name']) and re.fullmatch(valid, data['New_Dis'])):
            result = table.update_item(
                Key={
                    'id': data['id']
                },
                UpdateExpression='SET Patient_Name= :New_Name, '
                                'Disease= :New_Dis',
                ExpressionAttributeValues={
                    ':New_Name': data["New_Name"],
                    ':New_Dis': data["New_Dis"]
                },
                ReturnValues="UPDATED_NEW"
            )
            response = {
                "statusCode": 200,
                "body": json.dumps(result['Attributes'], cls=decimalencoder.DecimalEncoder)
            }
        else:
            response = {
                    "statusCode": 201,
                    "body": "Please Enter a Valid Patient Name or Disease Name"
            }
    else:
        response = {
                "statusCode": 202,
                "body": "Please Review your event body you may have misspelled some parameters or entered them with wrong type::, required are 'New_Name'(str), 'New_Dis'(str) and 'id'(str) "        
        }


    return response

