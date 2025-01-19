import socket
import threading
import time
import os

from packet import PacketManager, Packet

COMMAND_PING = 'ping'
COMMAND_KILL = ['kill', "close"]
COMMAND_DISCONNECT = 'disconnect'
COMMAND_SENDDATA = ["msg", "talk", "senddata"]

class Client:
    def __init__(self, IP: str, PORT: int) -> None:
        os.system("cls")
        self.IP = IP
        self.PORT = PORT
        self.ADDR = (IP, PORT)
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(self.ADDR)
        except ConnectionRefusedError:
            print(f"Can't connect to server {self.IP}:{self.PORT}")
            exit(1)
        
        self.connected = True
        self.ping = 0
        
        thread = threading.Thread(target=self.receiving)
        thread.start()
        
        while self.connected:
            command = input(">> ").lower()
            if ":" in command:
                command, data = command.split(":", 1)
            else:
                data = None

            if command in COMMAND_PING: self.ping_pong()
            elif command in COMMAND_KILL: self.kill_snc()
            elif command in COMMAND_DISCONNECT: self.disconnect()
            elif command in COMMAND_SENDDATA: self.send("sendall", data)
            time.sleep(0.5)

    def ping_pong(self) -> None:
        pack = Packet("ping", time.time())
        PacketManager.send(self.client, pack)
        
    def kill_snc(self) -> None:
        pack = Packet("close")
        PacketManager.send(self.client, pack)
        
    def disconnect(self):
        pack = Packet("disconnect")
        PacketManager.send(self.client, pack)
        time.sleep(1)
        self.connected = False
        self.client.close()
        exit(0)

    def send(self, name: str, data) -> None:
        pack = Packet(name, data)
        PacketManager.send(self.client, pack)
    
    def receiving(self):
        while self.connected:
            try:
                pack = PacketManager.receive(self.client)
                
                if pack.name is not None:
                    if "from" not in pack.data:
                        print(f"[SERVER:{pack.name}] {pack.data}")
                    if pack.name == 'close':
                        self.connected = False
                        self.client.close()
                        exit(0)
                    if pack.name == 'pong':
                        print(f"[SERVER] ping: {int((pack.data[0]+time.time()-pack.data[1])/100)}ms")
                    if pack.name == "new_client":
                        print(f"[{pack.data[1]}] connected")
                    if pack.name == "sendall":
                        if pack.data['from'] == self.ADDR[1]:
                            continue
                        print(f"[{pack.data['from'][0]}:{pack.data['from'][1]}] {pack.data['message']}")
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

addr = ("localhost", 5050)

c = Client(addr[0], addr[1])