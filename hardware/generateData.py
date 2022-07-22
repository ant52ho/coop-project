# this program is meant to be run in a linux system, where redis is available
# this program uses the austin_weather.csv file, and stores a bunch of keys
# into the redis database.
# these values should then be extracted from the db for usage.


import time
import datetime

# key retention duration in redis
RETENTION = 86400000  # retention in milliseconds


f = open("austin_weather.csv", "r")

# indices of interesting data
dayIndex = 0
tempHighIndex = 1
tempLowIndex = 2
windHighIndex = 15
precipitationIndex = 18


def inputData(msg, r):
    data = msg[2:].split(',')
    id = 'sensor' + str(data[0])
    day = data[1]

    unixTime = int(time.mktime(
        datetime.datetime.strptime(day, "%Y-%m-%d").timetuple()))

    commands = ["id", "day", "tempHigh", "tempLow", "wind", "rain"]

    for commandIndex in range(2, len(commands)):
        newKey = id + ":" + commands[commandIndex]
        if not r.exists(newKey):
            r.ts().create(newKey)

        r.ts().add(key=newKey, timestamp=unixTime,
                   value=data[commandIndex], retention_msecs=RETENTION, duplicate_policy='last')
    print("stored in redis!")
    return True


def sendData(entries):
    f = open("austin_weather.csv", "r")
    line = f.readline().split(',')
    heading = [line[dayIndex], line[tempHighIndex], line[tempLowIndex],
               line[windHighIndex], line[precipitationIndex]]
    print(heading)
    for i in range(entries):
        line = f.readline().split(',')
        # print(line)
        select = [line[dayIndex], line[tempHighIndex], line[tempLowIndex],
                  line[windHighIndex], line[precipitationIndex]]
        select = 'f:' + '-'.join(select)
        print(select)
        time.sleep(1)
    return True


if __name__ == '__main__':
