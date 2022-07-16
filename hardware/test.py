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
import redis
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)


def tempStore(r, cmd):
    retval = r.rpush('temp', cmd)
    print(retval)


def emptyTempStore(r):
    while r.exists('temp'):
        print(r.lpop('temp'))
    return True


retval = False  # not connected
if __name__ == '__main__':
    redisEmpty = not r.exists('temp')
    hello = str(input("Connected to cloud?"))
    if hello == 'y':
        retval = True
    else:
        retval = False

    print(redisEmpty)
    for i in range(3):
        msg = 'item' + str(i)
        if not retval:
            tempStore(r, msg)
        if retval and not redisEmpty:
            redisEmpty = emptyTempStore(r)
