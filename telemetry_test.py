# Temperature and humidity sensor import.
import Adafruit_DHT
# 
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

import spidev
import time
import os


# Temperature and humidity sensor.
sensor = Adafruit_DHT.DHT22

pin = 4

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature, humidity))
else:
    print("Failed to read")


# Configuration:
CLK = 18
MISO = 23
MOSI = 24
CS = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
# SPI_PORT = 0
# SPI_DEVICE = 0
# mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)

# Main program loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*8
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    # Pause for half a second.
    time.sleep(0.5)


 
# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts
 
# Function to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
def ConvertTemp(data,places):
 
  # ADC Value
  # (approx)  Temp  Volts
  #    0      -50    0.00
  #   78      -25    0.25
  #  155        0    0.50
  #  233       25    0.75
  #  310       50    1.00
  #  465      100    1.50
  #  775      200    2.50
  # 1023      280    3.30
 
  temp = ((data * 330)/float(1023))-50
  temp = round(temp,places)
  return temp
 
# Define sensor channels
light_channel = 0
temp_channel  = 1
 
# Define delay between readings
delay = 5
 
while True:
 
  # Read the light sensor data
  light_level = ReadChannel(light_channel)
  light_volts = ConvertVolts(light_level,2)
 
  # Read the temperature sensor data
  temp_level = ReadChannel(temp_channel)
  temp_volts = ConvertVolts(temp_level,2)
  temp       = ConvertTemp(temp_level,2)
 
  # Print out results
  print "--------------------------------------------"
  print("Light: {} ({}V)".format(light_level,light_volts))
  print("Temp : {} ({}V) {} deg C".format(temp_level,temp_volts,temp))
 
  # Wait before repeating loop
  time.sleep(delay)





