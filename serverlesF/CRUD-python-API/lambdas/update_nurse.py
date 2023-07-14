import json
import boto3
import os
import re

from lambdas import decimalencoder

def handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    data = event['body'].copy()
    if "id" in data and "New_Name" in data and "New_Qual" in data and type(data['New_Name']) == str and type(data['New_Qual']) == str and type(data['id']) == str:    
        valid=re.compile('[A-Za-z]{2,25}( [A-Za-z]{2,25})?')
        # email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # print("data", event)
        if(re.fullmatch(valid, data['New_Name']) and re.fullmatch(valid, data['New_Qual'])):

            result = table.update_item( 
                Key={
                    'id': data['id']
                },
                UpdateExpression='SET Nurse_Name= :New_Name, '
                                'Qualification= :New_Qual',
                ExpressionAttributeValues={
                    ':New_Name': data["New_Name"],
                    ':New_Qual': data["New_Qual"]
                },
                ReturnValues="UPDATED_NEW"
            )

            
            response = {
                "statusCode": 200,
                "body": json.dumps(result['Attributes'],  cls=decimalencoder.DecimalEncoder)
            }

        else:
            response = {
                "statusCode": 200,
                "body": "Please Enter valid names,email and Qualification 'Your name may contains integers in it' or 'Your Email may be Invalid' verify that and continue"
            }
    else:
        response = {
                "statusCode": 200,
                "body": "Please Review event body,you may have misspelled some parameters or entered wrong type:: required are 'New_Name'(str), 'New_Qual'(str), 'New_Email'(str), 'id'(str) "        
        }
    return response

