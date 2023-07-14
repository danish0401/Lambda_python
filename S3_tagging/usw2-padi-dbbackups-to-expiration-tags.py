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
BUCKET_CONSTANT = 'usw2-padi-dbbackups-testing'

all_dbs = ["ASPState", "ClubRefresh", "DIR", "eCommerce", "M2ErrorTracker", "M2Report", "Club", "SSISDB","eCommerce200", "eCommerce300", "M2110", "M2200", "M2Log", "M2Security", "M2Email", "M2Setting","MacolaDataTransfer", "PADIJapan", "ScubaEarth", "DB_Admin","M2Image","M2"]

def lambda_handler(event, context):
    # TODO implement
    get_list_objects()
    object_tag_csv_columns = ['Key','Tag']
    object_tag_csv_buffer = StringIO() 
    instance_patches_writer = csv.DictWriter(object_tag_csv_buffer, fieldnames=object_tag_csv_columns)
    instance_patches_writer.writeheader()
    get_object_tag_csv(instance_patches_writer)
    # send_email(object_tag_csv_buffer)

#check if the object has expiration tag already attached to it than return false else return true
def is_other_tag(bucket, key):
    client = boto3.client('s3')
    other_tag = False
    response = client.get_object_tagging(
        Bucket=bucket,
        Key=key
    )
    tags = response['TagSet']
    for tag in tags:
        if tag['Key'] == 'expiration':
            other_tag = True
    return other_tag
    
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

def get_last_sundays_of_months_in_year():
    last_sundays_of_month=[]
    year = datetime.datetime.now().year
    for i in range(1,10): 
        month = calendar.monthcalendar(year, i)
        last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])
        last_sunday_of_month = str(year)+"0"+str(i)+str(last_sunday)
        last_sundays_of_month.append(last_sunday_of_month)
    for i in range(10,13): 
        month = calendar.monthcalendar(year, i)        
        last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])
        last_sunday_of_month = str(year)+str(i)+str(last_sunday)
        last_sundays_of_month.append(last_sunday_of_month)
    return last_sundays_of_month

def get_last_sundays_of_months_all_year():
    last_sundays_of_month_in_all_year=[]
    year = datetime.datetime.now().year
    for year_iter in range(year-3,year):
        for i in range(1,10): 
            month = calendar.monthcalendar(year_iter, i)
            last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])
            last_sunday_of_month = str(year_iter)+"0"+str(i)+str(last_sunday)
            last_sundays_of_month_in_all_year.append(last_sunday_of_month)
        for i in range(10,13): 
            month = calendar.monthcalendar(year_iter, i)        
            last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])
            last_sunday_of_month = str(year_iter)+str(i)+str(last_sunday)
            last_sundays_of_month_in_all_year.append(last_sunday_of_month)
    return last_sundays_of_month_in_all_year


def get_list_objects():
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket=BUCKET_CONSTANT,
        Prefix='Prod/PAM-M2SQLR3',
        MaxKeys=20
    )
    next_continuation_token = get_response_information(response)
    
    while next_continuation_token:
        response = client.list_objects_v2(
            Bucket=BUCKET_CONSTANT,
            Prefix='Prod/PAM-M2SQLR3',
            MaxKeys=20,
            ContinuationToken=next_continuation_token
        )
        next_continuation_token = get_response_information(response)

def get_date_key(key):
    m = re.search("_\d{8}_", key)
    if m:
        # print("in if")
        concatdate = m.group(0)
        concatdate = concatdate.replace('_', '')
        return concatdate
    else:
        # print("in else")
        return False
        # return ""
        # return datetime.datetime.now(datetime.timezone.utc)

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

    last_sundays_of_month_in_this_year = get_last_sundays_of_months_in_year()
    last_sundays_of_last_month_in_all_years = get_last_sundays_of_months_all_year()
    date_key = get_date_key(content['Key']) #extract date value from object name
    # print(type(date_key))
    if date_key != False:
        # print("current datetime",datetime.datetime.now())
        date_from_object = datetime.datetime.strptime(date_key, '%Y%m%d')
        time_between_last_modified = datetime.datetime.now() - date_from_object
        

        print("Key:", content['Key'])
        print("last modify",time_between_last_modified)
        dbname = get_dbname_key(content['Key'])
        if('/FULL/' in content['Key'] and content['StorageClass'] == 'STANDARD' and not is_other_tag(BUCKET_CONSTANT, content['Key'])):
            # print(content['Key'])
            if dbname in all_dbs:
                if date_key not in last_sundays_of_month_in_this_year and date_key not in last_sundays_of_last_month_in_all_years and time_between_last_modified.days > 14:
                    add_tag(content['Key'], 'expiration', 'true')
                    tag_added_objects_list.append({'Key':content['Key'], 'Tag':'expiration'})

    
    
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
    
    MESSAGE['subject'] = 'PADI Expiration tag report'
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
