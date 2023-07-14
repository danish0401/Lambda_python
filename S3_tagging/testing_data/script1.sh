#!/bin/bash

# Start date and end date
start_date="2020-01-01"
end_date="2022-12-31"

# Iterate over all Sundays between start_date and end_date
date="$start_date"
while [ "$date" != "$end_date" ]; do
  # Check if the current date is a Sunday
  day_of_week=$(date -d "$date" +%u)
  if [ "$day_of_week" -eq 7 ]; then
    # Format the date as YYYYMMDD
    formatted_date=$(date -d "$date" +%Y%m%d)
    # Print the command with the formatted date
    echo "touch Prod/PAM-M2SQLR3\$M2SQLAG1/CLUB/FULL/PAM-M2SQLR3\$M2SQLAG1_CLUB_FULL_${formatted_date}_001320.bak"
  fi
  # Increment the date by 1 day
  date=$(date -d "$date + 1 day" +%F)
done
