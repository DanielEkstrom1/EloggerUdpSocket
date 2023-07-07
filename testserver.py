import socket
import pandas
import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

datadict = {
    "320008014E9B00DF":"ElPanna",
    "FB0008014E9B01DF":"LVP",
    "F700000CB6819C28":"Retur",
    "F500000CB417CC28":"Framled",
    "2A00000CB676EA28":"Till Vp",
    "0C00000CB3B6ED28":"Från VP",
    "6D00000B9C480928":"Ute temp",
    "9600000CB5120428":"Sov1 Kv",
    "2400000B9C30CE28":"Sov2 Kv",
    "CA00000B9E12E128":"Hall",
    "0100000CB52FBF28":"Sov Öv",
    "6C00000CB3B91128":"Badr Kv",
    "F500000CB53D6528":"V vatten",
}

results = {}

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

bucket = "e-logger"
org = "proxmox"
token = "VVlG0-svAlA3uGbzEmklKzLCzHkJIueVZwo9TMJpmZFuToy1jdJkHXR9UCbfL-ANC9WmVZO1VTS68z5bAn6Bjg=="
# Store the URL of your InfluxDB instance
url="http://192.168.0.156:8086/"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)
    
sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

print("Starting")
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data = data.decode().split("&")
    for item in data:
      id_, value = item.split('=')
      name = datadict.get(id_, id_)
      results[name] = value
      write_api.write(bucket=bucket,org=org,record=influxdb_client.Point("_measurement").tag("location", name).field("temperature", float(value)))
    print(results)
    results.clear()
    time.sleep(1)
    
    
#b'320008014E9B00DF=14&FB0008014E9B01DF=0&F700000CB6819C28=20.9&F500000CB417CC28=20.7&2A00000CB676EA28=24.4&0C00000CB3B6ED28=40.5&6D00000B9C480928=20.7&9600000CB5120428=20.1&2400000B9C30CE28=20.2&CA00000B9E12E128=21&0100000CB52FBF28=21&6C00000CB3B91128=19.9&F500000CB53D6528=41.3'