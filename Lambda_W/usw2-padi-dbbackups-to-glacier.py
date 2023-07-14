import json
import boto3
import pprint
import calendar
import datetime
import csv
import smtplib
import os
import re

from io import StringIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import b64decode
from dateutil.relativedelta import relativedelta

tag_added_objects_list = []
BUCKET_CONSTANT = 'usw2-padi-dbbackups'

not_glacier_and_two_s3_retention = ["ASPState", "ClubRefresh", "DIR", "eCommerce", "M2ErrorTracker", "M2Report", "Club", "SSISDB"]
glacier_three_month_retention = ["eCommerce200", "eCommerce300", "M2110", "M2200", "M2Log", "M2Security", "M2Email", "M2Setting",
                            "MacolaDataTransfer", "PADIJapan", "ScubaEarth", "DB_Admin"]
not_glacier_and_four_s3_retention = ["M2Image"]
glacier_yearly_retention = ["M2"]

def lambda_handler(event, context):
    # TODO implement
    get_list_objects()
    object_tag_csv_columns = ['Key','Tag']
    object_tag_csv_buffer = StringIO() 
    instance_patches_writer = csv.DictWriter(object_tag_csv_buffer, fieldnames=object_tag_csv_columns)
    instance_patches_writer.writeheader()
    get_object_tag_csv(instance_patches_writer)
    # send_email(object_tag_csv_buffer)
    
def add_tag(key, tag_key, tag_value):
    print("Key:" + key)
    client = boto3.client('s3')
    response = client.put_object_tagging(
        Bucket=BUCKET_CONSTANT,
        Key=key,
        Tagging={
            'TagSet': [
                {
                    'Key': tag_key,
                    'Value': tag_value
                },
            ]
        }
    )

# def get_all_first_last_three_month_dates():
#     first_date_list_concat = []
#     now = datetime.datetime.now()
#     first_day = datetime.date(now.year, now.month, 1)
#     for month_iter in range(0, 4):
#         monthstr = ''
#         sub_month = first_day + relativedelta(months=-month_iter)
#         if len(str(abs(sub_month.month))) == 1:
#             monthstr = str(0) + str(sub_month.month)
#         else:
#             monthstr = str(sub_month.month)
#         first_date_list_concat.append(str(sub_month.year) + monthstr + '01')
#     return first_date_list_concat

def get_first_month_dates():
    first_date_list_concat = []
    now = datetime.datetime.now()
    year = now.year
    for iter_year in range(year - 2, year + 1):
        for month in range(2, 13):
            first_day = datetime.date(iter_year, month, 1)
            monthstr = ''
            if len(str(abs(month))) == 1:
                monthstr = str(0) + str(month)
            else:
                monthstr = str(month)
            first_date_list_concat.append(str(iter_year) + monthstr + '01')
    return first_date_list_concat
    
# def get_first_year_dates():
#     first_date_list_concat = []
#     now = datetime.datetime.now()
#     year = now.year
#     for iter_year in range(year - 20, year + 1):
#         first_day = datetime.date(iter_year, 1, 1)
#         first_date_list_concat.append(str(iter_year) + '01' + '01')
#     return first_date_list_concat

def get_list_objects():
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket=BUCKET_CONSTANT,
        Prefix='Prod/PAM-M2SQLR3/',
        MaxKeys=20
    )
    next_continuation_token = get_response_information(response)
    
    while next_continuation_token:
        response = client.list_objects_v2(
            Bucket=BUCKET_CONSTANT,
            Prefix='Prod/PAM-M2SQLR3/',
            MaxKeys=20,
            ContinuationToken=next_continuation_token
        )
        next_continuation_token = get_response_information(response)

def get_date_key(key):
    m = re.search("_\d{8}_", key)
    if m:
        concatdate = m.group(0)
        concatdate = concatdate.replace('_', '')
        return concatdate
    else:
        return False

