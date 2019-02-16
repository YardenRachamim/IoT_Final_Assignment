# Yarden Rachamim 204623284
# Maya Kerem 204818181
# Ori Zilka 312277650

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from datetime import datetime
import thread
import requests

# AWS client configurations:
host = 'a1rpddawph4ysg-ats.iot.eu-west-1.amazonaws.com'
rel_path='../../AWS_CLASS1/'
rootCA =  rel_path + 'HW1/root-CA.crt'
privateKey = rel_path + 'certificates/56075c5af2-private.pem.key'
cert = rel_path + 'certificates/56075c5af2-certificate.pem.crt'
thingName = 'MayaOriYarden-demo'
deviceId = thingName
my_topic = thingName + '/telemetry'
tap_topic = thingName + '/tap'


# Global variables:
# Api url
url = 'https://iot.fernbach.ml'
# Wait interval
interval = 15
# Tap status options
tap_options = {
    0: "off",
    1: "on",
    2 :"rest"
}
# Indicates current tap status(on/off/rest)
tap_status = tap_options[0]
# Indicates when the last time we got indication that tap is on
last_time_on = datetime(1970, 1, 1)
# Max time, in minutes, that tap can be in "on" status
max_time_on = 1
# Time, in seconds, that tap neew to be in "rest" mode 
rest_interval = 60
# Indicates if we need to send turn off command
force_tap_off = False
# Indicates if this is the first time we upload the system
first_time_on = True


# Sensors configuration:
# Configuration for Temperature and humidity sensor:
sensor = Adafruit_DHT.DHT22
pin = 4
# Configuration for light sensor:
CLK = 18
MISO = 23
MOSI = 24
CS = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("--------------\n\n")
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


# Tap on handelling
def tapOnCallback(client, userdata, message):
    global tap_status, last_time_on, force_tap_off
    last_time_on = datetime.now()
    tap_status = tap_options[1]
    tap_data = json.loads(message.payload)
    start_time = datetime.strptime(tap_data['start_time'], '%Y-%m-%dT%H:%M:%SZ')
    time = datetime.strptime(tap_data['time'], '%Y-%m-%dT%H:%M:%SZ')
    # If "max_time_on" minutes pass, raise shut down flag
    force_tap_off = max_time_on < ((time.hour * 60) + time.minute) - ((start_time.hour * 60) + start_time.minute)
    print("--------------\n\n")
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("current global variables status is: \ntap_status={0}\nlast_time_on={1}\nforce_tap_off={2}".format(tap_status, last_time_on, force_tap_off))
    

# Init tap falgs
def init_flags():
     global tap_status, force_tap_off
     print("--------------\n\n")
     print("init_flags()")
     # If we forced to stop, then give tap some rest
     if force_tap_off:
        try:
            thread.start_new_thread(change_force_tap_status, ())
            tap_status = tap_options[2]
            return
        except Exception as e:
            force_tap_off = False
            print("--------------\n\n")
            print("Exception in init_flag() function\nUnable to start new thread!\n" + e)
     tap_status = tap_options[0]


# Change force_tap_off to False, only after "rest_interval" seconds
def change_force_tap_status():
    global force_tap_off, tap_status
    print("--------------\n\n")
    print("tap is now resting for {} seconds".format(rest_interval))
    time.sleep(rest_interval) 
    force_tap_off = False
    tap_status = tap_options[0]
    print("--------------\n\n")
    print("tap is finnished resting, global variables status is: \nforce_tap_off = {0}\ntap_status = {1}".format(force_tap_off, tap_status))


# Send http request to turn tap off
def turn_tap_off():
    payload= {
        'device_id': deviceId,
        'status': "off"
    }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers)
    except Exception as e:
        print("EXception in main loop, during first time on!" + e)


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
# For debug 
myAWSIoTMQTTClient.subscribe(my_topic, 1, customCallback)
# For tap-on handelling
myAWSIoTMQTTClient.subscribe(tap_topic, 1, tapOnCallback)
time.sleep(2)


while True:
    # If first time on. make sure the tap is off! 
    if first_time_on:
        turn_tap_off()
        first_time_on = False
        print("first time on!")
        print("--------------\n\n")
        
    # Temparature and humidity data 
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        print("Failed to read temperature and humidity")

    # Light sensor data 
    light = mcp.read_adc(7)
    print('light sensor data={}'.format(light))

    # Send information to my_topic:
    payload ={
                'temperature': temperature,
				'humidity': humidity,
				'light': light,
                'tap_status': tap_status,
                'shut_down': force_tap_off
            }
    curr_time = datetime.now()
    if tap_status == "on":
        diff = ((curr_time.minute*60) + curr_time.second) - ((last_time_on.minute*60) + last_time_on.second)
        print("Didn't got 'on' indication for: {} seconds".format(diff))
        # If there is more then 30 secondes interval between "on" indication and current time, then the tap is "off"!:
        if diff > 30:
            init_flags()
            
    try:
        myAWSIoTMQTTClient.publish(my_topic,json.dumps(payload), 1)
    except Exception as e:
        print("Exception on main loop, during publish to {}".format(my_topic))
        print(payload)

    # Wait interval
    time.sleep(interval)
