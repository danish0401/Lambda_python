import json
import logging
import boto3
import uuid
import os
import re
from lambdasP import decimalencoder

def handler(event, context):
    data = event['body'].copy()

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Danish-python-api-Patient')
    table2 = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    if "Nurse_Id" in data and "Patient_Id" in data and type(data['Nurse_Id'] == str) and type(data['Patient_Id'] == str):                        
        result = table2.get_item(
            Key={
                'id': data['Nurse_Id']
            }
        )
        if "Item" in result:
                            # result dict contains details of Nurse
                            # scan dict contains details of Existing Patients
            scan = table.get_item(
                Key={
                    'id': data['Patient_Id']
                }
            )
            if "Item" in scan:

                no_of_ptnt = int(result['Item']['No_of_ptnt'])
                max=2
                min=0
                
                if no_of_ptnt >= min and no_of_ptnt < max :
        
                    resultupdate = table.update_item(
                        Key={
                            'id': data['Patient_Id']
                        },
                        UpdateExpression='SET Nurse_Assigned= :Nurse_Name, '
                                        'Nurse_Id= :Nurse_Id',
                        ExpressionAttributeValues={
                            ':Nurse_Name': result['Item']['Nurse_Name'],
                            ':Nurse_Id': data['Nurse_Id']
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                    response = {
                        "statusCode": 200,
                        "body": json.dumps(resultupdate['Attributes'], cls=decimalencoder.DecimalEncoder)
                    }
                    
                    new_no_of_ptnt=int(result['Item']['No_of_ptnt']+1)
                    print(new_no_of_ptnt)
                    
                    v = table2.update_item(
                        Key={'id': data['Nurse_Id']},
                        UpdateExpression="SET No_of_ptnt= :s",
                        ExpressionAttributeValues={':s': new_no_of_ptnt },
                        ReturnValues="UPDATED_NEW"
                    )

                else:
                    response = {
                        "statusCode": 203,
                        "body": "can not assign any more patients to this nurse"
                    }
            else:
                response = {
                    "statusCode": 200,
                    "body": "Cant Assign a Nurse to a Patient that doesn't exist please enter valid Patient ID and try again!!.."
                }    
        else:
            response = {
                "statusCode": 200,
                "body": "Cant Assign a Nurse that doesn't exist please enter valid nurse ID and try again!!.."
            }
    else:
        response = {
                "statusCode": 202,
                "body": "Please Review your event body you may have misspelled some parameters orentered them with wrong type:: required are 'Patient_Id'(str), 'Nurse_Id'(str)" 
        }

    return response
