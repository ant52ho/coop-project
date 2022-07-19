import time
f = open("austin_weather.csv", "r")

# indices of interesting data
dayIndex = 0
tempHighIndex = 1
tempLowIndex = 2
windHighIndex = 15
precipitationIndex = 18


def spprint(text):
    print(text)


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
    sendData(5)
