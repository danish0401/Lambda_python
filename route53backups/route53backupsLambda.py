import json
import boto3
import os
from datetime import datetime

route53 = boto3.client('route53')
s3 = boto3.client('s3')


zone_names=os.environ["zonenames"]
zone_ids=os.environ["zoneids"]
s3_bucket = os.environ["bucket"]
s3_bucket_folder = os.environ["s3folder"]

def upload_to_s3(filename, s3_bucket):
    key = s3_bucket_folder+'/'+filename.split("/")[-1]+'.json'
    print(key)
    s3.upload_file(filename, s3_bucket, key)

def write_zone_to_json(zone_records, zone_name):
    zone_file_name = '/tmp/' + zone_name +'-'+ datetime.today().strftime('%Y-%m-%d')
    with open(zone_file_name, 'w') as json_file:
        json.dump(zone_records, json_file, indent=4)
    return zone_file_name

def get_resources(zone_id, next_record=None):
    if(next_record):
        response = route53.list_resource_record_sets(
            HostedZoneId=zone_id,
            StartRecordName=next_record[0],
            StartRecordType=next_record[1]
        )
    else:
        response = route53.list_resource_record_sets(HostedZoneId=zone_id)
    res = dict()
    for (key, value) in response.items():
        if key == "ResourceRecordSets":
            res[key] = value
    zone_records = res #['ResourceRecordSets']
    if(response['IsTruncated']):
        zone_records += get_resources(zone_id,(response['NextRecordName'],response['NextRecordType']))
    return zone_records

def lambda_handler(event, context):
    zones_name=zone_names.split(",")
    zones_id=zone_ids.split(",")
    for zone_id,zone_name in zip(zones_id, zones_name):
        zone_records = get_resources(zone_id=zone_id)
        print(zone_records)
        upload_to_s3(write_zone_to_json(zone_records, zone_name=zone_name),s3_bucket)
    return True