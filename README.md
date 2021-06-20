# aWhere-weather-pull
**Objective:** pull the daily observed weather for the first day of the previous 12 months for list of coordinates using the aWhere freemium weather API. 

**Specs:** Python 3.9

**Requirements:** see _requirements.txt_

**Notes:**
In order to run the script:
- Create developer account on aWhere.com
- Download the necessary requirements
- Download _coordinates.csv_
- Run python3 fetch-weather-data.py -k [ENTER_KEY] -s [ENTER_SECRET] -i [FILEPATH/coordinates.csv] in terminal

**Caveat**
aWhere allows for 400 API requests per month with its freemium subscription service. In effort to limit API requests, I chose to use the “start date, end date” endpoint versus the “single date” endpoint. In theory, this would limit API requests to 1x per location (99 total requests) vs. 12x per location (1,188 total requests). However, upon further review, only 10 results are allowed per response call. Thus, it is not mathematically possible to execute this script for all farms with a freemium account. However, given the structure of the current script, with a paid account, it would capture all necessary data. 
