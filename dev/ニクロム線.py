import RPi.GPIO as GPIO
import time

# リレー制御用GPIOピン番号（BCM番号）
RELAY_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

try:
    print("ニクロム線通電開始")
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # リレーON（ニクロム線通電）
    time.sleep(5)  # 5秒通電（必要に応じて調整）
    GPIO.output(RELAY_PIN, GPIO.LOW)   # リレーOFF（通電停止）
    print("ニクロム線通電停止")
finally:
    GPIO.cleanup()
