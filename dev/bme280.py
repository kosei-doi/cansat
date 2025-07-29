import smbus2
import bme280

# --- BME280のI2Cアドレス（通常は0x76か0x77） ---
BME280_I2C_ADDR = 0x76

# --- SMBusオブジェクト作成（1はRaspberry PiのI2Cバス番号） ---
bus = smbus2.SMBus(1)

# --- 補正データ（キャリブレーション）を読み込む ---
calibration_params = bme280.load_calibration_params(bus, BME280_I2C_ADDR)

# --- センサからデータ取得 ---
data = bme280.sample(bus, BME280_I2C_ADDR, calibration_params)

# --- データ表示 ---
print(f"気温: {data.temperature:.2f} °C")
print(f"湿度: {data.humidity:.2f} %")
print(f"気圧: {data.pressure:.2f} hPa")
