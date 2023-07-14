import json
import boto3
import os
from lambdasP import decimalencoder

def handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Danish-python-api-Patient')
    
    result = table.get_item(
        Key={
            'id': event['id']
        }
    )


    if "Item" in result: 
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Item'],  cls=decimalencoder.DecimalEncoder)
        }
    else:
        response = {
            "statusCode": 201,
            "body": "No such Item Exist in Database!!.."
        }

    return response

