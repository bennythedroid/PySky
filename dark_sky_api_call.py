import sys, getopt, requests, json, time, datetime
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.darksky
api_key = sys.argv[1]
starting_val = sys.argv[2]
num_days = sys.argv[3]
num_years = sys.argv[4]
lat_long = sys.argv[5]
#mongo_collection = sys.argv[6]

leap_years = [1904, 1908, 1912, 1916, 1920, 1924, 1928, 1932, 1936, 1940, 1944, 1948, 1952, 1956, 1960, 1964, 1968,
              1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020]

print("Basic db info: ")
print(db)

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

# url = 'https://api.darksky.net/forecast/{darkskyApiKey}/47.165197,-122.171723,7804800
# ?exclude=daily,flags,currently'


def has_leap_year(timestamp):
    timestamp_to_year = time.strftime('%Y', time.gmtime(int(timestamp)))
    timestamp_to_year_plus1 = int(timestamp_to_year) + 1
    for year in leap_years:
        if year == timestamp_to_year_plus1:
            print("Next window will push into a leap year: " + str(timestamp_to_year_plus1))
            result = True
            return result
    print("No leap year identified")
    result = False
    return result


def set_next_window_start(start_timestamp, format):
    if has_leap_year(start_timestamp):
        year_length = 366
    else:
        year_length = 365
    starting_time = epoch_to_time(format, start_timestamp)
    format_it = datetime.datetime.strptime(starting_time, format)
    format_it += datetime.timedelta(days=year_length)
    return_epoch = time_to_epoch(str(format_it), format)
    return return_epoch

def time_to_epoch(formatted_time, format):
    epoch_to_return = int(time.mktime(time.strptime(formatted_time, format)))
    return epoch_to_return

def epoch_to_time(format, epoch):
    time_to_return = time.strftime(format, time.localtime(epoch))
    return time_to_return

def one_day_later_epoch(epoch, format):
    starting_time = epoch_to_time(format, epoch)
    format_it = datetime.datetime.strptime(starting_time, time_format)
    format_it += datetime.timedelta(days=1)
    return_epoch = time_to_epoch(str(format_it), format)
    return return_epoch

def return_darksky_response(url, params, tries):
    failures = 0
    while (failures < tries or True):
        try:
            response = requests.get(url, params, timeout=(5,10))
            print(response.url)
            return response
        except requests.exceptions.Timeout:
            failures += 1
            print('Darksky api timeout at ', response.headers['Date'], 'with a', response.status_code,
                  'and the message:',
                  api_response_or_default_message(response, "You: looks like there's nothing here"))
        except JSONDecodeError:
            failures += 1
            print("return_darksky_response has failed",failures,"times, will try until try limit is reached")
            time.sleep(2)
            continue

def api_response_or_default_message(response, default_message):
    if response.text is None:
        return default_message
    else:
        return response.text

url = 'https://api.darksky.net/forecast/' + api_key + '/' + lat_long + ',' + starting_val

print("list of vars")
print(api_key)
print(starting_val)
print(num_days)
print(num_years)
print(lat_long)
#print(mongo_collection)



params = {}
params['exclude'] = ('minutely','hourly','daily','alerts','flags')

data = '''{
  "query": {
    "bool": {
      # "must": [
      #   {
      #     "text": {
      #       "record.document": "SOME_JOURNAL"
      #     }
      #   },
      #   {
      #     "text": {
      #       "record.articleTitle": "farmers"
      #     }
      #   }
      # ],
      "must_not": [],
      "should": []
    }
  },
  "from": 0,
  "size": 50,
  "sort": [],
  "facets": {
}'''
time_format = '%Y-%m-%d %H:%M:%S'
one_day_later_global = starting_val
start_of_year = starting_val
entries = db.orting
#v2
for x in range(0, int(num_years)):
    for y in range(0, int(num_days)):
        response = return_darksky_response(url,params,10)
        responseJson = response.json()
        print(responseJson)
        newEntry = {}
        newEntry["date"] = int(starting_val)
        for hourChunk in responseJson["hourly"]["data"]:
            iter_temp = hourChunk["temperature"]
            if 'maxDailyTemp' in newEntry:
                if iter_temp > newEntry["maxDailyTemp"]:
                    newEntry["maxDailyTemp"] = iter_temp
            else:
                newEntry["maxDailyTemp"] = iter_temp
            if 'minDailyTemp' in newEntry:
                if iter_temp < newEntry["minDailyTemp"]:
                    newEntry["minDailyTemp"] = iter_temp
            else:
                newEntry["minDailyTemp"] = iter_temp
        entry_id = entries.insert_one(newEntry).inserted_id
        one_day_later = one_day_later_epoch(int(starting_val), time_format)
        starting_val = one_day_later
        url = 'https://api.darksky.net/forecast/' + api_key + '/' + lat_long + ',' + str(one_day_later)
        print("DAY LOOP Starting time stamp for next day: " + epoch_to_time(time_format, one_day_later))
        #day_count += 1
    starting_val = set_next_window_start(int(start_of_year), time_format)
    start_of_year = starting_val
    print("Starting stamp for next year",starting_val)
    url = 'https://api.darksky.net/forecast/' + api_key + '/' + lat_long + ',' + str(starting_val)
    print("YEAR LOOP Starting time stamp for first day of the next year: " + epoch_to_time(time_format, starting_val))


# "hourly": {
#         "summary": "Mostly cloudy throughout the day.",
#         "icon": "partly-cloudy-day",
#         "data": [
#             {
#                 "time": 7804800,
#                 "summary": "Mostly Cloudy",
#                 "icon": "partly-cloudy-night",
#                 "precipType": "rain",
#                 "temperature": 48.16,
#                 "apparentTemperature": 43.9,
#                 "dewPoint": 37.29,
#                 "humidity": 0.66,
#                 "pressure": 1022,
#                 "windSpeed": 9.6,
#                 "windBearing": 195,
#                 "cloudCover": 0.93,
#                 "visibility": 10
#             },




