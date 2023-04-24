from machine import Pin
from utime import sleep

print("Hello, Pi Pico!")

led = Pin(5, Pin.OUT)
while True:
  led.toggle()
  print(f"LED: {led.value()}")
  sleep(0.5)
