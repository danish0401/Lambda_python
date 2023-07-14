import json
import boto3
import os
from lambdasP import decimalencoder


def handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Danish-python-api-Patient')    
    result = table.scan()

    if "Items" in result: 
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Items'],
                                    cls=decimalencoder.DecimalEncoder)
        }
    else:
        response = {
            "statusCode": 201,
            "body": "Data not Found, Empty dynamodb!!..."
        }

    return response

