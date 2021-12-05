#!/usr/bin/env python3

import socket
import requests, json, os
from argparse import ArgumentParser
from dns_generator import ClientHandler
from datetime import datetime
import signal
import sys

# Global variables
IP = '192.168.1.7'
PORT = 53

import threading, time

def load_zones(from_ip, from_port, create_zone_file_flag ):
    if not from_ip:
        return None
    json_zone = {}
    try :
        app_response = requests.get(f'http://{from_ip}:{from_port}/dns/load')
        app_response = app_response.json()
        all_data = app_response['data'] if app_response else None

        if not all_data:
            return None

        for data in all_data:
            zone_name = data["$origin"]
            json_zone[zone_name] = data
            if create_zone_file_flag :
                with open(f'Zones/{zone_name}.zone', 'w+') as f:
                    json.dump(data, f, ensure_ascii=False)    
        
        print('\nZone loaded from Server ',from_ip, from_port,' successfully ', "[ On ",datetime.fromtimestamp(time.time()).strftime("%b %d, %Y - %H:%M:%S"),']')
    except: 
        print('\nEXCEPTION FROM SERVER')
        pass
    
    return json_zone  # {'daidns1.com': content of file 'daidns1.com' }

def load_zones_from_path():
    json_zone = None
    zones_path = "Zones"
    files = []
    try:
        files = os.listdir(zones_path)
    except FileNotFoundError:
        zones_path = "..\Zones"
        files = os.listdir(zones_path)
        print('\nEXCEPTION FROM FILE')

        
    if len(files) == 0 : return 
    
    json_zone = {}
    for zone_file in os.listdir(zones_path):
        with open(os.path.join(zones_path, zone_file), "r") as f:
            data = json.load(f)
            zone_name = data["$origin"]
            json_zone[zone_name] = data

    print('\nZone loaded from folder \/',zones_path,' successfully ', "[ On ",datetime.fromtimestamp(time.time()).strftime("%b %d, %Y - %H:%M:%S"),']')
    return json_zone # {'daidns1.com': content of file 'daidns1.com' } 

def main(from_ip_address, from_port, debug_flag=False):
    REST_TIME = 5 #sec
    def loading(from_ip_address, from_port, debug_flag, sec):
        global ZONES
        print("THREADING ON ")
        ZONES = load_zones(from_ip_address, from_port, debug_flag) or load_zones_from_path() 
        if not ZONES: return 
        time.sleep(sec)
        
    try: # Version Listening IP, Port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((IP, PORT))
        print("\nDNS Listening on {0}:{1} !!\n".format(IP, PORT))
    except: # Version Loading from Zones folder
        print('\nEXCEPTION FROM DNS')
        pass
    
    x = threading.Thread(
        target=loading,
        args=[from_ip_address, from_port, debug_flag, REST_TIME]
    )
    x.start()
    x.join()


    print('-------------------- INITIAL ----------------------------------')
    print("Zones : ")
    if not ZONES : 
        print(f" No Zones is being sent from {0}:{1}!! ".format(from_ip_address, from_port)) 
    else: 
        print("Initial len : ", len(ZONES))
        print("Initial arr : ", [ zone for zone in ZONES ])
    print("---------------- LISTENING ON PORT 53 --------------------")
    print("< Press select 'Kill active process' or CTRL + C to end process, this may take time, please wait >" )
    
    while ZONES:
        try: 
            data, address = sock.recvfrom(650)
            # data: Raw Data , address : Tuple
            # b'I_\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07daidns1\x03com\x00\x00\x01\x00\x01' ('192.168.1.7', 57426)
            # NEW_ZONES = load_zones(from_ip_address, from_port, debug_flag) or load_zones_from_path()
            # if NEW_ZONES != ZONES : ZONES = NEW_ZONES
            if not ZONES :
                x.join()
                raise KeyboardInterrupt
            x = threading.Thread(
                target=loading,
                args=[from_ip_address, from_port, debug_flag, REST_TIME]
            )
            x.start()
            x.join()
            print("\tLen : ", len(ZONES) or 0)
            print("\tArr : ", [ zone for zone in ZONES ])
            if debug_flag == True:
                print("DATA: ", data)
                print("ADDRESS: ", address)

            client = ClientHandler(address, data, sock, ZONES)
            client.run() # return
        except KeyboardInterrupt:
            print("---------------- ENDING WITH CTRL + C --------------------" )
            x.join()
            sock.close()
            break
    print("---------------- CLEANING DNS CACHE --------------------")
    os.system('restartNIC.bat')


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('-db', '--debug', action="store_true",
                        help='Flag to turn on(1)/off(0) debug message, default: off(0) ')

    parser.add_argument('-ip', '--ip',  nargs="?", const='', type=str,
                        help='Application\'s IP Address that sending data to the Server ')

    parser.add_argument('-p', '--port',  nargs="?", const=5000,
                        type=int, help='Option application\'s port')
    args = parser.parse_args()

    debug_flag = args.debug
    from_ip_address = args.ip or socket.gethostbyname(socket.gethostname())
    from_port = args.port

    main(from_ip_address, from_port, debug_flag)
