#!/bin/bash

# Start Emulator: TEMP-SENSOR
echo "Starting Emulator: TEMP-SENSOR"
python3 emulator.py TEMP-SENSOR Celsius Room_1 7 &
sleep 3

# Start Emulator: ELECTRICITY-SENSOR
echo "Starting Emulator: ELECTRICITY-SENSOR"
python3 emulator.py ELECTRICITY-SENSOR kWh Room_1 11 &
sleep 3

#Start Emulator: RACK-SENSOR
echo "Starting Emulator: RACK-SENSOR"
python3 emulator.py RACK-SENSOR Celsius rRoom_1 6 &
sleep 3

# Start Emulator: WATER-SENSOR
echo "Starting Emulator: WATER-SENSOR"
python3 emulator.py WATER-SENSOR m3 Room_1 13 &
sleep 3


echo "Starting Notification Service"
python3 notification_service.py &


# Start Smart Home Manager
echo "Starting Smart DC-Safe Manager"
python3 manager.py &
sleep 10

# Start System GUI
echo "Starting System GUI"
python3 gui.py
