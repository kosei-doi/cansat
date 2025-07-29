import RPi.GPIO as GPIO
import time

# GPIOピンの定義
IN1_L = 23  # 左モーター TB67H450 の IN1
IN2_L = 24  # 左モーター TB67H450 の IN2
IN1_R = 20  # 右モーター TB67H450 の IN1
IN2_R = 21  # 右モーター TB67H450 の IN2

# 初期化
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1_L, GPIO.OUT)
GPIO.setup(IN2_L, GPIO.OUT)
GPIO.setup(IN1_R, GPIO.OUT)
GPIO.setup(IN2_R, GPIO.OUT)

# 動作関数
def forward():
    GPIO.output(IN1_L, GPIO.HIGH)
    GPIO.output(IN2_L, GPIO.LOW)
    GPIO.output(IN1_R, GPIO.HIGH)
    GPIO.output(IN2_R, GPIO.LOW)

def backward():
    GPIO.output(IN1_L, GPIO.LOW)
    GPIO.output(IN2_L, GPIO.HIGH)
    GPIO.output(IN1_R, GPIO.LOW)
    GPIO.output(IN2_R, GPIO.HIGH)

def turn_left():
    GPIO.output(IN1_L, GPIO.LOW)
    GPIO.output(IN2_L, GPIO.HIGH)
    GPIO.output(IN1_R, GPIO.HIGH)
    GPIO.output(IN2_R, GPIO.LOW)

def turn_right():
    GPIO.output(IN1_L, GPIO.HIGH)
    GPIO.output(IN2_L, GPIO.LOW)
    GPIO.output(IN1_R, GPIO.LOW)
    GPIO.output(IN2_R, GPIO.HIGH)

def stop():
    GPIO.output(IN1_L, GPIO.LOW)
    GPIO.output(IN2_L, GPIO.LOW)
    GPIO.output(IN1_R, GPIO.LOW)
    GPIO.output(IN2_R, GPIO.LOW)

try:
    print("前進")
    forward()
    time.sleep(20)

    print("右旋回")
    turn_right()
    time.sleep(1)

    print("左旋回")
    turn_left()
    time.sleep(1)

    print("後退")
    backward()
    time.sleep(2)

    print("停止")
    stop()

finally:
    GPIO.cleanup()
