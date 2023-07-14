import json
import boto3
import os


def handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    data = event['body'].copy()
    if "id" in data:
        result=table.get_item(
            Key={
                'id': data['id']
            }
        )
        if "Item" in result:
            no_of_ptnt = int(result['Item']['No_of_ptnt'])
            max=2
            min=0
            if no_of_ptnt > min and no_of_ptnt <= max :

                response = {
                    "statusCode": 200,
                    "body": "can not delete nurse as it is assigned to some patient"
                }
                
            else:
                table.delete_item(
                    Key={
                        'id': data['id']
                    }
                ) 
                response = {
                    "statusCode": 200,
                    "body": "Deleted successfully"
                }
        else:
            response = {
                "statusCode": 201,
                "body": "No such Item Exist in Database!!.."
            }
    else:
        response = {
                "statusCode": 200,
                "body": "Please Review your event body you may have misspelled some parameters, required are 'id' "        
        }
       
    return response

