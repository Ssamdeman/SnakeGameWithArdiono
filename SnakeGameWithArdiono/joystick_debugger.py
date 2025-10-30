import serial
import time

# Replace with your actual port
SERIAL_PORT = 'COM3'  # Or '/dev/ttyACM0' on Mac/Linux
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Connected to joystick. Listening for input...\n")
    
    while True:
        if ser.in_waiting > 0:
            line = ser.read_until(b'\n').decode('utf-8', errors='ignore').strip()
            if line:
                parts = line.split(',')
                if len(parts) == 3:
                    try:
                        x, y, button = map(int, parts)
                        direction = "none"
                        if x < 400:
                            direction = "left"
                        elif x > 600:
                            direction = "right"
                        if y < 400:
                            direction = "up"
                        elif y > 600:
                            direction = "down"
                        print(f"Raw: {line} | X: {x}, Y: {y}, Button: {button} => Direction: {direction}")
                    except ValueError:
                        print(f"Invalid data: {line}")
                else:
                    print(f"Incomplete data: {line}")
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()