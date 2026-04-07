from pythonosc import udp_client

class OSCSender:
    def __init__(self, ip="127.0.0.1", port=7700):
        # QLC+ default OSC port is usually 7700
        self.ip = ip
        self.port = port
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        print(f"OSCSender connected to {self.ip}:{self.port}")

    def send_intensity(self, fixture_id, intensity):
        """Sends an intensity value (0-255) to a fixture."""
        # QLC+ OSC paths are usually tied to Virtual Console widgets.
        # A simple structure could be /<fixture_id>/intensity
        path = f"/{fixture_id}/intensity"
        self.client.send_message(path, intensity)
        print(f"OSC -> {path}: {intensity}")

    def send_color(self, fixture_id, r, g, b):
        path = f"/{fixture_id}/color"
        self.client.send_message(f"{path}/r", r)
        self.client.send_message(f"{path}/g", g)
        self.client.send_message(f"{path}/b", b)
        print(f"OSC -> {path} (R:{r}, G:{g}, B:{b})")
        
    def send_pan_tilt(self, fixture_id, pan, tilt):
        self.client.send_message(f"/{fixture_id}/pan", pan)
        self.client.send_message(f"/{fixture_id}/tilt", tilt)
        print(f"OSC -> /{fixture_id}/pan_tilt (P:{pan}, T:{tilt})")

    def send_strobe_rate(self, fixture_id, rate):
        self.client.send_message(f"/{fixture_id}/rate", rate)
        print(f"OSC -> /{fixture_id}/rate: {rate}")
