import json
import os

QUESTION_TYPES = {
    b"\x00\x01": "a"
}


class DNSGen(object):
    def __init__(self, data, ZONES = None, debug = False):
        self.data = data
        self.debug = debug
        self.QR = "1"
        self.AA = "1"
        self.TC = "0"
        self.RD = "0"
        self.RA = "0"   # 0= No Recursion Available
        self.Z = "000"
        self.RCODE = "0000"
        self.QDCOUNT = b"\x00\01"   # Answer only 1 question for now
        self.NSCOUNT = b"\x00\x00"  # Nameserver count
        self.ARCOUNT = b"\x00\x00"  # Additional records
        self.format_error = 0       # 1=Error in trying to parse domain parts
        self.domain = ""
        self.ZONES = ZONES if ZONES else self.load_zones()
    
    def get_zone(self, domain):
        zone_name = ".".join(domain)
        zone = {}
        try:
            zone = self.ZONES[zone_name]
            if self.debug == True :
                print("GET ZONES :",zone)
            
        except KeyError:
            return None
        return zone
    
        
    def _get_transaction_id(self):
        return self.data[0:2]  # first 2 bytes have transaction ID

    def _get_opcode(self):
        byte1 = self.data[2:3]    # get 1 byte after transaction id
        opcode = ""
        for bit in range(1, 5):	    # loop bits till end of OPCODE bit
            opcode += str(ord(byte1) & (1 << bit))	   # ord converts byte to unicode int
        return opcode

    def _generate_flags(self):
        flags1 = int(self.QR + self._get_opcode() + self.AA + self.TC + self.RD, 2).to_bytes(1, byteorder="big")
        flags2 = int(self.RA + self.Z + self.RCODE).to_bytes(1, byteorder="big")
        return flags1 + flags2

    def _get_question_domain_type(self, data):
        # data = b'\x07daidns1\x03com\x00\x00\x01\x00\x01'
        self.format_error = 0
        state = 0   # 1 = parsing for text labels, 0 = update length of next text to parse
        expected_length = 0
        domain_string = ""
        domain_parts = []
        question_type = None
        x = 0   # count to see if we reach end of subtext to parse
        y = 0   # count number of bytes
        try:
            for byte in data:
                '''
                    BYTE - CHAR : 7 -
                    BYTE - CHAR : 100 - d
                    BYTE - CHAR : 97 - a
                    BYTE - CHAR : 105 - i
                    BYTE - CHAR : 100 - d
                    BYTE - CHAR : 110 - n
                    BYTE - CHAR : 115 - s
                    BYTE - CHAR : 49 - 1
                    BYTE - CHAR : 3 - *
                    BYTE - CHAR : 99 - c
                    BYTE - CHAR : 111 - o
                    BYTE - CHAR : 109 - m
                    BYTE - CHAR : 0 -
                '''
                if state == 1:
                    if byte != 0:   # domain name not ended so add chars
                        domain_string += chr(byte)
                        if self.debug == True : print(f'BYTE - CHAR ( byte != 0 ) : {byte} - {chr(byte)}')
                    x += 1
                    if x == expected_length:    # got to end of this label
                        domain_parts.append(domain_string)
                        if self.debug == True :
                            print("DOMAIN STRING ADD BY (x == expected_length): ",domain_string)
                            print("DOMAIN PARTS: ",domain_parts)
                        domain_string = ""
                        state = 0   # ensure that next loop captures the byte length of the next label
                    if byte == 0:   # Check if we have reached the end of the question domain
                        domain_parts.append(domain_string)
                        if self.debug == True :
                            print(f'BYTE - CHAR ( byte = 0 ) : {byte} - {chr(byte)}')
                            print("DOMAIN STRING ADD BY (byte = 0): ",domain_string)
                            print("DOMAIN PARTS: ",domain_parts)
                        break
                else:
                    state = 1
                    expected_length = byte # byte = #\x07 => expected_length = 7
                y += 1 
            question_type = data[y:y+2]    # after the domain the next 2 bytes are question type
            # data[y,y+2] = NG : \x00\x00\  OK : \x00\x00\x01\
            self.domain = ".".join(domain_parts) # ".".join(['daidns1','com']) -> 'daidns1.com'
        except IndexError:
            self.format_error = 1
        finally:
            return domain_parts, question_type

    def _get_records(self, data):
        # data = b'\x07daidns1\x03com\x00\x00\x01\x00\x01'
        domain, question_type = self._get_question_domain_type(data) # daidns1, \x00\x00\x01\
        if question_type is None and len(domain) == 0:
            return {}, "", ""
        qt = ""
        
        try:
            qt = QUESTION_TYPES[question_type]
            # print("GET QUESTION TYPE BY TRY ", question_type)
        except KeyError:
            qt = "a"
            # print("GET QUESTION TYPE BY EXCEPT ", question_type)
        zone = self.get_zone(domain) # Search in domain
        if zone is None:
            return [], qt, domain   # empty list ensure a domain we don't have returns correct data
        return zone[qt], qt, domain 

    @staticmethod
    def _record_to_bytes(domain_name, record_type, record_ttl, record_value):
        resp = b"\xc0\x0c"
        if record_type == "a":
            resp += b"\x00\x01"
        resp += b"\x00\x01"    # class IN
        resp += int(record_ttl).to_bytes(4, byteorder="big")    # ttl in bytes
        if record_type == "a":
            resp += b"\x00\x04"    # IP length
            for part in record_value.split("."):
                resp += bytes([int(part)])
        return resp

    def _make_header(self, records_length):
        transaction_id = self._get_transaction_id()
        ancount = records_length.to_bytes(2, byteorder="big")
        if self.format_error == 1:
            self.RCODE = "0001"  # Format error
        elif ancount == b"\x00\x00":
            self.RCODE = "0003"  # Name error
        flags = self._generate_flags()  # relies on state variable self.RCODE, which modified above if appropriate
        if self.debug == True :
            print( "---BEGIN-MAKING-HEADER-----------")
            print("TX_ID : " ,transaction_id) # data[0:2] = 'I_'
            print("ACCOUNT : " ,ancount)
            print("FLAGS : " ,flags)
            print( "---FINISH-MAKING-HEADER-----------")
        return transaction_id + flags + self.QDCOUNT + ancount + self.NSCOUNT + self.ARCOUNT

    def _make_question(self, records_length, record_type, domain_name):
        
        resp = b""
        if self.format_error == 1:
            return resp
        for part in domain_name:
            length = len(part)
            resp += bytes([length])
            for char in part:
                resp += ord(char).to_bytes(1, byteorder="big")
        resp += b"\x00"    # end labels
        if record_type == "a":
            resp += (1).to_bytes(2, byteorder="big")
        resp += (1).to_bytes(2, byteorder="big")
        if self.debug == True :
            print( "---BEGIN-MAKING-QUESTION-----------")
            print("RESP: " ,resp)
            print( "---FINISH-MAKING-QUESTION-----------")
        return resp

    def _make_answer(self, records, record_type, domain_name):
        resp = b""
        if len(records) == 0 or self.format_error == 1:
            return resp
        for record in records:
            resp += self._record_to_bytes(domain_name, record_type, record["ttl"], record["value"])
        if self.debug == True :
            print( "---BEGIN-MAKING-ANSWER-----------")
            print("RESP: " ,resp)
            print( "---FINISH-MAKING-ANSWER-----------")
        return resp

    def make_response(self):
        records, record_type, domain_name = self._get_records(self.data[12:])
        header   =  self._make_header(len(records)) 
        question =  self._make_question(len(records), record_type, domain_name)
        answer   =  self._make_answer(records, record_type, domain_name)
        response =  header + question + answer
        if self.debug == True :
            print( 'DATA[12:]:', self.data[12:] ) # b'\x07daidns1\x03com\x00\x00\x01\x00\x01'
            print( "RECORDS  : ",records, len(records))
            print( "RECORD_TYPE: ",record_type)
            print( "DOMAIN_NAME: ",domain_name)
            print( "---START-MAKING-RESPONSE-----------")
            print( "HEADER  : ",header)
            print( "QUESTION: ",question)
            print( "ANSWER: ",answer)
            print( "RESPONSE: HEADER + QUESTION + ANSWER")
            print( "---FINISH-MAKING-RESPONSE-----------")
        return response

if __name__ == "__main__":
    pass
