import json
import logging
import boto3
import uuid
import os
import re

def handler(event, context):
    data = event['body'].copy()

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Danish-python-api-Patient')
    table2 = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    if "P_Name" in data and "P_Disease" in data and "Nurse_Id" in data and "Email" in data and type(data['P_Name'] == str) and type(data['P_Disease'] == str) and type(data['Email'] == str) and type(data['Nurse_Id'] == str):
        valid=re.compile('[A-Za-z]{2,25}( [A-Za-z]{2,25})?')
        email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # print("data", event)
        if(re.fullmatch(valid, data['P_Name']) and re.fullmatch(valid, data['P_Disease']) and re.fullmatch(email, data['Email'])):

            scan = table.scan()
            if not(next((item for item in scan["Items"] if item["Email"] == data['Email'].lower()),None)):
                            
                result = table2.get_item(
                    Key={
                        'id': data['Nurse_Id']
                    }
                )
                if "Item" in result:
                    no_of_ptnt = int(result['Item']['No_of_ptnt'])
                    max=2
                    min=0
                    
                    if no_of_ptnt >= min and no_of_ptnt < max :
                        item = {
                            'id' : str(uuid.uuid1()),
                            'Patient_Name' : data['P_Name'],
                            'Disease' : data['P_Disease'],
                            'Nurse_Assigned' : result['Item']['Nurse_Name'],
                            'Email' : data['Email'],
                            'Nurse_Id' : data['Nurse_Id']
                        }
                        table.put_item(Item=item)

                        new_no_of_ptnt=int(result['Item']['No_of_ptnt']+1)
                        print(new_no_of_ptnt)
                        
                        v = table2.update_item(
                            Key={'id': data['Nurse_Id']},
                            UpdateExpression="SET No_of_ptnt= :s",
                            ExpressionAttributeValues={':s': new_no_of_ptnt },
                            ReturnValues="UPDATED_NEW"
                        )
                        response = {
                            "statusCode": 200,
                            "body": json.dumps(item)
                        }
                    else:
                        response = {
                            "statusCode": 203,
                            "body": "can not assign any more patients to this nurse"
                        }
                else:
                    response = {
                        "statusCode": 200,
                        "body": "Cant Assign a Nurse that doesn't exist please enter valid nurse ID and try again!!.."
                    }
            else:
                response = {
                    "statusCode": 200,
                    "body": "Err:: Seems like email is already in use try again with another email!.."
                }        
        else:
            response = {
                    "statusCode": 201,
                    "body": "Please Enter a Valid Patient Name or Disease Name"
            }
    else:
        response = {
                "statusCode": 202,
                "body": "Please Review your event body you may have misspelled some parameters orentered them with wrong type::, required are 'P_Name'(str), 'P_Disease'(str), 'Nurse_Id'(str), 'Email'(str)" 
        }

    return response
