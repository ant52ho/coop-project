# import
import socket
import string
import redis
# 上集群所以没用redis，用下面这一行
from rediscluster import StrictRedisCluster
import time
import serial
import threading
import binascii
from datetime import datetime
from datetime import timedelta

# 变量
dataGet = []


# redis连接
def connectRedisCluster(redis_conn_list):
    r_conn = StrictRedisCluster(startup_nodes=redis_conn_list, decode_responses=True)
    if not r_conn:
        print("连接redis集群失败")
    else:
        print("连接redis集群成功")
    return r_conn


# 校验
def CheckSum(data):
    return (~(sum(data[:-1])) + 1) & 0xff == data[-1] & 0xff


class UARTdataCollection(threading.Thread):
    def __init__(self, port, baudRate):
        super().__init__()
        self.port = port  # 端口
        self.baudRate = baudRate  # 波特率
        self.is_exit = True
        self.now_time_str = ""  # 当前时刻的时间
        self.storage_value = ""  # 要存储的字符串
        # 后面上了多个采集模块上了，还需要添加一个多线程管理的列表
        # self.threads = []

    def connectDevice(self):
        # 这里面port 还有baudRate都需要修改为上面的初始化对象，这样才能持续添加，自动采集数据。
        # 我设置了数据位默认为8，停止位默认为1，还有校验位默认为无，需要更改的化就需要操作代码了。
        try:
            serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudRate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
        except Exception as e:
            print("---异常---：", e)
            return
        print("成功打开串口，正在接收数据。")
        # 下面是真正的数据接受
        # 发送起始命令
        aa = serial_port.write(bytes.fromhex("11 02 01 00 EC"))
        while not aa and self.is_exit:
            aa = serial_port.write(bytes.fromhex("11 02 01 00 EC"))
            print("发送起始命令失败，正在重新发送！", aa)
            time.sleep(1)
        print("成功发送起始命令")

        # 在数据库中存入两个0数据
        # 若传感器在开机时刻没采到数据，可取0，避免出错
        dt = datetime.now()
        self.now_time_str = dt.strftime('%Y-%m-%d %H-%M-%S')
        self.storage_value = "CO2 0 HCHO 0 humidity 0 temperature 0 PM2.5 0"
        r_conn.hset(self.now_time_str, rec_name, self.storage_value)
        time.sleep(1)
        dt = datetime.now()
        self.now_time_str = dt.strftime('%Y-%m-%d %H-%M-%S')
        self.storage_value = "CO2 0 HCHO 0 humidity 0 temperature 0 PM2.5 0"
        r_conn.hset(self.now_time_str, rec_name, self.storage_value)

        while self.is_exit:
            print("is_exit:", self.is_exit)
            time.sleep(0.9)
            count = serial_port.inWaiting()
            if count:
                print("接收到的数据长度count: ", count)
                data = serial_port.read(count)
                # print("接收到的数据长度data: ", len(data))
                # 检验数据长度和校验码
                if len(data) >= 9 and CheckSum(data):
                    if len(data) == 14:  # 正常
                        print("二氧化碳浓度:", data[3] * 256 + data[4])
                        print("甲醛浓度:", data[5] * 256 + data[6])
                        print("湿度浓度:", data[7] * 256 + data[8])
                        print("温度浓度:", (data[9] * 256 + data[10] - 500) / 10.0)
                        print("PM2.5浓度:", data[11] * 256 + data[12])
                        data_CO2 = data[3] * 256 + data[4]
                        data_HCHO = data[5] * 256 + data[6]
                        data_WET = data[7] * 256 + data[8]
                        data_TEM = (data[9] * 256 + data[10] - 500) / 10.0
                        data_PM = data[11] * 256 + data[12]
                        # 得到时间
                        dt = datetime.now()
                        self.now_time_str = dt.strftime('%Y-%m-%d %H-%M-%S')
                        print(self.now_time_str)
                        # now_time_str = dt.strftime('%y-%m-%d %I-%M-%S')
                        # 得到数据
                        self.storage_value = "CO2 " + str(data_CO2) + " HCHO " + str(data_HCHO) + " humidity " + str(
                            data_WET) + " temperature " + str(data_TEM) + " PM2.5 " + str(data_PM)
                        # storage_value = "CO2 " + str(data_CO2) + " HCHO " + str(data_HCHO) + " humidity " + str(
                        #     data_WET) + " temperature " + str(data_TEM) + " PM2.5 " + str(data_PM)

                        # 存入redis
                        # 设备名 时间 值
                        # r_conn.hset(rec_name, self.now_time_str, self.storage_value)
                        # 时间 设备名 值
                        r_conn.hset(self.now_time_str, rec_name, self.storage_value)
                        # r_conn.expire(self.now_time_str, 30)
                        data = str(binascii.b2a_hex(data))[:]  # 转16进制
                        print(data)
                    else:  # 数据错误 赋给此刻在前一时刻的数据
                        dt = datetime.now()
                        self.now_time_str = dt.strftime('%Y-%m-%d %H-%M-%S')
                        x_time = (dt + timedelta(seconds=-1)).strftime("%Y-%m-%d %H-%M-%S")
                        x_data = r_conn.hmget(x_time, rec_name)
                        x_data = ''.join(x_data)
                        r_conn.hset(self.now_time_str, rec_name, x_data)
                        print("接收到了数据，但是数据长度不正确，已舍弃。")
                else:  # 校验码出错，舍弃数据 赋给此刻在前一时刻的数据
                    dt = datetime.now()
                    self.now_time_str = dt.strftime('%Y-%m-%d %H-%M-%S')
                    # r_conn.hset(rec_name, self.now_time_str, "NULL")
                    x_time = (dt + timedelta(seconds=-1)).strftime("%Y-%m-%d %H-%M-%S")
                    x_data = r_conn.hmget(x_time, rec_name)
                    x_data = ''.join(x_data)
                    print(self.now_time_str)
                    print(x_data)
                    r_conn.hset(self.now_time_str, rec_name, x_data)
                    print("接收到了数据，但是数据校验不正确，已舍弃。")
            else:  # 未收到数据
                dt = datetime.now()
                self.now_time_str = dt.strftime('%Y-%m-%d %H-%M-%S')
                # r_conn.hset(self.now_time_str, rec_name, "NULL  ")
                x_time = (dt + timedelta(seconds=-1)).strftime("%Y-%m-%d %H-%M-%S")
                x_data = r_conn.hmget(x_time, rec_name)
                x_data = ''.join(x_data)
                print(self.now_time_str)
                print(x_data)
                r_conn.hset(self.now_time_str, rec_name, x_data)
                print("未接收到数据！")
        # 关掉端口 删除数据库
        serial_port.close()
        r_conn.delete(rec_name)
        print("这个线程现在要结束啦！")

    def run(self):
        # 由于是主动上送数据，我们只需要开启一个线程接收数据并解析数据，存储到数据库即可
        self.connectDevice()

    def stopDatacollection(self):
        self.is_exit = False

    def myName(self):
        return self.port


