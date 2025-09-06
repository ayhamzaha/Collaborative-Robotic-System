# File Responsibilities: connect to ESP32 server, send data to ESP32, receive data from ESP32
from bleak import BleakClient
import bleak

# set ESP32 characteristic ID
CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"


# allows RPi to connect to ESP32
async def connect(address):
	client = BleakClient(address)
	try:
		await client.connect()
	#	for service in client.services:
	#		for characteristic in service.characteristics:
	#			print(f"{characteristic.properties}, uuid: {characteristic.uuid}")
		if client.is_connected:
			print("Connected to ESP32!")
			return client
	except Exception as e:
		print(f'Failed to connect: {e}')
		return None

# allows RPi to disconnect from ESP32
async def disconnect(client):
	print("disconnecting...")
	try:
		await client.disconnect()
	except Exception as e:
		print(f'Failed to disconnect: {e}')


# allows connected RPi to send data to ESP32
async def send_data(address, data):
	#print(f'sending:{data}')
	data_str = ",".join(map(str, data))
	print(f"data = {data_str}")
	client = await connect(address)
	await client.write_gatt_char(CHAR_UUID, data_str.encode("utf-8"), response=True)
	test = await client.read_gatt_char(CHAR_UUID)
	print(test)
	await disconnect(client)
# allows connected RPi to receive data from ESP32
def callback(sender: str,data: bytearray):
	print(f"{sender}: {data}")
