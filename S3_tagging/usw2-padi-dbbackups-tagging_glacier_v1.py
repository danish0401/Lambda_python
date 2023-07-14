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

list_of_folders = ["Prod/PAM-M2SQLR3$M2SQLAG1/", "Prod/PAM-MACOLA-04/"]
S3_CLIENT = boto3.client('s3')
IS_DRY_RUN = True

if os.getenv('DRY_RUN').lower() =="false":
    IS_DRY_RUN = False

def lambda_handler(event, context):
    # TODO implement
    get_objects_of_each_folder(list_of_folders)
    # get_list_of_objects()
    object_tag_csv_columns = ['Key','Tag']
    object_tag_csv_buffer = StringIO() 
    instance_patches_writer = csv.DictWriter(object_tag_csv_buffer, fieldnames=object_tag_csv_columns)
    instance_patches_writer.writeheader()
    get_object_tag_csv(instance_patches_writer)
    # send_email(object_tag_csv_buffer)
    
def add_tag(key, tag_key, tag_value):
    print("object: {}, key: {}, value: {}".format(key, tag_key, tag_value))
    if not IS_DRY_RUN:
        response = S3_CLIENT.put_object_tagging(
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

def tag_objects(content, tag_key):
    add_tag(content['Key'], tag_key, 'true')
    tag_added_objects_list.append({'Key':content['Key'], 'Tag':tag_key})

def get_last_day_of_each_month_in_all_years():
    last_day_of_months=[]
    start_year=2021
    year = datetime.datetime.now().year
    for year_iter in range(start_year,year+1):
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
    start_year=2021
    year = datetime.datetime.now().year
    for year_iter in range(start_year,year+1):
        for i in range(1,10): 
            first_day_of_month = str(year_iter)+"0"+str(i)+"01"
            first_day_of_months.append(first_day_of_month)
        for i in range(10,13): 
            first_day_of_month = str(year_iter)+str(i)+"01"
            first_day_of_months.append(first_day_of_month)
    return first_day_of_months

        
def get_objects_of_each_folder(list_of_folders):
    for item in list_of_folders:
        get_list_of_objects(prefix= item)

def get_list_of_objects(prefix):
    list_object_params = {
        "Bucket": BUCKET_CONSTANT,
        "Prefix": prefix
    }
    
    response = S3_CLIENT.list_objects_v2(**list_object_params)
    is_data_still_pending = True
    
    while is_data_still_pending:
        is_data_still_pending = True if 'NextContinuationToken' in response else False
        
        for content in response['Contents']:
            check_conditions_and_add_tag(prefix, content)
        
        if is_data_still_pending:
            list_object_params["ContinuationToken"] = response['NextContinuationToken']
            response = S3_CLIENT.list_objects_v2(**list_object_params)

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
    
def check_conditions_and_add_tag(prefix, content):
    date_key = get_date_key(content['Key'])
    
    if not date_key is False and '/FULL/' in content['Key']:
        objname = get_obj_name_key(prefix, content['Key'])
        # no glacier policy for /PAM-M2SQL-04/
        if '/PAM-M2SQLR3$M2SQLAG1/' in content['Key']:
            PAM_M2SQLR3_M2SQLAG1_tagging(objname, date_key, content)
        elif '/PAM-MACOLA-04/' in content['Key']:
            PAM_MACOLA_04_tagging( date_key, content)
    

def PAM_M2SQLR3_M2SQLAG1_tagging(objname, date_key, content):
    first_days_of_all_months_in_year = get_first_day_of_each_month_in_all_years()
    # convert date string from object name to date time formate
    date_from_object = datetime.datetime.strptime(date_key, '%Y%m%d')
    time_between_last_modified = datetime.datetime.now() - date_from_object
    # If Database name is M2
    if objname == 'M2':
        # 1st backup of each month is moved to glacier after 31 days 
        if date_key in first_days_of_all_months_in_year and time_between_last_modified.days > 31 and time_between_last_modified.days < 740:
            tag_objects(content, 'PAM_M2SQLR3_M2SQLAG1_GLACIER')
    else: 
        # 1st backup of each month moved to glacier after 28 days
        if date_key in first_days_of_all_months_in_year and time_between_last_modified.days > 28 and time_between_last_modified.days < 122:
            tag_objects(content, 'PAM_M2SQLR3_M2SQLAG1_GLACIER')



def PAM_MACOLA_04_tagging( date_key, content):
    last_days_of_all_months_in_year= get_last_day_of_each_month_in_all_years()
    #convert date string from object name to date time formate
    date_from_object = datetime.datetime.strptime(date_key, '%Y%m%d')
    time_between_last_modified = datetime.datetime.now() - date_from_object
    # move all month end (last day of month) backups to deep archive after 31 days 
    # -- do not expire (this will include all year end backups too)
    if date_key in last_days_of_all_months_in_year and time_between_last_modified.days > 31:
        tag_objects(content, 'PAM_MACOLA_04_DEEP_ARCHIVE')


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
    EMAIL_PASSWORD = boto3.S3_CLIENT('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_PASSWORD))['Plaintext']
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

