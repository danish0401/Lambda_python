
  

# AWS Lambda functions to add Expiration and Glacier tags on S3 objects 
## PreRequisite:
In S3 bucket "**usw2-padi-dbbackups-weekly**", it contained three folders in **/Prod**
 1. Prod/PAM-M2SQL-04/
 2. Prod/PAM-M2SQLR3$M2SQLAG1/
 3. Prod/PAM-MACOLA-04/
### Requirements: 
Requirements for each folder is given below.
**s3://usw2-padi-dbbackups-weekly/Prod/PAM-M2SQL-04/**
- Expire all the objects after 28 days.

**s3://usw2-padi-dbbackups-weekly/Prod/PAM-M2SQLR3$M2SQLAG1/M2**
- 1st backup of each month is moved to glacier after 31 days and then kept in glacier for 2 years and expired after 740 days
- 1st backup of each year is moved to glacier after 31 days and archived indefinitely with no expiration.

**s3://usw2-padi-dbbackups-weekly/Prod/PAM-M2SQLR3$M2SQLAG1**
- 1st backup of each month moved to glacier after 28 days and expired after 122 days (4 months)
- All other weekly backups on S3 (not first backups of month) can be expired in 62 days (2 months)

**s3://usw2-padi-dbbackups-weekly/Prod/PAM-MACOLA-04/**
- move all month end (last day of month) backups to deep archive after 31 days -- do not expire (this will include all year end backups too)
- expire all other Sunday(s) weekly backups after 2 months (62 days)

***for all remaining objects expiration of all other Sunday(s) weekly backups after 2 months (62 days)***

## Implementation for tagging objects: 
Two lambda functions were deployed to implement the following tasks. one for glacier tags and other for expiration tags. To get the time of object creation Date_Key is used which is obatined from object key in format YYYYMMDD like 20221211.
**1. Prod/PAM-M2SQL-04/**
		- All the objects whose time > 28 days
		- **Tag** -> **PAM_M2SQL_04_EXPIRATION: true**
no condition required to put objects in glacier so only expiration tag is added to the objects of this folder
**2. Prod/PAM-M2SQLR3$M2SQLAG1/**
***In s3-tagging-glacier-function***
for /M2
- if date is in starting date of month and time is more than 31 days 
	-	add tag '**PAM_M2SQLR3_M2SQLAG1_GLACIER:true**'

for other folders within Prod/PAM-M2SQLR3$M2SQLAG1/
- if date is in starting date of month and time is more than 28 days. 
	- add tag '**PAM_M2SQLR3_M2SQLAG1_GLACIER:true**'

***In s3-tagging-expiration-funcion***
for /M2
- if date is not in list_of_yearly_backups(januray) and time is more than 740 days 
	- add tag '**PAM_M2SQLR3_M2SQLAG1_EXPIRATION:true**'
- if date is not stating date of month and time is greater than 62 days 
	- add tag '**PAM_M2SQLR3_M2SQLAG1_EXPIRATION:true**'

for other folders within Prod/PAM-M2SQLR3$M2SQLAG1/
- if date is not in list of yearly backups(januray) and time is more than 122 days
	- add tag '**PAM_M2SQLR3_M2SQLAG1_EXPIRATION:true**'
- if date is not stating date of month and time is greater than 62 days 
	- add tag '**PAM_M2SQLR3_M2SQLAG1_EXPIRATION:true**'

**3. Prod/PAM-MACOLA-04/**
***In s3-tagging-glacier-function***
- if date is in last days of months and time is greater than 31 days: 
	- add tag '**PAM_MACOLA_04_DEEP_ARCHIVE:true**'

***In s3-tagging-expiration-function***
- if date is not in last days of months and time is greater than 62 days 
	-  add tag '**PAM_MACOLA_04_EXPIRATION:true**'

### Lifecycle policies:
As we have total of five different tags which cover all scenarios three tags for expiration and two for Glaciers, 
these tags in key:value pair are

 1. **PAM_M2SQLR3_M2SQLAG1_GLACIER:true**
 2. **PAM_MACOLA_04_DEEP_ARCHIVE:true**
 3. **PAM_M2SQL_04_EXPIRATION: true**
 4. **PAM_M2SQLR3_M2SQLAG1_EXPIRATION:true**
 5. **PAM_MACOLA_04_DEEP_ARCHIVE:true**

So based on these tags and folder prefix we will be filtering objects within the bucket **usw2-padi-dbbackups-weekly**, and than setting "Days after object creation" to 1 will move our objects in different storage classes or expire them.
Note: we don't explicitly need to mention days or time in our policy as all of this is managed in our functions. 
 
1. PAM_M2SQL_04 policy for Expiration:
		-	Added filter to limit the scope of this rule to a single prefix. (Prod/PAM-M2SQL-04/)
		-	Added this tag to filter objects: **PAM_M2SQL_04_EXPIRATION:true**
2. PAM_M2SQLR3_M2SQLAG1 policy for Expiration:
		-	Added filter to limit the scope of this rule to a single prefix. (Prod/PAM-M2SQLR3$M2SQLAG1/)
		-	Added this tag to filter objects: **PAM_M2SQLR3_M2SQLAG1_EXPIRATION:true**
3. PAM_MACOLA_04 policy for Expiration:
		- Added filter to limit the scope of this rule to a single prefix. (Prod/PAM-MACOLA-04/)
		- Added this tag to filter objects: **PAM_MACOLA_04_EXPIRATION:true**
4. PAM_M2SQLR3_M2SQLAG1 policy for moving objects to Glacier: 
		 -	Add filter to limit the scope of this rule to a single prefix. (Prod/PAM-M2SQLR3$M2SQLAG1/)
		 -	Add this tag to filter objects: **PAM_M2SQLR3_M2SQLAG1_GLACIER:true**
5. PAM_MACOLA_04 policy for moving objects to Deep Archive:
		-	Add filter to limit the scope of this rule to a single prefix. (Prod/PAM-MACOLA-04/)
		-	Add this tag to filter objects: **PAM_MACOLA_04_DEEP_ARCHIVE:true**