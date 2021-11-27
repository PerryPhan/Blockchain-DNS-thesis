#!/usr/bin/env python3

import socket
import requests, json
from argparse import ArgumentParser
from dns_generator import ClientHandler

# Global variables
IP = '192.168.1.7'
PORT = 53
ZONES = None


def load_zones(from_ip, from_port):
    if not from_ip:
        return None

    json_zone = {}
    app_response = requests.get(f'http://{from_ip}:{from_port}/dns/load')
    app_response = app_response.json()
    all_data = app_response['data'] if app_response else None

    if not all_data:
        return None

    for data in all_data:
        zone_name = data["$origin"]
        json_zone[zone_name] = data
        with open(f'Zones/{zone_name}.zone', 'w+') as f:
            json.dump(data, f, ensure_ascii=False)    
    

    return json_zone  # {'daidns1.com': content of file 'daidns1.com' }


def main(from_ip_address, from_port, debug_flag=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    ZONES = load_zones(from_ip_address, from_port)
    print("DNS Listening on {0}:{1} ...".format(IP, PORT))
    print("ZONES : ", ZONES)
    while True:
        data, address = sock.recvfrom(650)
        # data: Raw Data , address : Tuple
        # b'I_\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07daidns1\x03com\x00\x00\x01\x00\x01' ('192.168.1.7', 57426)
        if debug_flag == True:
            print("DATA: ", data)
            print("ADDRESS: ", address)
        client = ClientHandler(address, data, sock, None)
        client.run() # return


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('-db', '--debug', action="store_true",
                        help='Flag to turn on(1)/off(0) debug message, default: off(0) ')

    parser.add_argument('-ip', '--ip',  nargs="?", const='0.0.0.0', type=str,
                        help='Application\'s IP Address that sending data to the Server ')

    parser.add_argument('-p', '--port',  nargs="?", const=5000,
                        type=int, help='Option application\'s port')
    args = parser.parse_args()

    debug_flag = args.debug
    from_ip_address = args.ip
    from_port = args.port

    main(from_ip_address, from_port, debug_flag)
