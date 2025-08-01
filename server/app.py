from flask import Flask, render_template, jsonify, request
import threading
import time
import RPi.GPIO as GPIO
import pigpio
from bme280_utils import read_temp, read_pressure, read_calibration_data
from adafruit_bno055 import BNO055_I2C
import board
import busio
import math
import atexit

app = Flask(__name__)

sensor_data = {
    "acceleration": (0.0, 0.0, 0.0),
    "pressure": 0.0,
    "landing": False
}

# パラメータ設定
GRAVITY = 9.8
ACC_THRESHOLD = 0.5  # ±0.5 m/s²の誤差許容範囲
PRESSURE_DIFF_THRESHOLD = 0.05
CONTINUOUS_COUNT_NEEDED = 10
SAMPLE_INTERVAL = 0.1

# GPIO設定
RELAY_PIN = 26
IN1_L = 24
IN2_L = 23
IN1_R = 20
IN2_R = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

for pin in [IN1_L, IN2_L, IN1_R, IN2_R]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


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
    for pin in [IN1_L, IN2_L, IN1_R, IN2_R]:
        GPIO.output(pin, GPIO.LOW)


def nichrome_power_on(duration=5):
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(RELAY_PIN, GPIO.LOW)


def calc_acc_magnitude(acc_tuple):
    return math.sqrt(sum(x * x for x in acc_tuple))


def sensor_loop(pi, spi_handler, bno, cal_data):
    global sensor_data
    prev_pressure = None
    continuous_count = 0

    while True:
        acc = bno.acceleration or (0.0, 0.0, 0.0)
        acc_mag = calc_acc_magnitude(acc)

        t_fine, temp = read_temp(pi, spi_handler, cal_data)
        pressure = read_pressure(pi, spi_handler, cal_data, t_fine)

        pressure_diff = abs(pressure - prev_pressure) if prev_pressure is not None else 0
        stable_acc = abs(acc_mag - GRAVITY) < ACC_THRESHOLD
        stable_pressure = pressure_diff < PRESSURE_DIFF_THRESHOLD

        if stable_acc and stable_pressure:
            continuous_count += 1
        else:
            continuous_count = 0

        landed = continuous_count >= CONTINUOUS_COUNT_NEEDED

        sensor_data["acceleration"] = acc
        sensor_data["pressure"] = pressure
        # 一度Trueになったら、外部からリセットされるまでTrue維持
        if not sensor_data["landing"]:
            sensor_data["landing"] = landed

        prev_pressure = pressure
        time.sleep(SAMPLE_INTERVAL)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/nichrome')
def nichrome():
    return render_template('nichrome.html')


@app.route('/nichrome/start', methods=['POST'])
def start_nichrome():
    threading.Thread(target=nichrome_power_on).start()
    return jsonify({"result": "ニクロム線通電を開始しました（5秒間）"})


@app.route('/motor')
def motor():
    return render_template('motor.html')


@app.route('/motor/move', methods=['POST'])
def motor_move():
    cmd = request.json.get('command', '')
    if cmd == 'forward':
        forward()
    elif cmd == 'backward':
        backward()
    elif cmd == 'left':
        turn_left()
    elif cmd == 'right':
        turn_right()
    elif cmd == 'stop':
        stop()
    else:
        return jsonify({'result': '不明なコマンド'}), 400
    return jsonify({'result': f'{cmd} 実行しました'})


@app.route('/status')
def status():
    return render_template('status.html')


@app.route('/status/data')
def get_status_data():
    return jsonify(sensor_data)


@app.route('/status/reset', methods=['POST'])
def reset_landing():
    sensor_data["landing"] = False
    return jsonify({"result": "着地判定をリセットしました。"})


@atexit.register
def cleanup():
    GPIO.cleanup()
    if 'pi' in globals():
        pi.stop()


if __name__ == '__main__':
    pi = pigpio.pi()
    if not pi.connected:
        raise Exception("pigpioへの接続に失敗しました")
    spi_handler = pi.spi_open(0, 1_000_000, 0b11)
    cal_data = read_calibration_data(pi, spi_handler)
    i2c = busio.I2C(board.SCL, board.SDA)
    bno = BNO055_I2C(i2c)

    threading.Thread(target=sensor_loop, args=(pi, spi_handler, bno, cal_data), daemon=True).start()

    app.run(host='0.0.0.0', port=5000)
