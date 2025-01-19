import pickle
import socket     

class Packet: 
    """
    A class representing a packet of data.

    Attributes:
    name (str): The name of the packet (lowercase).
    data: The data contained in the packet.
    """
    format = 'utf-8'
    header = 64
    
    def __init__(self, name: str = None, data = None) -> None:
        """
        Initializes a Packet object.

        Args:
        name (str): The name of the packet (default is None).
        data: The data contained in the packet (default is None).
        """
        if name is not None:
            if not isinstance(name, str):
                raise TypeError("Name must be a string")
            self.name: str = name.lower()
        else:
            self.name: str = None
        self.data = data
        
    @staticmethod
    def _encode(packet: 'Packet') -> bytes:
        """
        Encodes a Packet object into bytes.

        Args:
        packet (Packet): The Packet object to encode.

        Returns:
        bytes: The encoded Packet object.
        """
        return pickle.dumps(packet.__dict__)
    
    @staticmethod
    def _decode(data: bytes) -> 'Packet':
        """
        Decodes bytes into a Packet object.

        Args:
        data (bytes): The bytes to decode.

        Returns:
        Packet: The decoded Packet object.
        """
        try:
            decoded = pickle.loads(data)
            return Packet(*[decoded[i] for i in decoded])
        except pickle.UnpicklingError as e:
            raise ValueError("Invalid packet data") from e
    
    def __repr__(self) -> str:
        """
        Returns a string representation of the Packet object.

        Returns:
        str: A string representation of the Packet object.
        """
        return str(self.__dict__)

class PacketManager:
    @staticmethod
    def _receive_length(conn: socket.socket) -> int:
        """
        Receives the length of a packet from a socket connection.

        Args:
        conn (socket.socket): The socket connection.

        Returns:
        int: The length of the packet.
        """
        try:
            return int(conn.recv(Packet.header).decode(Packet.format))
        except (ConnectionResetError, ConnectionAbortedError, ValueError):
            return 0
    
    @staticmethod
    def receive(conn: socket.socket) -> 'Packet':
        """
        Receives a packet from a socket connection.

        Args:
        conn (socket.socket): The socket connection.

        Returns:
        Packet: The received packet.
        """
        try:
            length = PacketManager._receive_length(conn)
            if length:
                return Packet._decode(conn.recv(length, socket.MSG_WAITALL))
            return Packet()
        except (ConnectionResetError, ConnectionAbortedError):
            return Packet()
    
    @staticmethod
    def _send_length(data: bytes) -> bytes:
        """
        Sends the length of a packet.

        Args:
        data (bytes): The packet data.

        Returns:
        bytes: The length of the packet.
        """
        try:
            length = str(len(data)).encode(Packet.format)
            length += b' ' * (Packet.header - len(length))
            return length
        except (ConnectionResetError, ConnectionAbortedError):
            return b'0' * Packet.header
        
    @staticmethod
    def send(conn: socket.socket, packet: Packet) -> None:
        """
        Sends a packet over a socket connection.

        Args:
        conn (socket.socket): The socket connection.
        packet (Packet): The packet to send.
        """
        try:
            packet_data = Packet._encode(packet)
            conn.send(PacketManager._send_length(packet_data))
            conn.send(packet_data)
        except (ConnectionResetError, ConnectionAbortedError):
            pass