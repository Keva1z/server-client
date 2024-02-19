import socket
import threading
import time
import os

from packet import packmng, packet

class client:
    def __init__(self, IP: str, PORT: int) -> None:
        os.system("cls")
        self.IP = IP
        self.PORT = PORT
        self.ADDR = (IP, PORT)
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(self.ADDR)
        except ConnectionRefusedError:
            print(f"Cant connect to server {self.IP}:{self.PORT}")
            exit()
        
        self.connected = True
        self.ping = 0
        
        thread = threading.Thread(target=self.reciving)
        thread.start()
        
        while self.connected:  # Simple menu to use basic client commands. This can be changed
            command = input(">> ")
            if command == 'ping': self.ping_pong()
            elif command == 'kill': self.kill_snc()
            elif command == 'disconnect': self.disconnect()
            time.sleep(0.5)
    
    def ping_pong(self) -> None:
        pack = packet("ping", time.time())
        packmng.send(self.client, pack)
        
    def kill_snc(self) -> None:
        pack = packet("close")
        packmng.send(self.client, pack)
        self.disconnect()
        
    def disconnect(self):
        pack = packet("disconnect")
        packmng.send(self.client, pack)
        time.sleep(1)
        self.connected = False
        self.client.close()
        exit()
        
    def send(self, name: str, data) -> None:
        pack = packet(name, data)
        packmng.send(self.client, pack)
    
    def reciving(self):
        while self.connected:
            try:
                pack = packmng.recv(self.client)
                
                if pack.name is not None:
                    print(f"[SERVER] {pack.data}")
                    if pack.name == 'close': self.disconnect()
                    if pack.name == 'pong':
                        print(f"[SERVER] ping: {int((pack.data[0]+time.time()-pack.data[1])/100)}ms")
            except ConnectionAbortedError:
                self.disconnect()
            except ConnectionResetError:
                self.disconnect()
                

def get_valid_addr() -> list[str, int]:
    ip, port = input("IP:PORT >> ").split(':')
    try:
        ip, port = ip, int(port)
        if len(ip.split('.')) != 4:
            print(f"Wrong IP format! 255.255.255.255")
            exit()
        for i in ip.split("."):
            try:
                i = int(i)
                if i < 0 or i > 255:
                    print(f"IP {i} is > 255 or < 0")
                    exit()
            except ValueError:
                print(f"Wrong IP numbers! {i}")
                exit()
    except ValueError:
        print(f"port must be numbers, not '{port}'")
        exit()
    return [ip, port]

# addr = ("localhost", 5050)

# c = client(addr[0], addr[1])