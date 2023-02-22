# This file includes the helper functions that are used
# when connecting and sending to the AWS cloud server

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import projectConf
import time
import json

# setting some constants - are usually cmd line args
ROOT_CA_PATH = "/home/pi/certs/root-CA.crt"
PRIVATE_KEY = "/home/pi/certs/CP_Edge.private.key"
CERT_PATH = "/home/pi/certs/CP_Edge.cert.pem"

# don't change these
ENDPOINT = "a13e7ib2mb92sn-ats.iot.us-east-2.amazonaws.com"
THING_NAME = "SensorData"  # will be displayed under this path in console
# check $aws/things/{thing_name}/shadow/update/accepted
CLIENT_ID = "RaspberryPi"


def customShadowCallback_Update(payload, responseStatus, token):

    # Display status and data from update request
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("moisture: " + str(payloadDict["state"]["reported"]["data"]))
        # print("moisture: " + str(payloadDict["state"]["reported"]["moisture"]))
        # print("temperature: " + str(payloadDict["state"]["reported"]["temp"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")


def customShadowCallback_Delete(payload, responseStatus, token):

    # Display status and data from delete request
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


def connect():
    '''
    Connects to AWS IOT using the parameters specified in awsHelpers.py

    Returns a tuple of 
    (myAwsIotMQTTShadowClient, deviceShadowHandler)
    '''

    # Init AWSIoTMQTTShadowClient
    myAWSIoTMQTTShadowClient = None
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(CLIENT_ID)
    # myAWSIoTMQTTShadowClient.configureEndpoint(ENDPOINT, args.port)
    myAWSIoTMQTTShadowClient.configureEndpoint(ENDPOINT, 8883)
    myAWSIoTMQTTShadowClient.configureCredentials(
        ROOT_CA_PATH, PRIVATE_KEY, CERT_PATH)

    # AWSIoTMQTTShadowClient connection configuration
    myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect to AWS IoT
    myAWSIoTMQTTShadowClient.connect()

    # Create a device shadow handler, use this to update and delete shadow document
    deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(
        THING_NAME, True)

    # Delete current shadow JSON doc
    deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 5)

    return (myAWSIoTMQTTShadowClient, deviceShadowHandler)


def sendAWS(msg, deviceShadowHandler):
    '''
    Sends a specially formatted string to AWS IoT. Either data or status string
    Sends using the configurations returned in awsHelpers.connect

        msg: the message to be sent to aws iot

    Sample strings:
    - f:data:eth:2,1665377260,None,None,None,0.0,None,None,None,None,None,None,None,None
    - f:status:sensor2:status:True
    '''
    res = msg.split(":")
    payload = ""
    if res[1] == 'data':
        payload = {"state": {"reported": {"data": msg,
                                          "status": None}}}
    if res[1] == 'status':
        payload = {"state": {"reported": {"data": None,
                                          "status": msg}}}

    # update shadow
    deviceShadowHandler.shadowUpdate(json.dumps(
        payload), customShadowCallback_Update, 5)
