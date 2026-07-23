"""ESP32 communication interface (placeholder for WiFi/MQTT hardware I/O)."""

import json

from ..state import TwinState


class ESP32Interface:
    """Receive sensor data and send actuator commands to the physical chamber.

    The transport (WiFi/MQTT) is not implemented; `receive_sensor_data` returns
    the last packet stored on the interface and `send_commands` prints the
    actuator packet. These are the integration points for real hardware.
    """

    def __init__(self):
        self.connected = False
        self.ip_address = None
        self.last_received = {}
        self.last_command = {}

    def connect(self, ip_address: str) -> None:
        self.connected = True
        self.ip_address = ip_address

    def disconnect(self) -> None:
        self.connected = False
        self.ip_address = None

    def receive_sensor_data(self) -> dict:
        """Placeholder for a real ESP32 sensor packet."""
        return self.last_received

    def update_twin(self, state: TwinState) -> None:
        """Update TwinState using the received sensor data, if any."""
        data = self.receive_sensor_data()
        if len(data) == 0:
            return

        state.temperature = data.get("temperature", state.temperature)
        state.humidity = data.get("humidity", state.humidity)
        state.co2 = data.get("co2", state.co2)
        state.moisture = data.get("moisture", state.moisture)

    def actuator_packet(self, state: TwinState) -> dict:
        packet = {
            "cooling_pad": state.cooling_pad,
            "heater": state.heater,
            "fogger": state.fogger,
            "sprinkler": state.sprinkler,
            "exhaust_fan": state.exhaust_fan,
            "fresh_air_fan": state.fresh_air_fan,
        }
        self.last_command = packet
        return packet

    def send_commands(self, state: TwinState) -> None:
        """Placeholder for WiFi/MQTT communication."""
        packet = self.actuator_packet(state)
        print(json.dumps(packet, indent=4))

    def health_check(self) -> bool:
        """Check communication status."""
        return self.connected

    def status(self) -> dict:
        """Return communication status."""
        return {
            "Connected": self.connected,
            "IP Address": self.ip_address,
            "Last Sensor Packet": self.last_received,
            "Last Command Packet": self.last_command,
        }

    def validate(self) -> bool:
        """Validate communication interface state."""
        if not isinstance(self.connected, bool):
            return False
        if not isinstance(self.last_received, dict):
            return False
        if not isinstance(self.last_command, dict):
            return False
        return True

    def reset(self) -> None:
        self.connected = False
        self.ip_address = None
        self.last_received = {}
        self.last_command = {}

    def print_status(self) -> None:
        print("\n" + "=" * 70)
        print("ESP32 COMMUNICATION STATUS")
        print("=" * 70)
        print(f"Connected : {self.connected}")
        print(f"IP Address : {self.ip_address}")
        print(f"Last Sensor Packet : {self.last_received}")
        print(f"Last Command Packet : {self.last_command}")
        print("=" * 70)
