# intended to manage the Smart Home system
# insert data to Smart home DB

import paho.mqtt.client as mqtt
# import os
import time
# import sys, getopt
# import logging
# import queue
import random
from init import *
import data_acq as da
from icecream import ic
from datetime import datetime 

def time_format():
    return f'{datetime.now()}  Manager|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False) # use True for including script file context file  

# Define callback functions
def on_log(client, userdata, level, buf):
        ic("log: "+buf)
            
def on_connect(client, userdata, flags, rc):    
    if rc==0:
        ic("connected OK")                
    else:
        ic("Bad connection Returned code=",rc)
        
def on_disconnect(client, userdata, flags, rc=0):    
    ic("DisConnected result code "+str(rc))
        
def on_message(client, userdata, msg):
    topic=msg.topic
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    ic("message from: " + topic, m_decode)
    insert_DB(topic, m_decode)

def send_msg(client, topic, message):
    ic("Sending message: " + message)
    #tnow=time.localtime(time.time())
    client.publish(topic,message)   

def client_init(cname):
    r=random.randrange(1,10000000)
    ID=str(cname+str(r+21))
    client = mqtt.Client(client_id=ID, clean_session=True) # create new client instance
    # define callback function       
    client.on_connect=on_connect  #bind callback function
    client.on_disconnect=on_disconnect
    client.on_log=on_log
    client.on_message=on_message        
    if username !="":
        client.username_pw_set(username, password)        
    ic("Connecting to broker ",broker_ip)
    client.connect(broker_ip,int(port))     #connect to broker
    return client

def insert_DB(topic, m_decode):
    # DHT case:
    if "alert" in topic:
        return
    print(f"decode - {m_decode}")
    if 'TEMP' in m_decode: 
        value=parse_data(m_decode)
        if value != 'NA':
            da.add_IOT_data(m_decode.split('From: ')[1].split(' Temperature: ')[0], da.timestamp(), value)
            # TODO - update IOT device last_updated
    if 'ELECTRICITY' in m_decode: 
        # value=parse_data(m_decode)
        da.add_IOT_data('ELECTRICITY-SENSOR', da.timestamp(), m_decode.split(' Electricity: ')[1])
            # TODO - update IOT device last_updated     
    if 'RACK' in m_decode: 
        da.add_IOT_data('RACK-SENSOR', da.timestamp(), m_decode.split(' Temperature_Rack: ')[1])
    if 'WATER' in m_decode: 
        da.add_IOT_data('WATER-SENSOR', da.timestamp(), m_decode.split(' Water: ')[1])
            # TODO - update IOT device last_updated
    # Elec Meter case:
    elif 'Meter' in m_decode:        
        da.add_IOT_data('ElectricityMeter', da.timestamp(), m_decode.split(' Electricity: ')[1].split(' Water: ')[0])
        da.add_IOT_data('WaterMeter', da.timestamp(), m_decode.split(' Water: ')[1])

def parse_data(m_decode):
    value = 'NA'
    print(f"parse_data = {m_decode}")
    # 'From: ' + self.name+ ' Temperature: '+str(temp)+' Humidity: '+str(hum)
    value = m_decode.split(' Temperature: ')[1].split(' Humidity: ')[0]
    return value

def enable(client, topic, msg):
    ic(topic+' '+msg)
    client.publish(topic, msg)

def airconditioner(client,topic, msg):
    ic(topic)
    enable(client, topic, msg)
    pass

def actuator(client,topic, msg):
    enable(client, topic, msg)
    pass

def check_DB_for_change(client):
    print("in check db")
    df = da.fetch_data(db_name, 'data', 'TEMP-SENSOR')
    print(f"the temp df is - {df}")
    if len(df.value)==0: return
    if float(df.value[len(df.value)-1]) > Temp_max:
        msg = f'TEMP-SENSOR: Current Temperature exceed 30 degrees Celsius! at Room_1 - Temperature : {df.value[len(df.value)-1]}'
        ic(msg)
        client.publish(comm_topic+'alert', msg)

    df = da.fetch_data(db_name, 'data', 'ELECTRICITY-SENSOR')
    print(f"the elec df is - {df}")
    if len(df.value)==0: return
    if float(df.value[len(df.value)-1]) > Elec_max:
        msg = f'ELECTRICITY-SENSOR: Current electricity consumption exceed the normal! electricity val - {df.value[len(df.value)-1]}'
        ic(msg)
        client.publish(comm_topic+'alert', msg)

    df = da.fetch_data(db_name, 'data', 'RACK-SENSOR')
    print(f"the rack df is - {df}")
    if len(df.value)==0: return
    if float(df.value[len(df.value)-1]) > RackSensor_max:
        msg = f'RACK-SENSOR - Rack is not healthy in the DC main room! Rack value - {df.value[len(df.value)-1]}'
        ic(msg)
        client.publish(comm_topic+'alert', msg)


    df = da.fetch_data(db_name, 'data', 'WATER-SENSOR')
    print(f"the water df - {df}")
    if len(df.value)==0: return
    if float(df.value[len(df.value)-1]) > Water_max:
        msg = f'WATER-SENSOR: A water leak was detected in the DC main room! water high value - {df.value[len(df.value)-1]}'
        ic(msg)
        client.publish(comm_topic+'alert', msg)


def check_Data(client):
    #ic('we are here')
    try:
        rrows = da.check_changes('iot_devices')
        #ic(rrows)    
        for row in rrows:
            #ic(row)
            topic = row[17]
            if row[10]=='airconditioner':
                msg = 'Set temperature to: ' + str(row[15])
                airconditioner(client, topic, msg)
                da.update_IOT_status(int(row[0]))
            else:
                msg = 'actuated'
                actuator(client, topic, msg)
    except:
        pass            

def main():    
    cname = "Manager-"
    client = client_init(cname)
    # main monitoring loop
    client.loop_start()  # Start loop
    client.subscribe(comm_topic+'#')
    try:
        while conn_time==0:
            print("here-conn_time")
            check_DB_for_change(client)
            time.sleep(conn_time+manag_time)
            check_Data(client) 
            time.sleep(3)       
        ic("con_time ending") 
    except KeyboardInterrupt:
        client.disconnect() # disconnect from broker
        ic("interrrupted by keyboard")

    client.loop_stop()    #Stop loop
    # end session
    client.disconnect() # disconnect from broker
    ic("End manager run script")

if __name__ == "__main__":
    main()
