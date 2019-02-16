from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json

# Change according to your configuration
host = 'a1rpddawph4ysg-ats.iot.eu-west-1.amazonaws.com'

rel_path='../../AWS_CLASS1/'
rootCA =  rel_path + 'HW1/root-CA.crt'
privateKey = rel_path + 'certificates/56075c5af2-private.pem.key'
cert = rel_path + 'certificates/56075c5af2-certificate.pem.crt'

thingName = 'MayaOriYarden-demo'
deviceId = thingName
topic = thingName + '/telemetryCounter'

isTapOn = False;

# Custom MQTT message callback
def customCallback(client, userdata, message):
    global isTapOn
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    print("isTapOn = " + (str) (isTapOn))
    print("--------------\n\n")


def tapOnCallback():
    global isTapOn
    isTapOn = True




# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.WARNING)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(deviceId)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials(rootCA, privateKey, cert)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)
counter = 0

while True:
    myAWSIoTMQTTClient.publish(topic, json.dumps({'counter': counter}), 1)
    myAWSIoTMQTTClient.subscribe(deviceId + 'telemetryCounterBack', 1, tapOnCallback)
    time.sleep(10)
    counter += 1