import serial
import pynmea2

ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)

while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith('$GPGGA'):
            msg = pynmea2.parse(line)
            print("緯度:", msg.latitude)
            print("経度:", msg.longitude)
            print("高度:", msg.altitude, msg.altitude_units)
            print("---")
    except pynmea2.ParseError:
        continue
