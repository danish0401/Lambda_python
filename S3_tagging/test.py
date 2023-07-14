import json
import boto3
import pprint
import calendar
import datetime
import csv
import smtplib
import os
import re

def get_first_sundays_of_months_in_year():
    first_sundays_of_month=[]
    year = datetime.datetime.now().year
    # print(year)
    for i in range(1,10): 
        month = calendar.monthcalendar(year, i)
        first_sunday = min(month[0][calendar.SUNDAY], month[1][calendar.SUNDAY])        
        first_sunday_of_month = str(year)+"0"+str(i)+"0"+str(first_sunday)
        first_sundays_of_month.append(first_sunday_of_month)
    for i in range(10,13): 
        month = calendar.monthcalendar(year, i)        
        first_sunday = min(month[0][calendar.SUNDAY], month[1][calendar.SUNDAY])        
        first_sunday_of_month = str(year)+str(i)+"0"+str(first_sunday)
        first_sundays_of_month.append(first_sunday_of_month)
    return first_sundays_of_month

def get_first_sundays_of_months_all_year():
    first_sundays_of_month_in_all_year=[]
    year = datetime.datetime.now().year
    for year_iter in range(year-3,year):
        for i in range(1,10): 
            month = calendar.monthcalendar(year_iter, i)
            # print(month)
            first_sunday = min(month[0][calendar.SUNDAY], month[1][calendar.SUNDAY])
            first_sunday_of_month = str(year_iter)+"0"+str(i)+"0"+str(first_sunday)
            first_sundays_of_month_in_all_year.append(first_sunday_of_month)
        for i in range(10,13): 
            month = calendar.monthcalendar(year_iter, i)        
            first_sunday = min(month[0][calendar.SUNDAY], month[1][calendar.SUNDAY])
            first_sunday_of_month = str(year_iter)+str(i)+"0"+str(first_sunday)
            first_sundays_of_month_in_all_year.append(first_sunday_of_month)
    return first_sundays_of_month_in_all_year

import datetime

def get_last_day_of_each_month():
    last_day_of_months=[]
    year = datetime.datetime.now().year
    # print(year)
    
    for i in range(1,10): 
        month = calendar.monthcalendar(year, i)
        last_day = max(month[-1])        
        last_day_of_month = str(year)+"0"+str(i)+str(last_day)
        last_day_of_months.append(last_day_of_month)
    for i in range(10,13): 
        month = calendar.monthcalendar(year, i)        
        last_day = max(month[-1])        
        last_day_of_month = str(year)+str(i)+str(last_day)
        last_day_of_months.append(last_day_of_month)
    return last_day_of_months

def get_last_day_of_each_month_in_all_years():
    last_day_of_months=[]
    year = datetime.datetime.now().year
    # print(year)
    for year_iter in range(year-3,year+1):
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

def get_first_day_of_first_month_in_all_years():
    first_day_of_months=[]
    year = datetime.datetime.now().year
    # print(year)
    for year_iter in range(year-3,year+1):
        first_day_of_month = str(year_iter)+"0101"
        first_day_of_months.append(first_day_of_month)
    return first_day_of_months
# # Example usage
# last_days = get_last_day_of_each_month(2023)
# for day in enumerate(last_days):
#     print(day)


last_day=get_first_sundays_of_months_all_year()
# print(last_day)
# nenene=[last_day[0],last_day[12],last_day[24]]
# print(last_day)
# print(calendar.monthcalendar(2023, 1)[0])


# string = "PAM-M2SQLR3$M2SQLAG1_M2_FULL_20220101_02311311.bak"
# regex = r'^([^_]+)'

# match = re.search(regex, string)
# if match and '/FULL/' in string:
#     result = match.group(1)
#     print(result)

# prefix="Prod/PAM-M2SQL-04/"
# print(prefix[5:])
date_key="20221218"
date_from_object = datetime.datetime.strptime(date_key, '%Y%m%d')
time_between_last_modified = datetime.datetime.now() - date_from_object
print(time_between_last_modified.days)