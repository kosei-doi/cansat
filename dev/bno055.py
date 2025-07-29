import time
import board
import busio
import adafruit_bno055

# I2C初期化
i2c = busio.I2C(board.SCL, board.SDA)

# センサ初期化
sensor = adafruit_bno055.BNO055_I2C(i2c)

# センサからデータ取得
while True:
    print("温度: {} ℃".format(sensor.temperature))
    print("加速度: {}".format(sensor.acceleration))
    print("角速度: {}".format(sensor.gyro))
    print("地磁気: {}".format(sensor.magnetic))
    print("オイラー角: {}".format(sensor.euler))  # (heading, roll, pitch)
    print("クォータニオン: {}".format(sensor.quaternion))
    print()
    time.sleep(1)
