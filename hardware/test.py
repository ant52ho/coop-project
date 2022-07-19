'''
import redis

r = redis.Redis(host='127.0.0.1', port=6379, password='rat')

cmd = r.config_get("bind")
print(r.config_get("bind"))
bindings = cmd['bind']
if len(bindings.split(' ')) != 3:
    cmd = r.config_set('bind', '127.0.0.1 10.0.0.1 -::1')
    print("successfully changed: ", r.config_get("bind"))


'''
import time
import datetime
day = "2022-12-21"
unixTime = time.mktime(
    datetime.datetime.strptime(day, "%Y-%m-%d").timetuple())

print(int(unixTime))
