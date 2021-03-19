import serial
port = '/dev/ttyUSB0'
baudrate = 9600
max_loop = 50

def open_port(port, baudrate):
    return serial.Serial(
        port=port,
        baudrate=baudrate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=2.0)


def distance_read(ser):
    return int(ser.readline().strip())


def clear_data(ser):
    while ser.inWaiting() > 0:
        ser.read_all()

def clear_data(ser):
    while ser.inWaiting() > 0:
        ser.read_all()


ser = open_port(port, baudrate)
clear_data(ser)

success = False
for _ in range(max_loop):
    dist = distance_read(ser)
    success = dist >= 0

if success:
    print('success')
else:
    print('fail')
