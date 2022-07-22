# this program is meant to be run in a linux system, where redis is available
# this program uses the austin_weather.csv file, and stores a bunch of keys
# into the redis database.
# these values should then be extracted from the db for usage.


import time
import datetime
import redis
import os
import threading
# key retention duration in redis
RETENTION = 86400000  # retention in milliseconds


f = open("austin_weather.csv", "r")

# indices of interesting data
dayIndex = 0
tempHighIndex = 1
tempLowIndex = 2
windHighIndex = 15
precipitationIndex = 18


def restartRedis(conf):
    print("server starting...")
    os.system('killall redis-server ' + conf)
    os.system('sudo redis-server ' + conf)


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


def spSendData(entries, r, delay=0):
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
        inputData(select, r)
        time.sleep(delay)
    return True


if __name__ == '__main__':
    os.system('sudo service redis-server stop')

    # initiates the redis server
    redis_thread = threading.Thread(
        target=restartRedis, args=("redisCloud.conf",))
    redis_thread.start()
    time.sleep(3)

    # connects to the redis server
    r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    spSendData(100, r, 0)
