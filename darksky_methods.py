import sys, getopt, requests, json, time, datetime

leap_years = [1904, 1908, 1912, 1916, 1920, 1924, 1928, 1932, 1936, 1940, 1944, 1948, 1952, 1956, 1960, 1964, 1968,
              1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020]

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
    failures=0
    while (failures < tries or True):
        try:
            response = requests.get(url, params)
            return response
        except requests.exceptions.Timeout:
            failures += 1
            print('Darksky api timeout at ',response.headers['Date'],'with a',response.status_code,'and the message:',
                  api_response_or_default_message(response, "You: looks like there's nothing here"))
        except JSONDecodeError:
            failures += 1
            print("return_darksky_response has failed",failures,"times, will try until try limit is reached")
            time.sleep(2)
            continue
    print("Maximum retries reached")

def api_response_or_default_message(response, default_message):
    if response.text is None:
        return default_message
    else:
        return response.text