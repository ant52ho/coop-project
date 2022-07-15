'''
Every 3 seconds, generate a variable sized text file that is titled with the current date and time.
Transfer this textfile from the raspberry pi to this computer.
'''
from time import sleep
import os.path
import datetime

absPath = r'C:\Users\antho\Code\coopProject\data'

while (True):
  t = datetime.datetime.now()
  name = t.strftime("%m-%d-%y-%H%M%S")+ ".txt"
  completeName = os.path.join(absPath, name)
  print(completeName)
  f = open(completeName, "w")
  f.write("hello rat " + t.strftime("%m-%d-%y-%X"))
  f.close()
  
  sleep(3)
