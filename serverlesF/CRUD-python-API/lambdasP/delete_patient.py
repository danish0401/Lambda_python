import json
import boto3
import os


def handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Danish-python-api-Patient')
    table2 = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    data = event['body'].copy()

    if "id" in data:    
        result = table.get_item(
            Key={
                'id': data['id']
            }
        )
        if "Item" in result:
            result_n = table2.get_item(
                Key={
                    'id': result['Item']['Nurse_Id']
                }
            )
            
            new_no_of_ptnt=int(result_n['Item']['No_of_ptnt']-1)
            print(new_no_of_ptnt)
            
            v = table2.update_item(
                Key={'id': result['Item']['Nurse_Id']},
                UpdateExpression="SET No_of_ptnt= :s",
                ExpressionAttributeValues={':s': new_no_of_ptnt },
                ReturnValues="UPDATED_NEW"
            )

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

