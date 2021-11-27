#!/usr/bin/env python3
import socket
import os, json
from dns_generator import ClientHandler

# Global variables
IP = '192.168.1.7'
PORT = 53

def load_zones():
    json_zone = {}
    zones_path = "Zones"
    files = []
    try:
        files = os.listdir(zones_path)
    except FileNotFoundError:
        zones_path = "..\Zones"
        files = os.listdir(zones_path)
    for zone_file in os.listdir(zones_path):
        with open(os.path.join(zones_path, zone_file), "r") as f:
            data = json.load(f)
            zone_name = data["$origin"]
            json_zone[zone_name] = data
    
    return json_zone # {'daidns1.com': content of file 'daidns1.com' }


def main():
    ZONE = load_zones()
    print( len(ZONE) )
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    print("DNS Listening on {0}:{1} ...".format(IP, PORT))
    while True:
        data, address = sock.recvfrom(650)
        client = ClientHandler(address, data, sock, ZONE)
        client.run()


if __name__ == "__main__":
    main()
