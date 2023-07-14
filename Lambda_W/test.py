# from datetime import date, timedelta
# sundays=[]
# def all_sundays(year):
# # January 1st of the given year
#        dt = date(year, 1, 1)
# # First Sunday of the given year       
#        dt += timedelta(days = 6 - dt.weekday())  
#        while dt.year == year:
#           yield dt
#           dt += timedelta(days = 7)
          
# for s in all_sundays(2002):
#    sundays.append(s.strftime("%Y%m%d"))

# print(sundays)

import datetime
import calendar
# last_sundays=[]
# year=2021
# for i in range(1,10): 
#     month = calendar.monthcalendar(year, i)
    
#     last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])
#     m = str(year)+"0"+str(i)+str(last_sunday)
#     last_sundays.append(m)
# for i in range(10,13): 
#     month = calendar.monthcalendar(2022, i)
    
#     last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])
#     m = str(year)+str(i)+str(last_sunday)
#     last_sundays.append(m)

# print(last_sundays)

# last_sundays_of_month_in_all_year=[]
# year = datetime.datetime.now().year
# # year = now.year
# print(year-20)

# for year_iter in range(year-20,year):
#     print(year_iter)
#     for i in range(1,10): 
#         month = calendar.monthcalendar(year_iter, i)
#         last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])
#         last_sunday_of_month = str(year_iter)+"0"+str(i)+str(last_sunday)
#         # print(m)
#         last_sundays_of_month_in_all_year.append(last_sunday_of_month)
#     for i in range(10,13): 
#         month = calendar.monthcalendar(year_iter, i)        
#         last_sunday = max(month[-1][calendar.SUNDAY], month[-2][calendar.SUNDAY])
#         last_sunday_of_month = str(year_iter)+str(i)+str(last_sunday)
#         last_sundays_of_month_in_all_year.append(last_sunday_of_month)
# print(last_sundays_of_month_in_all_year)

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
print(last_sundays_of_month_in_all_year)