import serial
import time
from pymycobot.mycobot import MyCobot

#
# This code runs on the myCobot280 and is responsible for
# maintenance of the cyclic system. The code also reads 
# data through the serial port and uses it to move the
# arm to the specified coordinates, then using the tactile
# information it determines if an object has been lifted.
#

mc = MyCobot('/dev/ttyAMA0',1000000)
ser = serial.Serial('/dev/ttyUSB0', 115200)

object_grabbed = 0
max_count = 30

def base():
    mc.send_angles([0,0,0,0,0,0],30)


while(True):
	if object_grabbed:
		base()
		time.sleep(5)
		print("moving to drop off object!")
		mc.send_angles([116.23,-0.95,-140.75,51.71,0.0,26.23],30)
		time.sleep(3)
		mc.set_gripper_state(0,30)
		time.sleep(3)
		object_grabbed = 0
		continue
	else:
		print("Waiting for data...")
		base()
		mc.set_gripper_state(0,30)
		try:
			data = ser.readline().decode("utf-8").strip()
			print(f"Data received: {data}")
			if data:
				angles = list(map(float, data.split(',')))
				mc.send_angles(angles,30)
				time.sleep(3)
				mc.set_gripper_state(1,20)
				ser.timeout = 5
				count = 0
				while count < max_count:
					newdata = ser.readline().decode("utf-8").strip()
					if newdata == "True":
						print("Object grabbed!")
						object_grabbed = 1
						break
					elif newdata == "False":
						count += 1
						continue
					elif newdata == '':
						break
					else:
						continue
				if not object_grabbed:
					mc.set_gripper_state(0,20)
				ser.timeout = None
				time.sleep(4)
		except UnicodeDecodeError:
			print("decode error")
		except ValueError:
			print("value error")
		except Exception as e:
			print(f"unexpected error: {e}")
ser.close()
