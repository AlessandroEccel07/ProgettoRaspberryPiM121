import time
import smbus2
import Adafruit_CharLCD as LCD

address = 0x38 #Put your device's address here

class LCDModule():
 
    def __init__(self):
        # Define LCD column and row size for 16x2 LCD.
        self.address = 0x21
        self.lcd_columns = 16
        self.lcd_rows = 2
        # Initialize the LCD using the pins
        self.lcd = LCD.Adafruit_CharLCDBackpack(address=self.address)
 
    def turn_off(self):
        # Turn backlight off
        self.lcd.set_backlight(1)
 
    def turn_on(self):
        # Turn backlight on
        self.lcd.set_backlight(0)
 
    def clear(self):
        # clear the LCD screen
        self.lcd.clear()
 
    def write_lcd(self,text):
        # turn on LCD
        self.turn_on()
        # wait 0.1 seconds
        time.sleep(0.1)
        # Print a two line message
        self.lcd.message(text)
        # wait 5 seconds
        time.sleep(5)
        # clear screen
        self.clear()
        # wait 0.1 seconds
        time.sleep(0.1)
        # turn off LCD
        self.turn_off()
 
# define LCD module
lcd_screen = LCDModule()
lcd_screen.turn_on()

def get_DHT20():
    i2cbus = smbus2.SMBus(1)
    time.sleep(0.5)
    
    #   Notify DHT20 to start initialization
    data = i2cbus.read_i2c_block_data(address,0x71,1)
    if (data[0] | 0x08) == 0:
        print('Initialization error')

    #   Notify DHT20 of work with using i2c
    i2cbus.write_i2c_block_data(address,0xac,[0x33,0x00])
    time.sleep(0.1)

    #   Getting raw data from DHT20 using i2c
    data = i2cbus.read_i2c_block_data(address,0x71,7)
    
    #   Humidity and temperature are obtained separately from the raw data.
    Traw = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
    Hraw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)

    #   Processing of data in degrees Celsius and percentages
    temperature = 200*float(Traw)/2**20 - 50
    humidity = 100*float(Hraw)/2**20

    return humidity,temperature
 
try:
    while True:
        # lcd_screen.lcd.cursor(cursor = False)
        humi, temp = get_DHT20()
        if temp is not None and humi is not None:
            print("Temperature: %-3.1f C" % temp)
            print("Humidity: %-3.1f C" % humi)
            lcd_screen.write_lcd(text=('Temp = {0:0.2f}*c \nHumd = {1:0.2f}%\n'.format(temp, humi)))
            time.sleep(0.5)
            break
        else:
            continue
 
except KeyboardInterrupt:
    lcd_screen.clear()
    lcd_screen.turn_off()
 