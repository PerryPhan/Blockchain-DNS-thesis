import threading
from dns_generator import DNSGen


class ClientHandler(threading.Thread):
    """
    Class to handle multiple client DNS requests
    """

    def __init__(self, address, data, sock , zones = None, debug = False):
        threading.Thread.__init__(self)
        self.client_address = address
        self.dns_gen = DNSGen(data, zones ,debug) # dns_gen received raw data
        self.sock = sock
        self.debug = False

    def run(self):
        try : 
            resp = self.dns_gen.make_response()
            self.sock.sendto( self.dns_gen.make_response(), self.client_address)
            print("Request from {0} for {1}".format(self.client_address, self.dns_gen.domain))
        except KeyboardInterrupt:
            pass
        except:
            pass
            
    
