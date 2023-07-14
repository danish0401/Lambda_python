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
BUCKET_CONSTANT = 'usw2-padi-dbbackups-weekly-testing'

# list_of_database_names = ["ASPState", "ClubRefresh", "DIR", "eCommerce", "M2ErrorTracker", "M2Report", "Club", "SSISDB","eCommerce200", "eCommerce300", "M2110", "M2200", "M2Log", "M2Security", "M2Email", "M2Setting","MacolaDataTransfer", "PADIJapan", "ScubaEarth", "DB_Admin","M2Image","M2"]
list_of_floders = ["Prod/PAM-M2SQL-04/", "Prod/PAM-M2SQLR3$M2SQLAG1/", "Prod/PAM-MACOLA-04/"]

IS_DRY_RUN = True

if os.getenv('DRY_RUN').lower() =="false":
    IS_DRY_RUN = False

def lambda_handler(event, context):
    # TODO implement
    get_objects_of_each_folder(list_of_floders)
    # get_list_objects()
    object_tag_csv_columns = ['Key','Tag']
    object_tag_csv_buffer = StringIO() 
    instance_patches_writer = csv.DictWriter(object_tag_csv_buffer, fieldnames=object_tag_csv_columns)
    instance_patches_writer.writeheader()
    get_object_tag_csv(instance_patches_writer)
    # send_email(object_tag_csv_buffer)
    
def add_tag(key, tag_key, tag_value):
    print("object: {}, key: {}, value: {}".format(key, tag_key, tag_value))
    client = boto3.client('s3')
    if not IS_DRY_RUN:
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

def is_other_tag(bucket, key, tag_c):
    client = boto3.client('s3')
    other_tag = False
    response = client.get_object_tagging(
        Bucket=bucket,
        Key=key
    )
    tags = response['TagSet']
    for tag in tags:
        if tag['Key'] == tag_c:
            other_tag = True
    return other_tag

def get_last_day_of_each_month_in_all_years():
    last_day_of_months=[]
    year = datetime.datetime.now().year
    # print(year)
    for year_iter in range(year-2,year+1):
        for i in range(1,10): 
            month = calendar.monthcalendar(year_iter, i)
            last_day = max(month[-1])        
            last_day_of_month = str(year_iter)+"0"+str(i)+str(last_day)
            last_day_of_months.append(last_day_of_month)
        for i in range(10,13): 
            month = calendar.monthcalendar(year_iter, i)        
            last_day = max(month[-1])        
            last_day_of_month = str(year_iter)+str(i)+str(last_day)
            last_day_of_months.append(last_day_of_month)
    return last_day_of_months

def get_first_day_of_each_month_in_all_years():
    first_day_of_months=[]
    year = datetime.datetime.now().year
    # print(year)
    for year_iter in range(year-2,year+1):
        for i in range(1,10): 
            first_day_of_month = str(year_iter)+"0"+str(i)+"01"
            first_day_of_months.append(first_day_of_month)
        for i in range(10,13): 
            first_day_of_month = str(year_iter)+str(i)+"01"
            first_day_of_months.append(first_day_of_month)
    return first_day_of_months

def get_first_day_of_first_month_in_all_years():
    first_day_of_months=[]
    year = datetime.datetime.now().year
    # print(year)
    for year_iter in range(year-2,year+1):
        first_day_of_month = str(year_iter)+"0101"
        first_day_of_months.append(first_day_of_month)
    return first_day_of_months
        
        
def get_objects_of_each_folder(list_of_floders):
    for item in list_of_floders:
        get_list_objects(prefix= item)



def get_list_objects(prefix):
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket=BUCKET_CONSTANT,
        Prefix= prefix,
        MaxKeys=20
    )
    next_continuation_token = get_response_information(prefix, response)
    
    while next_continuation_token:
        response = client.list_objects_v2(
            Bucket=BUCKET_CONSTANT,
            Prefix= prefix,
            MaxKeys=20,
            ContinuationToken=next_continuation_token
        )
        next_continuation_token = get_response_information(prefix, response)

def get_date_key(key):
    m = re.search("_\d{8}_", key)
    if m:
        concatdate = m.group(0)
        concatdate = concatdate.replace('_', '')
        return concatdate
    else:
        return False

def get_obj_name_key(prefix,key):
    sub_key = key.split(prefix[5:],1)[1]
    objname = sub_key.split("/FULL",1)[0]
    return objname
    
def get_response_information(prefix, response):
    for content in response['Contents']:
        check_add_tag(prefix, content)
    if "NextContinuationToken" in response and response['NextContinuationToken']:
        next_continuation_token = response['NextContinuationToken']
    else:
        next_continuation_token = ''
    return next_continuation_token