def get_dbname_key(key):
    sub_key = key.split("PAM-M2SQLR3/",1)[1]
    dbname = sub_key.split("/FULL",1)[0]
    return dbname
    
def get_response_information(response):
    for content in response['Contents']:
        check_add_tag(content)
    if "NextContinuationToken" in response and response['NextContinuationToken']:
        next_continuation_token = response['NextContinuationToken']
    else:
        next_continuation_token = ''
    return next_continuation_token

def check_add_tag(content):
    all_first_last_three_date_month_list_concat = get_all_first_last_three_month_dates()
    first_date_month_list_concat = get_first_month_dates()
    first_date_year_list_concat = get_first_year_dates()
    date_key = get_date_key(content['Key'])
    time_between_last_modified = datetime.datetime.now(datetime.timezone.utc) - content['LastModified']
    dbname = get_dbname_key(content['Key'])
    if dbname in glacier_three_month_retention and '/FULL/' in content['Key'] and content['StorageClass'] == 'STANDARD':
        if date_key in all_first_last_three_date_month_list_concat and time_between_last_modified.days > 14:
            add_tag(content['Key'], 'three_month_archived', 'true')
            tag_added_objects_list.append({'Key':content['Key'], 'Tag':'three_month_archived'})  
    if dbname in glacier_yearly_retention and '/FULL/' in content['Key'] and content['StorageClass'] == 'STANDARD':
        if date_key in first_date_month_list_concat and time_between_last_modified.days > 14 and time_between_last_modified.days < 366:
            add_tag(content['Key'], 'monthly_archived', 'true')
            tag_added_objects_list.append({'Key':content['Key'], 'Tag':'monthly_archived'})  
        if date_key in first_date_year_list_concat and time_between_last_modified.days > 14:
            add_tag(content['Key'], 'yearly_archived', 'true')
            tag_added_objects_list.append({'Key':content['Key'], 'Tag':'yearly_archived'})
    
def get_object_tag_csv(writer):
    for data in tag_added_objects_list:
        writer.writerow(data)
    # new lines
    return writer
    
def send_email(object_tag_columns_csv_buffer):
    EMAIL_TO_ADDRESS = os.environ['EMAIL_TO_ADDRESS'].split(',')
    EMAIL_CC_ADDRESS = os.environ['EMAIL_CC_ADDRESS'].split(',')
    EMAIL_USERNAME = os.environ['EMAIL_USERNAME']
    
    ENCRYPTED_PASSWORD = os.environ['EMAIL_PASSWORD']
    # Decrypt code should run once and variables stored outside of the function
    # handler so that these are decrypted once per container
    EMAIL_PASSWORD = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_PASSWORD))['Plaintext']
    EMAIL_PASSWORD = EMAIL_PASSWORD.decode("utf-8")
    MESSAGE = MIMEMultipart('alternative')
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    MESSAGE = MIMEMultipart('alternative')
    
    MESSAGE['subject'] = 'PADI Glacier tag report'
    MESSAGE['To'] = ', '.join(EMAIL_TO_ADDRESS)
    MESSAGE['Cc'] = '%s\n' % ','.join(EMAIL_CC_ADDRESS)
    MESSAGE['From'] = '%s\n' % EMAIL_USERNAME
    
    body = 'Hi,\n\nPlease find attach CSV for PADI tag report.All tagged k are listed in a report\n'
    body = MIMEText(body) # convert the body to a MIME compatible string
    
    object_tag_columns_csv = MIMEText(object_tag_columns_csv_buffer.getvalue())
    object_tag_columns_csv.add_header('Content-Disposition', 'attachment', filename="object_tag.csv")
    
    
    MESSAGE.attach(object_tag_columns_csv)
    
    MESSAGE.attach(body)
    
    server.sendmail(EMAIL_USERNAME, EMAIL_TO_ADDRESS + EMAIL_CC_ADDRESS, MESSAGE.as_string())
    server.quit()