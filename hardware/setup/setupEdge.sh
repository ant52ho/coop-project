# Source: setup.py. Assumes coop-project is pulled

# initial setup for edge server
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install git
sudo apt-get -y install redis
sudo apt-get -y install sqlite3
sudo apt-get -y install bridge-utils
sudo apt-get -y install python3 pip

# pip installs
sudo pip3 install redis
sudo pip3 install AWSIoTPythonSDK

# installing redis
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

# set up staticDHCPd
chmod +x ~/coop-project/hardware/dhcp/install.sh
sudo sh ~/coop-project/hardware/dhcp/install.sh
