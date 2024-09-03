import paho.mqtt.client as mqtt
import yagmail
import os
from icecream import ic
from init import *

class NotificationService:
    def __init__(self, gmail_user, recipient_email, mqtt_broker, mqtt_port, mqtt_topic):
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password
        self.recipient_email = recipient_email
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic

        
        self.mqtt_client = mqtt.Client()
        self.configure_mqtt_callbacks()

    def configure_mqtt_callbacks(self):
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_log = self.on_log

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            ic("Connected to MQTT Broker successfully")
            client.subscribe(self.mqtt_topic)
        else:
            ic(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode("utf-8")
        ic(f"Received message from topic {topic}: {message}")
        self.send_email(f"DCsafe-sytem Critical Alert {topic}", message)

    def on_log(self, client, userdata, level, buf):
        ic(f"MQTT Log: {buf}")

    def send_email(self, subject, body):
        try:
            yag = yagmail.SMTP(self.gmail_user, self.gmail_password)
            yag.send(to=self.recipient_email, subject=subject, contents=body)
            ic(f"Email sent: {subject}")
        except Exception as e:
            ic(f"Failed to send email: {e}")

    def start(self):
        ic(f"Connecting to MQTT Broker: {self.mqtt_broker}:{self.mqtt_port}")
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.mqtt_client.loop_forever()


if __name__ == "__main__":
    service = NotificationService(gmail_user, recipient_email, broker_ip, int(broker_port), alert_topic)
    service.start()
