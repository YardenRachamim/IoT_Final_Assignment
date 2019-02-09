import Adafruit_DHT
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


# Configuration for Temperature and humidity sensor:
sensor = Adafruit_DHT.DHT22
pin = 4

# Configuration for light sensor:
CLK = 18
MISO = 23
MOSI = 24
CS = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
# SPI_PORT = 0
# SPI_DEVICE = 0
# mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
#print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
# print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
# print('-' * 57)

# Main program loop.
while True:
    # Temparature and humidity data 
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        print("Failed to read temperature and humidity")

    # Light sensor data 
    print('light sensor data={}'.format(mcp.read_adc(7))
    time.sleep(0.5)

    # # Read all the ADC channel values in a list.
    # values = [0]*8
    # for i in range(8):
    #     # The read_adc function will get the value of the specified channel (0-7).
    #     values[i] = mcp.read_adc(i)
    # # Print the ADC values.
    # print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    # # Pause for half a second.
    # time.sleep(0.5)



