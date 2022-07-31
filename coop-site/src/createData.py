# this program creates some locally faked data.
# since this connects to redis, it is meant to be run in Ubuntu


import redis
import time
import datetime
import redis
import os
import threading

print(redis.__version__)

# key retention duration in redis
RETENTION = 86400000  # retention in milliseconds


f = open("/home/antho/coop-project/hardware/austin_weather.csv", "r")

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
            r.ts().create(newKey, labels={
                "id": data[0], "sensor": commands[commandIndex]})

        r.ts().add(key=newKey, timestamp=unixTime,
                   value=data[commandIndex],
                   retention_msecs=RETENTION,
                   duplicate_policy='last')
    print("stored in redis!")
    return True


def spSendData(entries, idNumber, r, delay, all=False):

    # indices of interesting data
    dayIndex = 0
    tempHighIndex = 1
    tempLowIndex = 2
    windHighIndex = 15
    precipitationIndex = 18

    id = idNumber

    f = open("/home/antho/coop-project/hardware/austin_weather.csv", "r")
    line = f.readline().split(',')
    heading = [str(id), line[dayIndex], line[tempHighIndex], line[tempLowIndex],
               line[windHighIndex], line[precipitationIndex]]
    print(heading)
    count = 0
    while True:

        if count == entries and all == False:
            break

        line = f.readline().split(',')
        # print(line)
        select = [str(id), line[dayIndex], line[tempHighIndex], line[tempLowIndex],
                  line[windHighIndex], line[precipitationIndex]]
        # print(select)
        select = 'f:' + ','.join(select)
        inputData(select, r)
        time.sleep(delay)  # for debugging
        count += 1
    return True


if __name__ == '__main__':
    os.system('sudo service redis-server stop')

    # initiates the redis server
    redis_thread = threading.Thread(
        target=restartRedis, args=("/home/antho/coop-project/coop-site/src/redisTemp.conf",))
    redis_thread.start()
    time.sleep(3)

    # connects to the redis server
    r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    r.flushdb()

    # entires, id, redis, delay, sendAll?
    for id in range(1, 6):
        spSendData(50, id, r, 0)
    print("data created!")
    redis_thread.join()
