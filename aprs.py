import socket
import math

def get_passcode(callsign):
    base = callsign.split("-")[0].upper()
    hash = 0x73E2
    for idx, character in enumerate(base):
        update = ord(character)
        if idx % 2 == 0:
            update *= 2**8
        hash ^= update
    return str(hash & 0x7FFF)

def position_report(callsign, destination="APRS", latitude=0, longitude=0, timestamp=None, altitude=None, comment=""):
    latletter = "N"
    if latitude < 0:
        latletter = 'S';
        latitude *= -1
    latmins = (latitude - math.floor(latitude)) * 60
    latstring = f"{math.floor(latitude):02.0f}{latmins:05.2f}{latletter}"
    
    lonletter = "E"
    if longitude < 0:
        lonletter = "W"
        longitude *= -1
    lonmins = (longitude - math.floor(longitude)) * 60
    lonstring = f"{math.floor(longitude):03.0f}{lonmins:05.2f}{lonletter}"

    if timestamp:
        timestring = timestamp.strftime("/%H%M%Sh")
    else:
        timestring = "!"

    altstring = ""
    if not altitude is None:
        altstring = f" /A={int(altitude)}"

    if comment:
        if not comment.startswith(" "):
            comment = " " + comment

    return f"{callsign}>{destination}:{timestring}{latstring}/{lonstring}>{altstring}{comment}\r\n"

class APRS(object):
    def __init__(self, server="rotate.aprs.net", port=10152, timeout=3):
        self.server = server
        self.port = port
        self.timeout = timeout

    def __enter__(self):
        self.sock = socket.create_connection((self.server, self.port), self.timeout)
        header = self.sock.recv(512).decode('UTF-8')
        if not header.startswith("#") or not header.endswith("\r\n"):
            print(f"Invalid header received: {header}")
        print(f"Connected to {self.sock.getpeername()}")
        return self

    def __exit__(self, type, value, traceback):
        self.sock.close()

    def login(self, callsign):
        passcode = get_passcode(callsign)
        self.sock.sendall(f"user {callsign} pass {passcode} vers customlib 1.0\r\n".encode('UTF-8'))
        
        auth = self.sock.recv(100).decode('UTF-8')
        
        if not auth.startswith("#") or not auth.endswith("\r\n"):
            print(f"Invalid auth received: {auth}")
            return False
        
        _, msgtype, call, status, _, server = auth.split(" ")
        
        if msgtype != "logresp":
            print(f"Unexpected message: {auth}")
            return False
        
        if status != "verified,":
            print(f"Login failed! {status}")
            return False
        print("Logged In")
        return True
        
    def send(self, data):
        print(f"Sending {data}")
        self.sock.sendall(data.encode("UTF-8"))
        print(self.sock.recv(100))