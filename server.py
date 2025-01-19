import socket
import threading
import time
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

from packet import Packet, PacketManager

class Client:
    def __init__(self, conn: socket.socket, addr):
        self.conn = conn
        self.addr = addr
        self.connected = True

class Server:
    IP = "localhost"
    PORT = 5050
    ADDR = (IP, PORT)
    clients: list[Client] = []
    
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.running = True
        logging.info("Server initialized and bound to %s:%d", self.IP, self.PORT)
    
    def shutdown(self) -> None:
        for client in self.clients:
            try:
                pack = Packet('close', "Server closed! Press ENTER")
                PacketManager.send(client.conn, pack)
                client.connected = False
            except Exception as e:
                logging.error("Error sending close packet to client: %s", e)
            
        time.sleep(1)
        self.running = False
        try:
            self.server.close()
        except Exception as e:
            logging.error("Error closing server socket: %s", e)
        logging.info("Server shutdown initiated.")
    
    def handle_client(self, client: Client) -> None:
        logging.info("[NEW CONNECTION] %s connected", client.addr)

        self.send_to_all(Packet("new_client", client.addr))

        self.clients.append(client)
        
        while client.connected:
            try:
                pack = PacketManager.receive(client.conn)
                if pack.name is not None:
                    logging.info("Received packet: %s", pack)
                if pack.name == 'close':
                    logging.info("Received close packet from %s", client.addr)
                    self.shutdown()
                if pack.name == 'disconnect':
                    client.connected = False
                if pack.name == 'ping':
                    c_time = time.time()
                    logging.info("Ping received with data: %s", pack.data)
                    serv_pack = Packet("pong", [c_time-pack.data, c_time])
                    PacketManager.send(client.conn, serv_pack)
                if pack.name == 'sendall':
                    pack.data = {"message": pack.data, "from": client.addr}
                    self.send_to_all(pack)
            except ConnectionResetError:
                client.connected = False
            except Exception as e:
                logging.error("Error handling client: %s", e)
        
        try:
            client.conn.close()
        except Exception as e:
            logging.error("Error closing client socket: %s", e)
        self.clients.remove(client)
        logging.info("[DISCONNECTION] %s disconnected", client.addr)
    
    def send_to_all(self, pack: Packet) -> None:
        for client in self.clients:
            try:
                PacketManager.send(client.conn, pack)
            except Exception as e:
                logging.error("Error sending packet to client: %s", e)

    def run(self) -> None:
        os.system("cls")
        self.server.listen()
        logging.info("Server listening on %s:%d", self.IP, self.PORT)
        
        while self.running:
            try:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(Client(conn, addr), ))
                thread.start()
                logging.info("[ACTIVE CONNECTIONS] %d", len(self.clients)+1)
            except OSError:
                pass
            except Exception as e:
                logging.error("Error accepting client connection: %s", e)
            
def main():
    server_instance = Server()
    server_instance.run()
    
if __name__ == "__main__":
    main()