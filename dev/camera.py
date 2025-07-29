import cv2
import numpy as np
import time
import RPi.GPIO as GPIO

# --- GPIO設定（モーター制御用） ---
LEFT_MOTOR_FORWARD = 17
RIGHT_MOTOR_FORWARD = 22
LEFT_MOTOR_BACKWARD = 18
RIGHT_MOTOR_BACKWARD = 23

GPIO.setmode(GPIO.BCM)
motor_pins = [LEFT_MOTOR_FORWARD, LEFT_MOTOR_BACKWARD, RIGHT_MOTOR_FORWARD, RIGHT_MOTOR_BACKWARD]
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def move_forward(duration=0.3):
    GPIO.output(LEFT_MOTOR_FORWARD, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_FORWARD, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LEFT_MOTOR_FORWARD, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_FORWARD, GPIO.LOW)

def turn_left(duration=0.2):
    GPIO.output(LEFT_MOTOR_BACKWARD, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_FORWARD, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LEFT_MOTOR_BACKWARD, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_FORWARD, GPIO.LOW)

def turn_right(duration=0.2):
    GPIO.output(LEFT_MOTOR_FORWARD, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_BACKWARD, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LEFT_MOTOR_FORWARD, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_BACKWARD, GPIO.LOW)

# --- 赤いコーン検出 ---
def detect_cone(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area > 500:
            x, y, w, h = cv2.boundingRect(largest)
            cx = x + w // 2
            return cx, area
    return None, 0

# --- メイン処理 ---
def approach_cone():
    FRAME_WIDTH = 640
    CENTER_X = FRAME_WIDTH // 2
    AREA_THRESHOLD = 10000  # 面積がこれ以上なら到達とみなす

    cap = cv2.VideoCapture(0)  # Piカメラ or USBカメラ
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("カメラから映像を取得できませんでした")
                break

            cx, area = detect_cone(frame)

            if area > AREA_THRESHOLD:
                print("コーン到達！")
                break
            elif cx is not None:
                offset = cx - CENTER_X
                print(f"コーン中心: {cx}, 面積: {area}")
                if offset < -50:
                    print("左へ回転")
                    turn_left()
                elif offset > 50:
                    print("右へ回転")
                    turn_right()
                else:
                    print("前進")
                    move_forward()
            else:
                print("コーン未検出、スキャン中...")
                turn_left(0.2)  # その場で回って探す

            time.sleep(0.1)

    finally:
        cap.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()

# --- 実行 ---
if __name__ == "__main__":
    approach_cone()
