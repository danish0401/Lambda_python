import json
import boto3
import os

from lambdas import decimalencoder

def handler(event, context):
    print(event)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
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

