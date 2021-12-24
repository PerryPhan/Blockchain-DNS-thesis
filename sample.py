# from models import db, generate_password_hash, random
import random
import json
import time
import re
import os
# from models import Accounts, Transactions
# Accounts -------------------------------------------------------
# db.session.add(
#     Accounts(
#         fullname='Phan Dai',
#         email='phandai@admin.com',
#         password=generate_password_hash('Phandai2@'),
#         type_cd=1, # ADMIN
#         is_deleted=False
#     )
# )
# Nodes ----------------------------------------------------------
# Transactions ---------------------------------------------------
HEADER = "#[domain] [type] [ip] [port] [ttl-Timetolive]\n"
CONTENTS = []
FILENAME = 'names.txt'


def autoInsertTransaction(number):
    def generateRecordTransaction(domain, ip, type='A', port=80, ttl=14400):
        return {
            'domain': domain,
            'type': type,
            'ip': ip,
            'port': port,
            'ttl': ttl
        }

    domains = generateDomains(number)
    ips = generateIPs(number)
    trans = [generateRecordTransaction(domains[i], ips[i])
             for i in range(number)]
    CONTENTS = [
        f"{tran['domain']} {tran['type']}  {tran['ip']} {tran['port']} {tran['ttl']}\n" for tran in trans]

    f = open("sample.txt", "w")
    f.write(HEADER)
    for content in CONTENTS:
        f.write(content)
    f.close()

    return json.dumps({
        'len': len(trans),
        'transactions': trans
    })
    # for i in range( number ):
    #     db.session.add(Transactions(
    #         hostname= domains[i],
    #         ip= ips[i],
    #         reward= reward,
    #         port= port))


def generateDomains(number):
    FILE = FILENAME
    list = []
    numberOfLine = 0
    with open(FILE) as file:
        for line in file:
            list.append(line[:-1].lower() + '.bit')
            numberOfLine = numberOfLine + 1
    numberOfLine = 100 if numberOfLine == 0 else numberOfLine
    return [list[random.randint(i, numberOfLine)] for i in range(0, number)]


def generateIPs(number):
    FROM = 0
    TO = 255
    list = []
    for i in range(number):
        ip = '192.168.'
        ip += str(random.randint(FROM, TO)) or '0'
        ip += '.'
        ip += str(random.randint(FROM, TO)) or '0'
        list.append(ip)
    return list


number = 5

def generateZoneFiles(number):
    zones_list = []

    domains = generateDomains(number)
    ips = generateIPs(number)

    for i in range(number):
        ZONE_FILE_FORMAT = {
            '$origin':  "{domain}".format(domain=domains[i]),
            '$ttl': 3600,
            'soa': {
                "mname": "ns1.{domain}".format(domain=domains[i]),
                "rname": "admin.{domain}".format(domain=domains[i]),
                        "serial": "{time}".format(time=str(time.time())),
                "refresh": 3600,
                "retry": 600,
                "expire": 604800,
                "minimum": 86400
            },

            'ns':  [
                {"host": "ns1.{domain}".format(domain=domains[i])},
                {"host": "ns2.{domain}".format(domain=domains[i])}
            ],

            'a':  [
                {
                    "name": "@",
                    "ttl": 400,
                    "value": "{ip}".format(ip=ips[i])
                },
                {
                    "name": "@",
                    "ttl": 400,
                    "value": "0.0.0.0"
                },
                {
                    "name": "@",
                    "ttl": 400,
                    "value": "0.0.0.0"
                },
            ],
        }
        sample_path = 'sample/'
        filename = "{domain}.zone".format(domain=domains[i])
        print('Append ',i,') ',filename,' to folder ',sample_path)
        with open(sample_path + filename, 'w+') as f:
            try:
                json.dump(ZONE_FILE_FORMAT, f)
            except:
                return []
        zones_list.append(ZONE_FILE_FORMAT)
    return zones_list


def testOpenJSON():
    json_zone = None
    zones_path = "sample"
    files = []
    try:
        files = os.listdir(zones_path)
    except FileNotFoundError:
        zones_path = "..\sample"
        files = os.listdir(zones_path)

    if len(files) == 0:
        return

    json_zone = {}
    for zone_file in os.listdir(zones_path):
        with open(os.path.join(zones_path, zone_file), "r") as f:
            data = json.load(f)
            zone_name = data["$origin"]
            json_zone[zone_name] = data

    return json_zone


generateZoneFiles(number)
# Blocks ---------------------------------------------------------
# PUSH ALL >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# db.session.commit()
