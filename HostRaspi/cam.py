
# File Responsibilities: initialize and verify camera hardware, take a picture, object recognition
import cv2
import asyncio
from datetime import datetime
import os
import numpy as np

# Define camera image dimensions
width_px = 640
height_px = 640

# Function to determine dominant color
def get_dominant_color(r, g, b):
	total = r + g + b + 1e-6
	r_norm, g_norm, b_norm = r / total, g / total, b / total

	if g_norm > r_norm and g_norm > b_norm:
		return 0 #Green
	elif r_norm > g_norm and r_norm > b_norm:
		return 1 #Red
	elif b_norm > r_norm and b_norm > g_norm:
		return 2 #Blue
	elif abs(r_norm - g_norm) < 0.1 and abs(g_norm - b_norm) < 0.1:
		return 3 #Gray
	else:
		return 4 #Other

max_objects_r = 10
max_objects_c = 3
async def getObjects(image):
	objects = np.empty((max_objects_r,max_objects_c))
	objects[0][0] = -1
	i = 0
	
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Apply thresholding
	_, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

	# Use morphological opening to separate close objects
	kernel = np.ones((5, 5), np.uint8)
	thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

	# Find contours
	contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Split image into R, G, B channels
	b_channel, g_channel, r_channel = cv2.split(image)

	# Process each detected object
	for contour in contours:
		if i >= 10:
			print(f"Max objects ({max_objects_r}) reached!")
			return image, objects
		x, y, w, h = cv2.boundingRect(contour)
		center_x, center_y = x + w // 2, y + h // 2

		# Extract object region from each color channel
		r_avg = np.mean(r_channel[y:y+h, x:x+w])
		g_avg = np.mean(g_channel[y:y+h, x:x+w])
		b_avg = np.mean(b_channel[y:y+h, x:x+w])

		# Determine the dominant color
		color_name = get_dominant_color(r_avg, g_avg, b_avg)

		# Draw the rectangle and center point
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		cv2.circle(image, (center_x, center_y), 5, (255, 0, 0), -1)
		if center_y >= 10:
			objects[i][0] = center_x
			objects[i][1] = center_y
			objects[i][2] = color_name
			#print(f"Object {i} detected at x: {center_x}, y: {center_y} (px) with color: {color_name}!")
			i += 1
	return image, objects[:i+1] if i == 0 else objects[:i]
	

	


async def camera_init():
	cap = cv2.VideoCapture(0)
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, width_px)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height_px)

	if not cap.isOpened():
		print('Could not start camera!')
		return None
	else:
		print("Camera initialized!")
		return cap


async def capture(cap):
	await asyncio.sleep(5)

	 # Check if the capture device is still open, if not, reopen it
	if not cap.isOpened() or cap is None:
		cap = await camera_init()  # Reinitialize the camera

	file_path ="images/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")
	if not os.path.exists("images"):
		os.makedirs("images")

	ret, frame = cap.read()
	if not ret:
		raise Exception("Failed to capture image!")
		return 0
	else:
		frame = frame[91:559,161:515]
		#print("Image shape before detection:", frame.shape)
		# Perform object recognition on the captured frame
		result, objects = await getObjects(frame)
		#print("Result shape:", result.shape)
		#print("Result type:", type(result))
		# Save the annotated image
		s = cv2.imwrite(file_path, result)
		print(f"Annotated image saved to: {file_path}, {s}")
		cap.release()
		return objects
