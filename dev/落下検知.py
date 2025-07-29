import time
import math
from Adafruit_BNO055 import BNO055
import board
import busio
import adafruit_bme280

# センサ初期化
bno = BNO055.BNO055()
if not bno.begin():
    raise RuntimeError('BNO055 初期化失敗')

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.sea_level_pressure = 1013.25  # 必要に応じて調整

initial_altitude = bme280.altitude

landed = False
stable_start_time = None

print("着地判定開始")

while not landed:
    ax, ay, az = bno.read_linear_acceleration()
    total_acc = math.sqrt(ax**2 + ay**2 + az**2)
    altitude = bme280.altitude
    delta_altitude = abs(altitude - initial_altitude)

    # 加速度が0.3G未満かつ高度変化0.5m未満なら安定状態とみなす
    if total_acc < 0.3 and delta_altitude < 0.5:
        if stable_start_time is None:
            stable_start_time = time.time()
        elif time.time() - stable_start_time >= 1.0:  # 1秒間継続
            landed = True
    else:
        stable_start_time = None

    time.sleep(0.1)

print(f"💥 着地判定完了！ 加速度={total_acc:.2f}G 高度変化={delta_altitude:.2f}m")
