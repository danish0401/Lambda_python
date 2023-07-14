import json
import boto3
import os

from lambdas import decimalencoder

def handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
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
            "body": "Data not Found in dynamodb!!..."
        }

    return response

