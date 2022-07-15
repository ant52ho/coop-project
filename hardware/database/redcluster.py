# This program connects to an existing redis cluster and is able to write/delete information from the cluster
import logging
import redis
from rediscluster import RedisCluster
import datetime

'''
logging.basicConfig()
logger = logging.getLogger('redis')
logger.setLevel(logging.DEBUG)
logger.propogate = True
'''

# connects the program to redis. Takes in a list of stuff
def connectRedisCluster(redis_conn_list):
  r_conn = redis.RedisCluster(startup_nodes=redis_conn_list)
  if r_conn:
    return r_conn
  else:
    print("failed to connect to redis")


redis_basis_conn = [{'host': '127.0.0.1', 'port': 7000},
                    {'host': '127.0.0.1', 'port': 7001},
                    {'host': '127.0.0.1', 'port': 7002},
                    {'host': '127.0.0.1', 'port': 7003},
                    {'host': '127.0.0.1', 'port': 7004},
                    {'host': '127.0.0.1', 'port': 7005},]

# this line connects the client to the database
r = redis.RedisCluster(startup_nodes=redis_basis_conn, decode_responses=True) #could just be 127.0.0.1, port 7000 or any ip/port combination
rec_name = "127.0.0.1"
dt = datetime.now()
cur_time = dt.strftime('%Y-%m-%d %H-%M-%S')
store_val = "valvalvalval"
r.hset(cur_time, rec_name, store_val)

# hset convention: (hash) time (key) device name (val) data
r.hset('test', 'foo3', 'bar3')


                    