if __name__ == '__main__':
    # 连接数据库 redis host 本机地址 port 一般是6379
    # r_pool = redis.ConnectionPool(host='127.0.0.1', port='6379', decode_responses=True)
    # r_conn = redis.Redis(connection_pool=r_pool)
    # 上集群连接数据库
    redis_basis_conn = [{'host': '192.168.1.119', 'port': 8000},
                        {'host': '192.168.1.119', 'port': 8001},
                        {'host': '192.168.1.124', 'port': 8002},
                        {'host': '192.168.1.124', 'port': 8003},
                        {'host': '192.168.1.110', 'port': 8004},
                        {'host': '192.168.1.110', 'port': 8005}]
    r_conn = connectRedisCluster(redis_basis_conn)

    # 创建套接字 socket
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定本地信息 bind （本机地址，端口号）
    tcp_server_socket.bind(("", 7788))
    # 监听请求 10的意思是排队十个
    tcp_server_socket.listen(10)
    # 等待客户端的链接 accept
    connection_socket, client_adder = tcp_server_socket.accept()
    # 进入循环 持续等待指令
    while 1:
        # 接收客户端发送过来的请求
        rec_data = connection_socket.recv(1024)
        # 获得指令
        rec_data_str = rec_data.decode()
        # print(rec_data_str)
        # 分开指令
        rec_data_ls = rec_data_str.split('_')
        # 判断指令的长度
        if len(rec_data_ls) != 4:
            # print("please input right mingling!")
            continue
        # 分解指令
        rec_action = rec_data_ls[0]  # 操作指令
        rec_name = rec_data_ls[1]  # 传感器名称
        rec_protocol = rec_data_ls[2]  # 传感器协议
        rec_port = rec_data_ls[3]  # 端口号
        # # 执行命令
        if rec_action == "add":
            # 判断协议-判断传感器类型
            try:
                # 9600是波特率 存到dataGet中
                dataGet.append(UARTdataCollection(rec_port, 9600))
                for i in dataGet:
                    i.start()
                # 回送信息
                send_data = "Success"
            except Exception as e:
                print("---异常---：", e)
                send_data = "Failed"
        elif rec_action == "delete":
            try:
                for i in dataGet:
                    print(i.myName())
                    if i.myName() == rec_port:
                        # 关掉端口 删除数据库
                        i.stopDatacollection()
                        dataGet.remove(i)
                        break
                send_data = "Success"
            except Exception as e:
                print("---异常---：", e)
                send_data = "Failed"
        else:
            send_data = "指令有误，请重新输入"

        # 回送结果给客户端 成功与否
        connection_socket.send(send_data.encode("utf-8"))

        # 结束
        if rec_data_str == "END":
            for i in dataGet:
                i.stopDatacollection()
            break

    # 关闭套接字
    connection_socket.close()
    tcp_server_socket.close()
