from datetime import datetime
from pathlib import Path
import time
import serial
import serial.tools.list_ports


# --- Configuration ---
BAUD_RATE = 115200
NUM_PINS = 40
HEADER = 0xAA

import time
import serial
import serial.tools.list_ports

# Standard vendor/device identifiers for Arduino UNO, Mega, Nano, and common USB-Serial chips (CH340, FTDI, CP210x)
ARDUINO_KEYWORDS = ["arduino", "ch340", "ftdi", "cp210x", "usb-serial", "ttyacm", "ttyusb"]


def select_and_connect_port(baud_rate=BAUD_RATE):
    """
    Attempts to auto-detect an Arduino port.
    If 1 match is found -> Auto-connects.
    If 0 or >1 matches found -> Prompts user with an interactive CLI menu.
    """
    ports = list(serial.tools.list_ports.comports())

    if not ports:
        raise IOError("❌ No serial ports detected on this computer. Check USB connections.")

    # 1. Filter ports based on known Arduino/USB-Serial keywords
    matching_ports = []
    for port in ports:
        desc = (port.description or "").lower()
        mfg = (port.manufacturer or "").lower()
        dev = (port.device or "").lower()

        if any(keyword in desc or keyword in mfg or keyword in dev for keyword in ARDUINO_KEYWORDS):
            matching_ports.append(port)

    # 2. Decision Logic
    selected_port_name = None

    if len(matching_ports) == 1:
        # Exactly one candidate found -> Auto-select
        auto_port = matching_ports[0]
        print(f"🤖 Auto-detected device: {auto_port.device} ({auto_port.description})")
        selected_port_name = auto_port.device

    else:
        # 0 or multiple candidates found -> Fallback to interactive menu
        if len(matching_ports) > 1:
            print(f"⚠️ Found {len(matching_ports)} candidate devices. Please select one:")
        else:
            print("⚠️ Could not automatically identify an Arduino. Please choose from all available ports:")

        print("\n--- Available Serial Ports ---")
        for idx, port in enumerate(ports):
            match_tag = " (Suggested)" if port in matching_ports else ""
            print(f" [{idx + 1}] {port.device} - {port.description}{match_tag}")

        # Interactive user prompt
        while True:
            try:
                choice = int(input("\nSelect port number to connect: ")) - 1
                if 0 <= choice < len(ports):
                    selected_port_name = ports[choice].device
                    break
                else:
                    print(f"Invalid option. Please enter a number between 1 and {len(ports)}.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    # 3. Establish Serial Connection
    print(f"Connecting to {selected_port_name} at {baud_rate} baud...")
    ser = serial.Serial(selected_port_name, baud_rate, timeout=1)
    time.sleep(2)  # Wait for Arduino auto-reset on connection
    print("✅ Connection established successfully!")

    return ser


def process_packet(payload):
    """Verifies checksum and unpacks 5 data bytes into a list of 40 booleans."""
    checksum = 0
    for byte in payload[0:6]:
        checksum ^= byte

    if checksum != payload[6]:
        print(f"Checksum error! Packet corrupted/dropped.")
        return None

    data_bytes = payload[1:6]
    pin_states = []

    for i in range(NUM_PINS):
        byte_idx = i // 8
        bit_idx = i % 8
        is_on = bool((data_bytes[byte_idx] >> bit_idx) & 1)
        pin_states.append(is_on)

    return pin_states


def get_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d-%Hh%Mm%Ss")


class Reader:

    def __init__(self, gtr_pin, swt_pin, direc):
        self.gtr_pin = gtr_pin
        self.swt_pin = swt_pin

        self.gtr_reads = []
        self.swt_reads = []
        self.gtr_switch_times = {}

        self.enabled = False
        self.directory = Path(direc)

    def read_from_packet(self, pin_data, timestamp):
        nxt_swt_reads = pin_data[self.swt_pin]
        self.swt_reads.append(nxt_swt_reads)

        # State machine transition handling
        recent_3_swt = self.swt_reads[-3:].count(True) == 3
        recent_10_swt = self.swt_reads[-10:].count(True) == 10

        if self.enabled and recent_10_swt:
            # Disable port if held down for 10 samples
            self.enabled = False
            self.save_data()

        elif not self.enabled and recent_3_swt:
            # Enable port
            self.enabled = True
            self.gtr_reads = []
            self.gtr_switch_times = {timestamp: "LIGADO"}

        elif self.enabled and recent_3_swt:
            # Reset port
            self.save_data()
            self.gtr_reads = []
            self.gtr_switch_times = {timestamp: "RESET"}

        # Track Gator Pin toggles when enabled
        if self.enabled:
            nxt_gtr_reads = pin_data[self.gtr_pin]
            self.gtr_reads.append(nxt_gtr_reads)

            # Requires at least 2 readings to compare state change
            if len(self.gtr_reads) >= 2:
                if self.gtr_reads[-1] != self.gtr_reads[-2]:
                    self.gtr_switch_times[timestamp] = (
                        "On" if nxt_gtr_reads else "Off"
                    )

    def save_data(self, timestamp=None):
        if not self.gtr_switch_times:
            return  # Nothing to save

        if timestamp is None:
            timestamp = get_time()

        port_num = int(1 + self.gtr_pin // 2)
        port_name = f"{timestamp}--port-{port_num}"

        port_txt_l1 = ",".join(self.gtr_switch_times.keys())
        port_txt_l2 = ",".join(self.gtr_switch_times.values())
        port_txt = f"{port_txt_l1}\n{port_txt_l2}"

        save_dir = self.directory / "medicoes"
        save_dir.mkdir(parents=True, exist_ok=True)

        with open(save_dir / f"{port_name}.csv", "w", encoding="utf-8") as f:
            f.write(port_txt)


class DataProcessor:

    def __init__(self, directory):
        self.directory = Path(directory)
        self.readers = [
            Reader(port, port + 1, self.directory)
            for port in range(0, NUM_PINS, 2)
        ]
        self.processed_files = set()

    def process_data(self, files=None):
        if files is None:
            data_dir = self.directory / "data"
            files = sorted(
                [f for f in data_dir.glob("*.bin") if f not in self.processed_files],
                key=lambda x: int(x.stem),
            )

        for file_path in files:
            file_path = Path(file_path)
            if not file_path.exists():
                continue

            with open(file_path, "rb") as f:
                full_packet = f.read()

            pins = process_packet(full_packet)
            if pins is not None:
                for reader in self.readers:
                    reader.read_from_packet(pins, file_path.stem)

            self.processed_files.add(file_path)

        timestamp = get_time()
        for reader in self.readers:
            reader.save_data(timestamp)


def main():
    cwd = Path.cwd()

    # Ensure required subdirectories exist
    (cwd / "data").mkdir(parents=True, exist_ok=True)
    (cwd / "medicoes").mkdir(parents=True, exist_ok=True)

    try:
        ser = select_and_connect_port(BAUD_RATE)
        time.sleep(2)

        message_count = 0
        data_processor = DataProcessor(cwd)
        pending_files = []

        while True:
            byte_in = ser.read(1)
            print(byte_in)
            if not byte_in:
                continue

            if byte_in[0] == HEADER:
                remaining_bytes = ser.read(6)

                if len(remaining_bytes) == 6:
                    read_time_ms = time.time_ns() // 1000000  # Convert to ms
                    full_packet = bytearray([HEADER]) + remaining_bytes
                    pins = process_packet(full_packet)

                    if pins is not None:
                        message_count += 1
                        filepath = cwd / "data" / f"{read_time_ms}.bin"

                        with open(filepath, "wb") as f:
                            f.write(full_packet)

                        active_count = sum(pins)
                        pins = ''.join([('1' if pin==True else '0') for pin in pins])
                        pin_blocks = ' '.join([pins[i:i+10] for i in range(0, len(pins), 10)])
                        print(
                            f"[{message_count}] Active Pins: {active_count}/40  |  {pin_blocks}"
                        )
                        pending_files.append(filepath)

            # Batch processing every 10 packets
            if message_count > 0 and message_count % 10 == 0 and pending_files:
                data_processor.process_data(pending_files)
                pending_files = []

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nStopping reader...")
    finally:
        if "ser" in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")


if __name__ == "__main__":
    main()