def check_add_tag(prefix, content):
    # last_sundays_of_month_in_this_year = get_last_sundays_of_months_in_year()
    # last_sundays_of_month_in_all_years = get_last_sundays_of_months_all_year()
    date_key = get_date_key(content['Key'])
    # time_between_last_modified = datetime.datetime.now(datetime.timezone.utc) - content['LastModified']
    
    if not date_key is False and '/FULL/' in content['Key']:
        # print("Key:", content['Key'])
        objname = get_obj_name_key(prefix, content['Key'])
        if '/PAM-M2SQL-04/' in content['Key']:
            PAM_M2SQL_04_tagging(objname, date_key, content)
        elif '/PAM-M2SQLR3$M2SQLAG1/' in content['Key']:
            PAM_M2SQLR3_M2SQLAG1_tagging(objname, date_key, content)
        elif '/PAM-MACOLA-04/' in content['Key']:
            PAM_MACOLA_04_tagging(objname, date_key, content)
    
def tag_object(content, tag_value):
    add_tag(content['Key'], tag_value, 'true')
    tag_added_objects_list.append({'Key':content['Key'], 'Tag':tag_value})    

def PAM_M2SQL_04_tagging(objname, date_key, content):
    #convert date string from object name to date time formate
    date_from_object = datetime.datetime.strptime(date_key, '%Y%m%d')
    time_between_last_modified = datetime.datetime.now() - date_from_object
    # Expire all the objects after 28 days.
    if time_between_last_modified.days > 28 and not is_other_tag(BUCKET_CONSTANT, content['Key'], 'PAM_M2SQL_04_EXPIRATION'):
        tag_object(content, 'PAM_M2SQL_04_EXPIRATION')



def PAM_M2SQLR3_M2SQLAG1_tagging(objname, date_key, content):
    # If Database name is M2
    if objname == 'M2':
        # 1st backup of each month is moved to glacier after 31 days 
        # and expired after 740 days
        PAM_M2SQLR3_M2SQLAG1_obj_tag(content, date_key, 31, 740, glacier_tag='PAM_M2SQLR3_M2SQLAG1_M2_GLACIER', experiration_tag='PAM_M2SQLR3_M2SQLAG1_M2_EXPIRATION')
    else: 
        # 1st backup of each month moved to glacier after 28 days and expired after 122 days (4 months)
        PAM_M2SQLR3_M2SQLAG1_obj_tag(content, date_key, 28, 62, glacier_tag='PAM_M2SQLR3_M2SQLAG1_GLACIER', experiration_tag='PAM_M2SQLR3_M2SQLAG1_EXPIRATION')

def PAM_M2SQLR3_M2SQLAG1_obj_tag(content, date_key, short_retention_period, long_retention_period, glacier_tag, experiration_tag):
    first_days_of_all_months_in_year = get_first_day_of_each_month_in_all_years()
    first_day_of_jan_all_year = get_first_day_of_first_month_in_all_years()
    # convert date string from object name to date time formate
    date_from_object = datetime.datetime.strptime(date_key, '%Y%m%d')
    time_between_last_modified = datetime.datetime.now() - date_from_object

    if date_key in first_days_of_all_months_in_year and time_between_last_modified.days > short_retention_period:
        if date_key not in first_day_of_jan_all_year and time_between_last_modified.days > long_retention_period and not is_other_tag(BUCKET_CONSTANT, content['Key'], experiration_tag):
            tag_object(content, experiration_tag)
        elif not is_other_tag(BUCKET_CONSTANT, content['Key'], glacier_tag):
            tag_object(content, glacier_tag)
    # expire all other Sunday(s) weekly backups after 2 months (62 days)
    elif date_key not in first_days_of_all_months_in_year and time_between_last_modified.days > 62 and not is_other_tag(BUCKET_CONSTANT, content['Key'], experiration_tag):
        tag_object(content, experiration_tag)

def PAM_MACOLA_04_tagging(objname, date_key, content):
    last_days_of_all_months_in_year= get_last_day_of_each_month_in_all_years()
    #convert date string from object name to date time formate
    date_from_object = datetime.datetime.strptime(date_key, '%Y%m%d')
    time_between_last_modified = datetime.datetime.now() - date_from_object
    # move all month end (last day of month) backups to deep archive after 31 days 
    # -- do not expire (this will include all year end backups too)
    if date_key in last_days_of_all_months_in_year and time_between_last_modified.days > 31 and not is_other_tag(BUCKET_CONSTANT, content['Key'], 'PAM_MACOLA_04_DEEP_ARCHIVE'):
        tag_object(content, 'PAM_MACOLA_04_DEEP_ARCHIVE')
    # expire all other Sunday(s) weekly backups after 2 months (62 days)
    elif date_key not in last_days_of_all_months_in_year and time_between_last_modified.days > 62 and not is_other_tag(BUCKET_CONSTANT, content['Key'], 'PAM_MACOLA_04_EXPIRATION'):
        tag_object(content, 'PAM_MACOLA_04_EXPIRATION')

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

