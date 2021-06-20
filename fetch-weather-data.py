
import argparse
import requests
import datetime as dt
import base64
import json
import csv
import pandas as pd
import time


parser = argparse.ArgumentParser(description='Fetch aWhere weather data')
parser.add_argument(
    '-k', '--key', help='API Key', required=True)
parser.add_argument(
    '-s', '--secret', help='API Secret', required=True)
parser.add_argument(
    '-i', '--input',
    help='Filename with path of coordinate data',
    required=True)


def request(**kwargs):
    try:
        response = requests.post(**kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)


def get_weather(key, secret, input):

    today = dt.date.today()
    yearago = dt.timedelta(days=365)

    def selected_dates(today, yearago):
        startyear = (today - yearago).year
        startmonth = (today - yearago).month
        endyear = today.year
        endmonth = today.month

        list = [dt.datetime(m // 12, m % 12 + 1, 1) for m in
                range(startyear * 12 + startmonth, endyear * 12 + endmonth)]
        dates = [d.strftime('%Y-%m-%d') for d in list]
        start_date = dates[0]
        end_date = dates[-1]
        return (start_date, end_date)

    API_ROOT = 'https://api.awhere.com'
    AUTH_ENDPOINT = API_ROOT + '/oauth/token'

    credentials = '{}:{}'.format(key, secret)
    hashed_cred = base64.b64encode(credentials.encode('ascii')).decode('ascii')

    AUTH_DATA = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + hashed_cred
    }
    REQUEST_BODY = 'grant_type=client_credentials'

    print("Requesting auth token...")
    payload = request(url=AUTH_ENDPOINT, headers=AUTH_DATA, data=REQUEST_BODY)
    time.sleep(3)
    access_token = json.loads(payload.text)
    token = access_token.get('access_token')

    print("Pulling weather data...")
    start_date, end_date = selected_dates(today, yearago)
    df_input = pd.read_csv(input)
    weather = []

    for index, row in df_input.iterrows():
        REPORTING_ENDPOINT = API_ROOT + '/v2/weather/locations/{},{}/observations/{},{}'.format(row['gps_lat'], row['gps_long'], start_date, end_date)
        r = requests.get(url=REPORTING_ENDPOINT, headers={'Authorization': 'Bearer {}'.format(token)}).json()
        weather.append(r)

    x = weather[0]
    f = csv.writer(open("weather_observations.csv", "w", newline=''))
    f.writerow(["date", "latitude", "longitude"
               , "maxTemp", "minTemp", "tempUnits"
               , "precipAmount", "precipUnits"
               , "solarAmount", "solarUnits"
               , "maxRelHumidity", "minRelHumidity"
               , "windMorningMax", "windDayMax",  "windAvg", "windUnits"])

    for x in x["observations"]:
        for row in x:
            if x["date"][-2:] == '01':
                f.writerow([
                            x["date"]
                            , x["location"]["latitude"]
                            , x["location"]["longitude"]
                            , x["temperatures"]["max"]
                            , x["temperatures"]["min"]
                            , x["temperatures"]["units"]
                            , x["precipitation"]["amount"]
                            , x["precipitation"]["units"]
                            , x["solar"]["amount"]
                            , x["solar"]["units"]
                            , x["relativeHumidity"]["max"]
                            , x["relativeHumidity"]["min"]
                            , x["wind"]["morningMax"]
                            , x["wind"]["dayMax"]
                            , x["wind"]["average"]
                            , x["wind"]["units"]
                ])


if __name__ == '__main__':
    args = parser.parse_args()
    get_weather(key=args.key, secret=args.secret, input=args.input)
