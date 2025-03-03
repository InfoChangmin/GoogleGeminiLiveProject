# Thonny에서의 코드
# 라즈베리파이 피코에 main.py
import sys
from time import sleep
from machine import Pin, I2C
from i2c_lcd import I2cLcd


DEFAULT_I2C_ADDR = 0x27


def setup():
    global lcd
    i2c = I2C(0,sda=Pin(0),scl=Pin(1),freq=400000)
    lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)


setup()

while True:
    v = sys.stdin.readline().strip()
    lcd.move_to(0,0)
    lcd.putstr(v)
    time.sleep(0.01)
    lcd.clear()

