import requests
import json
import smbus2
import time
import Adafruit_CharLCD as LCD
import speech_recognition as sr

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDBackpack(address=0x21)
# initialize DHT11
sensor = 11
pin = 4
address = 0x38 #Put your device's address here

def get_weather_API(city):

    HOST = "http://api.openweathermap.org/data/2.5/forecast?q=%s&appid=a78ccdc0fc5acda0566b9a11a356970a&units=metric" % city
    r = requests.get(HOST)
    j = json.loads(r.content)["list"][0]["main"]
    return('Temp=%s\nHumidity=%s' % (j["temp"],j["humidity"]))

def get_weather_DHT():
    i2cbus = smbus2.SMBus(1)
    time.sleep(0.5)

    data = i2cbus.read_i2c_block_data(address,0x71,1)
    if (data[0] | 0x08) == 0:
        print('Initialization error')

    i2cbus.write_i2c_block_data(address,0xac,[0x33,0x00])
    time.sleep(0.1)

    data = i2cbus.read_i2c_block_data(address,0x71,7)

    Traw = ((data[3] & 0xf) << 16) + (data[4] << 8) + data[5]
    temperature = 200*float(Traw)/2**20 - 50

    Hraw = ((data[3] & 0xf0) >> 4) + (data[1] << 12) + (data[2] << 4)
    humidity = 100*float(Hraw)/2**20

    # Un-comment the line below to convert the temperature to Fahrenheit.
    # temperature = temperature * 9/5.0 + 32

    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!
    if humidity is not None and temperature is not None:
        return('Temp={0:0.1f}*\nHumidity={1:0.1f}%'.format(temperature, humidity))
    else:
        return('')

def show_weather_LCD(data):
    # Turn backlight on
    lcd.set_backlight(0)
    # Print a two line message
    lcd.message(data)
    # wait 5 seconds
    time.sleep(5)
    # Turn the screen off
    lcd.clear()
    lcd.set_backlight(1)

# initialize voice recognizer
r = sr.Recognizer()
# listen
with sr.Microphone() as source:                # use the default microphone as the audio source
    r.adjust_for_ambient_noise(source)         # listen for 1 second to calibrate the energy threshold for ambient noise levels
    print("Please speak:")
    audio = r.listen(source)                   # now when we listen, the energy threshold is already set to a good value, and we can reliably catch speech right away
try:
    said_text = r.recognize_google(audio)
    print("You said: %s" % said_text)
    if "weather" in said_text:
        print("[-] Getting weather ...")
        weather_data = get_weather_DHT()
        print("[-] The weather is: %s" % weather_data)
        print("[-] Showing weather on LCD ...")
        show_weather_LCD(weather_data)
except LookupError:                            # speech is unintelligible
    print("Could not understand audio")
