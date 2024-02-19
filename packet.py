import pickle
import socket     

class packet: 
    format = 'utf-8'
    header = 64
    
    def __init__(self, name: str = None, data = None) -> None:
        self.name: str = name
        self.data = data
        if self.name is not None: self.name = self.name.lower()
    
    @staticmethod
    def _encode(object) -> bytes:
        return pickle.dumps(object.__dict__)
    
    @staticmethod
    def _decode(data: bytes):
        decoded = pickle.loads(data)
        return packet(*[decoded[i] for i in decoded])
    
    def __repr__(self) -> str:
        return str(self.__dict__)

class packmng:
    @staticmethod
    def _rclength(conn: socket.socket) -> int:
        try:
            return conn.recv(packet.header).decode(packet.format)
        except ConnectionResetError:
            return 0
        except ConnectionAbortedError:
            return 0
    
    @staticmethod
    def recv(conn: socket.socket):
        try:
            h_len = packmng._rclength(conn)
            if h_len:
                return packet._decode(conn.recv(int(h_len), socket.MSG_WAITALL))
            return packet()
        except ConnectionResetError:
            return packet()
        except ConnectionAbortedError:
            return packet()
    
    @staticmethod
    def _sndlength(data: bytes) -> bytes:
        try:
            length = str(len(data)).encode(packet.format)
            length += b' ' * (packet.header - len(length))
            return length
        except ConnectionResetError:
            return 0
        except ConnectionAbortedError:
            return 0
        
    @staticmethod
    def send(conn: socket.socket, pack: packet) -> None:
        try:
            pack = packet._encode(pack)
            conn.send(packmng._sndlength(pack))
            conn.send(pack)
        except ConnectionResetError:
            pass
        except ConnectionAbortedError:
            pass