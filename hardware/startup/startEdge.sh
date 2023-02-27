# exiting existing processes
sudo killall redis-server
# kill $(lsof -t -i:5000)

sudo redis-server ~/coop-project/hardware/redisFiles/redisTest.conf &
sudo python ~/coop-project/hardware/scripts/serverScript2.py