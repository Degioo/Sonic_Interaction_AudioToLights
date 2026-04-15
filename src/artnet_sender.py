import socket

class ArtNetSender:
    def __init__(self, ip="127.0.0.1", port=6454, universe=0):
        self.ip = ip
        self.port = port
        self.universe = universe
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 512 channels
        self.dmx_data = bytearray(512)
        
        # ArtDmx packet header configuration
        self.header = bytearray(b'Art-Net\x00')
        # OpOutput: 0x5000 (little endian)
        self.header.extend([0x00, 0x50])
        # Protocol Version: 14 (big endian)
        self.header.extend([0x00, 0x0e])
        # Sequence & Physical Port
        self.header.extend([0x00, 0x00])
        # Universe (little endian, max 15 bit)
        self.header.extend([self.universe & 0xFF, (self.universe >> 8) & 0xFF])
        # Length of DMX data (512 -> 0x0200 big endian)
        self.header.extend([0x02, 0x00])
        
        print(f"ArtNetSender connected to {self.ip}:{self.port} (Universe {self.universe})")

    def set_channel(self, address, value):
        """Sets a specific DMX channel (0-indexed address, meaning address 0 = Channel 1) to value (0-255)."""
        if 0 <= address < 512:
            self.dmx_data[address] = max(0, min(255, int(value)))

    def clear_universe(self):
        """Sets all channels to 0."""
        self.dmx_data = bytearray(512)

    def send_universe(self):
        """Sends the current state of the 512 channels as an ArtDmx packet."""
        packet = self.header + self.dmx_data
        self.sock.sendto(packet, (self.ip, self.port))
