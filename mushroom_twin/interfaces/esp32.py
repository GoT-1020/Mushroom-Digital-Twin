"""ESP32 communication interface: MQTT transport for WiFi/MQTT hardware I/O."""

import json

import paho.mqtt.client as mqtt

from ..config import Config
from ..state import TwinState


class ESP32Interface:
    """Receive sensor data and send actuator commands to the physical chamber.

    Transport is MQTT (via `paho-mqtt`): the twin subscribes to
    `Config.MQTT_TOPIC_SENSORS` for readings published by the ESP32 firmware, and
    publishes actuator commands to `Config.MQTT_TOPIC_ACTUATORS` for it to consume.
    Until `connect()` is called, both `update_twin()` and `send_commands()` are
    no-ops, so pure-simulation runs are unaffected.
    """

    def __init__(self):
        self.connected = False
        self.ip_address = None
        self.last_received = {}
        self.last_command = {}

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=Config.MQTT_CLIENT_ID,
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.will_set(Config.MQTT_TOPIC_STATUS, "offline", qos=1, retain=True)

    def _on_connect(self, client, userdata, connect_flags, reason_code, properties) -> None:
        if reason_code == 0:
            self.connected = True
            client.subscribe(Config.MQTT_TOPIC_SENSORS, qos=Config.MQTT_QOS)
        else:
            self.connected = False

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties) -> None:
        self.connected = False

    def _on_message(self, client, userdata, msg) -> None:
        try:
            self.last_received = json.loads(msg.payload)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"ESP32Interface: ignoring malformed payload on {msg.topic!r}")

    def connect(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        use_tls: bool = False,
    ) -> None:
        """Connect to the MQTT broker and start the background network loop."""
        if username is not None:
            self.client.username_pw_set(username, password)
        if use_tls:
            self.client.tls_set()

        self.ip_address = host or Config.MQTT_BROKER_HOST
        self.client.connect(self.ip_address, port or Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
        self.client.loop_start()
        self.client.publish(Config.MQTT_TOPIC_STATUS, "online", qos=1, retain=True)

    def disconnect(self) -> None:
        if self.connected:
            self.client.publish(Config.MQTT_TOPIC_STATUS, "offline", qos=1)
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        self.ip_address = None

    def receive_sensor_data(self) -> dict:
        """Latest sensor packet received over MQTT (empty until one arrives)."""
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
        """Publish the actuator packet over MQTT. No-op unless `connect()` was called."""
        packet = self.actuator_packet(state)
        if self.connected:
            self.client.publish(
                Config.MQTT_TOPIC_ACTUATORS, json.dumps(packet), qos=Config.MQTT_QOS, retain=True
            )

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
