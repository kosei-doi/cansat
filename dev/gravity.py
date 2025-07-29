import serial

# /dev/serial0 または /dev/ttyS0
ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

while True:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
        print(line)
