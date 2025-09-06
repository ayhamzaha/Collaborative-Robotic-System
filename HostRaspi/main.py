# File Responsibilities: derive coordinates from a picture, derive robotic arm movements and feasibility, maintenance for cyclic system  
import ble
import cam
import nlp
import asyncio
import robot_coords
import numpy as np
from enum import Enum
import time

ESP32_ARM_1 = "14:2B:2F:C6:5B:52"
ESP32_ARM_2 = "14:2B:2F:C6:64:4E"




class Color(Enum):
	Green = 0
	Red = 1
	Blue = 2
	Gray = 3
	Other = 4
	def __str__(self):
		return self.name


async def transfer_arm1(px_x, px_y):
	pos_a_matrix = np.array([72,172,272,72,172,272,72,172,272,72,172,272]).reshape(-1,1)
	pos_b_matrix = np.array([-200,-200,-200,-100,-100,-100,0,0,0,100,100,100]).reshape(-1,1)

	pix_p_matrix = np.hstack((np.array([329,214,98,325,208,93,320,206,88,318,203,86]).reshape(-1, 1),np.ones((12, 1)) ))
	pix_q_matrix = np.hstack((np.array([21,16,10,141,133,129,257,252,246,374,368,364]).reshape(-1, 1),np.ones((12, 1))))
	x_coeffs = np.linalg.pinv(pix_p_matrix.T @ pix_p_matrix) @ (pix_p_matrix.T @ pos_a_matrix)

	y_coeffs = np.linalg.pinv(pix_q_matrix.T @ pix_q_matrix) @ (pix_q_matrix.T @ pos_b_matrix)

	x = x_coeffs[0] * px_x + x_coeffs[1]
	y = y_coeffs[0] * px_y + y_coeffs[1]
	return x+10,y+15


async def transfer_arm2(px_x, px_y):
	pos_a_matrix = np.array([100,150,200,250,300,100,150,200,250,300,100,150,200,250,300]).reshape(-1,1)
	pos_b_matrix = np.array([150,150,150,150,150,0,0,0,0,0,-150,-150,-150,-150,-150]).reshape(-1,1)

	pix_p_matrix = np.hstack((np.array([54,114,175,238,302,51,112,172,233,298,31,96,162,224,293]).reshape(-1, 1),np.ones((15, 1)) ))
	pix_q_matrix = np.hstack(( np.array([56,61,64,65,65,236,240,245,249,250,432,431,436,437,438]).reshape(-1, 1),np.ones((15, 1))))

	x_coeffs = np.linalg.pinv(pix_p_matrix.T @ pix_p_matrix) @ (pix_p_matrix.T @ pos_a_matrix)

	y_coeffs = np.linalg.pinv(pix_q_matrix.T @ pix_q_matrix) @ (pix_q_matrix.T @ pos_b_matrix)

	x = x_coeffs[0] * px_x + x_coeffs[1]
	y = y_coeffs[0] * px_y + y_coeffs[1]
	return x-10,y+10



# Action 1: Pick up an object
async def pickUp(cap,color,arm ):
	print("Taking an image of workspace...")
	objects = await cam.capture(cap)
	if objects[0][0] == -1:
		print("No object was found!")
		return 0
	if arm == "x":
		move_arm = int(input("Which arm would you like to use (1 or 2): "))
	else:
		if arm == "one":
			move_arm = 1
		else:
			move_arm = 2
	pos_objects = []
	# If both parameters are specified the system should search for an exact match
	# If only one parameter is specified the system should display all objects with this parameter and ask user to select object
	# If no parameter is specified the system should display all objects and ask user to select object
	# If more than one exact match is present ask user which to grab   
	for i,obj in enumerate(objects):
		if move_arm == 1:
			x,y = await transfer_arm1(obj[0], obj[1])
		else:
			x,y = await transfer_arm2(obj[0], obj[1])
		coords, flag = await robot_coords.Ailink6dofelephant(x,y,124,np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]]))
		if flag:
			continue
		if color == "x":
			#print(f"{i}\t({obj[0]},{obj[1]})\t{Color(obj[2]).name}")
			pos_objects.append(i)
		elif color.lower() == Color(obj[2]).name.lower():
			#print(f"{i}\t({obj[0]},{obj[1]})\t{Color(obj[2]).name}")
			pos_objects.append(i)

	if len(pos_objects) <= 0:
		print("No valid object detected")
		return 0
	elif len(pos_objects) == 1:
		print("Only one valid object detected")
		choice = pos_objects[0]
	else:
		print("Possible Objects:\nIndex\t(X,Y)\t\tColor")
		for i,obj in enumerate(pos_objects):
				print(f"{i}\t({objects[obj][0]},{objects[obj][1]})\t{Color(objects[obj][2]).name}")
		choice = int(input("Enter the index of the object you would like to pick up: "))
	if move_arm == 1:
		x,y = await transfer_arm1(objects[choice][0], objects[choice][1])
		print(f"Object {choice} selected at {x},{y}mm!")
		client = ESP32_ARM_1
		coords, flag = await robot_coords.Ailink6dofelephant(x,y,120,np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]]))
	else:
		x,y = await transfer_arm2(objects[choice][0], objects[choice][1])
		print(f"Object {choice} selected {x} and {y}mm!")
		client = ESP32_ARM_2
		coords, flag = await robot_coords.Ailink6dofelephant(x,y,120,np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]]))
	if flag:
		print("Object not in range")
		return 0
	print("Sending coordinates to arm!")
	await ble.send_data(client, np.degrees(coords))	
	return 1

