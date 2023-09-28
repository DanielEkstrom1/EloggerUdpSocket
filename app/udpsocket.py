import socket
import pandas
import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import dotenv
import logging


logging.basicConfig(filename='app.log', level=logging.ERROR,
                    format='%(asctime)s [%(levelname)s]: %(message)s')


def main():
    datadict = {
        "320008014E9B00DF": "ElPanna",
        "FB0008014E9B01DF": "LVP",
        "F700000CB6819C28": "Retur",
        "F500000CB417CC28": "Framled",
        "2A00000CB676EA28": "Till vp",
        "0C00000CB3B6ED28": "Från VP",
        "6D00000B9C480928": "Utetemp",
        "9600000CB5120428": "Sov1 Kv",
        "2400000B9C30CE28": "Sov2 Kv",
        "CA00000B9E12E128": "Hall",
        "0100000CB52FBF28": "Sov Öv",
        "6C00000CB3B91128": "Badr Kv",
        "F500000CB53D6528": "V Vatten",
    }
    print("STARTING")

    dotenv.load_dotenv()
    try:
        BUCKET = os.environ.get('bucket')
        ORG = os.environ.get('org')
        TOKEN = os.environ.get('token')
        UDP_IP = os.environ.get('UDP_IP')
        UDP_PORT = int(os.environ.get('UDP_PORT'))

        # Store the URL of your InfluxDB instance
        URL = os.environ.get("url")
    except Exception as e:
        logging.error(f"Error reading env vars: {e}")
        return

    try:
        client = influxdb_client.InfluxDBClient(
            url=URL,
            token=TOKEN,
            org=ORG
        )

        write_api = client.write_api(write_options=SYNCHRONOUS)
    except Exception as e:
        logging.error(f"Error creating influxdb client: {e}")
        return
    try:
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))
    except Exception as e:
        logging.error(f"Error creating socket: {e}")
        return

    logging.info("Socket created")
    logging.info("STARTED")
    results = {}

    while True:
        try:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            data = data.decode().split("&")
            logging.info(f"Recieved data: {data}")
            for item in data:
                id_, value = item.split('=')
                name = datadict.get(id_, id_).replace(" ", "-")
                results[name] = value
                write_api.write(bucket=BUCKET, org=ORG, record=influxdb_client.Point(
                    "_measurement").tag("location", name).field("temperature", float(value)))
            logging.info(f"Data written to InfluxDB: {results}")
            results.clear()
        except Exception as e:
            logging.error(f"Error data: {e}")


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(f"Main function crashed: {e}")
            time.sleep(5)
