from yeelight import *
from dockerpi import DockerPi
from flask import Flask, render_template, request
app = Flask(__name__)


# Create a dictionary called devicess to store the device idx,  name, and power state
devices = {
   1 : {'name' : 'lamp', 'power' : False}
   }

# Create a dictionary called sensorhub to store the sensor name, value and unit
sensorhub = {
 1 : {'name': 'Room Temperature', 'value': 0, 'unit': 'degree celsius'},
 2 : {'name': 'Brightness', 'value': 0, 'unit': 'lux'},
 3 : {'name': 'Device Temperature', 'value': 0, 'unit': 'degree celsius'},
 4 : {'name': 'Humidity', 'value': 0, 'unit': '%'},
 5 : {'name': 'Barometer Temperature', 'value': 0, 'unit': 'degree celsius'},
 6 : {'name': 'Barometer Pressure', 'value': 0, 'unit': 'pascal'}
}

# discover all connected bulbs on LAN
connected_bulbs, ip2idx = discover_YeelightSmartBulbs(timeout=30)
bulbs = []

# create a list of yeelight bulb object(s)
for i in range(len(ip2idx)):
 host_ip = ip2idx[i+1] # idx 1
 bulbs.append(SmartBulb(host_ip))

#~~~~~~~~~~~~flask~~~~~~~~~~~~~
@app.route("/")
def main():
   # For each device, read the device state and store it in the devices dictionary
   for device in devices:
      #get properties of each device
      properties = bulbs[device -1].get_prop() #will return a dict
      power = properties["power"]
      name = properties["name"]
      devices[device]['power'] = True if power == 'on' else False
      devices[device]['name'] = name

   # For each sensor, read sensor data and store it in the sensor hub dictionary
   sensor = DockerPi(devicebus = 0x1, deviceaddr = 0x17)
   sensorhub[1]['value'] = sensor.getOffChipTemperature()
   sensorhub[2]['value'] = sensor.getOnBoardBrightness()
   sensorhub[3]['value']  = sensor.getOnBoardTemperature()
   sensorhub[4]['value'] = sensor.getOnBoardHumidity()
   sensorhub[5]['value'] = sensor.getBarometerTemperature()
   sensorhub[6]['value'] = sensor.getBarometerPressure()

   # Put the device dictionary into the template data dictionary
   templateData = {
      'devices' : devices,
      'sensorhub': sensorhub,
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the device number and action in it:
@app.route("/<changedevice>/<action>")
def action(changedevice, action):
   # Convert the device from the URL into an integer
   changedevice = int(changedevice)

   # Get the device name for the device being changed
   deviceName = devices[changedevice]['name']

   # If the action part of the URL is "on," execute the code indented below
   if action == "on":
      # Set the device high
      bulbs[changedevice -1].set_power('on')

      # Save the status message to be passed into the template
      message = "Turned the lamp \"" + deviceName + "\" ON."

   if action == "off":
      bulbs[changedevice -1].set_power('off')
      message = "Turned the lamp \"" + deviceName + "\" OFF."

   if action == "toggle":
      # Read the device and set it to whatever it isn't (that is, toggle it)
      bulbs[changedevice -1].toggle()
      message = "Toggled the lamp \"" + deviceName + "\"."

   # For each device, read the device state and store it in the devices dictionary
   for device in devices:
      properties = bulbs[device -1].get_prop() #will return a dict
      power = properties["power"]
      name = properties["name"]
      devices[device]['power'] = True if power == 'on' else False
      devices[device]['name'] = name

   # For each sensor, read sensor data and store it in the sensor hub dictionary
   sensor = DockerPi(devicebus = 0x1, deviceaddr = 0x17)
   sensorhub[1]['value'] = sensor.getOffChipTemperature()
   sensorhub[2]['value'] = sensor.getOnBoardBrightness()
   sensorhub[3]['value']  = sensor.getOnBoardTemperature()
   sensorhub[4]['value'] = sensor.getOnBoardHumidity()
   sensorhub[5]['value'] = sensor.getBarometerTemperature()
   sensorhub[6]['value'] = sensor.getBarometerPressure()

   # Along with the device dictionary, put the message into the template data dictionary
   templateData = {
      'message' : message,
      'devices' : devices,
      'sensorhub': sensorhub
   }

   return render_template('main.html', **templateData)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5001, debug=True)
