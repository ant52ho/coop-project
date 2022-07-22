import os

#os.system('killall wpa_supplicant')
os.system('sudo ifconfig wlan0 down')
#os.system('sudo iwconfig wlan0 channel 4') it's fine, everything channel 1
os.system('sudo iwconfig wlan0 mode ad-hoc')
os.system("sudo iwconfig wlan0 essid 'AHTest'")
os.system('sudo ifconfig wlan0 10.0.1.1')