async def main():
	# System initialization
	cap = await cam.camera_init()
	action_queue = []
	color_queue = []
	arm_queue = []

	if cap is None:
		print(f'Camera error: {cap}')
		return 0
	while True:
		if len(action_queue) > 0:
			# do action queue here
			for index,action in enumerate(action_queue):
				print(f"{len(action_queue)} actions queued")
				if action == 'p':
					if await pickUp(cap,color_queue[index],arm_queue[index]):
						time.sleep(31)
						print("Object picked up successfully")
					else:
						print("Failed to pick up object")
				action_queue.pop(index)
				color_queue.pop(index)
				arm_queue.pop(index)
			continue
		else:
			choice = int(input("1 - Send BLE data\n2 - Pick Up Object\n3 - Use voice input\n9 - Exit\n"))
		if choice == 1:
			data = input("What data would you like to send: ")
			await ble.send_data(ESP32_ARM_1, data)
			continue
		elif choice == 2:
			color_queue.append("x")
			arm_queue.append("x")
			result = await pickUp(cap,"x","x")
			color_queue.pop()
			arm_queue.pop()
		elif choice == 3:
			nlp.record_audio()
			transcribed_text = nlp.transcribe_audio()
			print(f"You said: \"{transcribed_text}\"")
			i = 0
			while i < len(transcribed_text):
					# Check the action
					if transcribed_text[i] == "pick" and i+1 < len(transcribed_text):
							if transcribed_text[i+1] == "up":
									print("Pick up action triggered!")
									action_queue.append("p")
									i += 2
									arm_queue.append("x")
									color_queue.append("x")
									while i+1 < len(transcribed_text):
											print(transcribed_text[i])
											if transcribed_text[i] == "then" or transcribed_text[i] == None:
													break
											elif transcribed_text[i] == "robot":
													if transcribed_text[i+1] == "one" or transcribed_text[i+1] == "two" or transcribed_text[i+1] == "too" or transcribed_text[i+1] == "to":
															print(f"choosing arm, {transcribed_text[i+1]}")
															arm_queue.pop()
															arm_queue.append(transcribed_text[i+1])
															i += 2
															continue
													i+=1
													continue
											elif transcribed_text[i] == "color":
													if transcribed_text[i+1] == "red" or transcribed_text[i+1] == "green" or transcribed_text[i+1] == "blue":
															print(f"choosing color, {transcribed_text[i+1]}")
															color_queue.pop()
															color_queue.append(transcribed_text[i+1])
															i += 2
															continue
													i+=1
													continue                    
											else:
													i+=1
											continue
					i += 1


			k = 0
			print("while loop starting...") 
			while k < len(action_queue):
					print(f"index: {k} | color: {color_queue[k]} | arm: {arm_queue[k]} | action: {action_queue[k]}")
					k += 1
			if len(action_queue) <= 0:
				print("No actions detected!")
			continue
		elif choice == 9:
			print("Goodbye!")
			break
		else:
			print("Invalid selection!")
			continue
asyncio.run(main())
