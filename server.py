import socket
import threading
import time
import os

from packet import packet, packmng

class client:
    def __init__(self, conn: socket.socket, addr):
        self.conn = conn
        self.addr = addr
        self.connected = True
        

class server:
    IP = "localhost"
    PORT = 5050
    ADDR = (IP, PORT)
    CLIENTS: list[client] = []
    
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(server.ADDR)
        
        self.running = True
    
    def close_server(self) -> None:
        for client in server.CLIENTS:
            pack = packet('close', "Server closed! Press ENTER")
            packmng.send(client.conn, pack)
            
        
        self.running = False
        self.server.close()
    
    def handle_client(self, client: client) -> None:
        print(f"[NEW CONNECTION] {client.addr} connected")
        server.CLIENTS.append(client)
        
        while client.connected:
            try:
                pack = packmng.recv(client.conn)
                if pack.name is not None: print(pack)
                if pack.name == 'close': self.close_server() # Change this if u want ^^)
                if pack.name == 'disconnect': client.connected = False
                if pack.name == 'ping':
                    c_time = time.time()
                    print(c_time, pack.data, c_time-pack.data)
                    serv_pack = packet("pong", [c_time-pack.data, c_time])
                    packmng.send(client.conn, serv_pack)
            
            except ConnectionResetError:
                client.connected = False
        
        client.conn.close()
        server.CLIENTS.remove(client)
        print(f"[DISCONNECTION] {client.addr} disconnected")
    
    def run(self) -> None:
        os.system("cls")
        self.server.listen()
        print(f"Server listening on {server.IP}:{server.PORT}")
        
        while self.running:
            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client(conn, addr), ))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {len(server.CLIENTS)+1}")
            except OSError:
                pass
            
def main():
    server_instance = server()
    server_instance.run()
    
if __name__ == "__main__":
    main()
        