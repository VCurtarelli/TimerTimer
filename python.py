from datetime import datetime
from pathlib import Path
import threading
import time
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from io import StringIO
import pandas as pd

# --- Configuration ---
BAUD_RATE = 115200
NUM_PINS = 40
HEADER = 0xAA
PRINT_ACTIVE_PINS = False

ARDUINO_KEYWORDS = [
    "arduino",
    "ch340",
    "ftdi",
    "cp210x",
    "usb-serial",
    "ttyacm",
    "ttyusb",
]

COLOR_B = "#202020"
COLOR_Y = "#E5BF00"
COLOR_G = "#46E890"
COLOR_W = "#E0E0E0"
PORT_COLORS = [COLOR_W, COLOR_B, COLOR_Y, COLOR_G] * 4
PORT_COLORS[-2] = COLOR_G
PORT_COLORS[-1] = COLOR_Y

ICON_DATA = "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAFiUlEQVR4nO3dP24UZxjAYRv5HFut3FLQuktBjsIJkqtwlFCkc0tBu3KVixBRICES4/3zfTsz/j1PidB6MHp/+854Z3y72+1ugKY3Sx8AsBwBgDABgDABgDABgDABgDABgDABgDABgDABgDABgLC7mxW7v7//uvQxwAiHw+H2ZoVu13QzkIGn4rCSICweAENP3WHBGCwWAIMPy4fg6gEw+LCeEFz1pwCGH9Y1J1fZAM79Bz09PY0/GFjAfr9f5TYwPQCnDr+h57XbnxiDmRGYGoBjh9/QU7U/MgazIjAtAMcMv8GH40MwIwJTLgIafjjNMW+GMy4ODt8AXjpI7/pw2TYwchMYugEYfrjcS2+SIzeBYQEw/LC9CFzlg0DWfljn3AwJwK9qZPjhfL+anxFbwMUBMPyw3Qh4IhCEXRQA7/6w7S1gygbgvB+2MVdnB8CtvbAe587j8A3Auz/MM3q+XASEsLMCYP2H9TlnLoduANZ/mG/knDkFgDABgLA3o84zrP9wPc/N26nXAWwAECYAECYAECYAECYAECYAECYAECYAECYAECYAECYAEHZ3s3IPHx+WPoRNefzwOPX1P717O/X1X5v3n7/crJkNAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMLu6s+4m/0Mwmsf/2t7xt3oZxCu/Rl912YDgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgDABgLC7pQ/gtXv4+DDkdR4/PA55HfiRDQDCBADCBADCXAPYiH/+/uuqX2/32+9X/XoswwYAYQIAYQIAYQIAYQIAYQIAYQIAYQIAYQIAYQIAYQIAYe4F2IhLP5t/7XsJ2AYbAIQJAIQJAIS5BjCZZ/mxZjYACBMACBMACBMACBMACBMACBMACBMACBMACPNJQIb79O6t7+pG2AAgTAAgTAAgzDUAxj9B6I8/fVc3wgYAYQIAYQIAYQIAYQIAYQIAYQIAYQIAYQIAYQIAYQIAYe4FiLj0twufxPMANsMGAGECAGECAGGuATDc+89fhr2W5wvOZQOAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAMAGAML8Y5CePHx6X+Z9g+i8Z4b9sABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABAmABB2cgAOh8Pt//35fr8fckDAy56bt+fm8zk2AAgTAAgbGgCnATDfyDk7KwCnnmcA850zl04BIGx4AJwGwDyj5+vsADgNgPU4dx6nnALYAmAbc/VmVnVEAMb51Txdso27CAhhFwfAFgDbfPcftgGIAGxv+K92CuB6AKxzboYF4KUaiQAc76V5GfVj+KEbgAjAdob/m9vdbncz2v39/deX/s7T09Pwrwtbtj9i5R/9Abwp1wCOOUinBLDs8E/bAE7ZBL6xDVC1P/JC36yP3k8NwCkR+E4MeO32J17dn3nfzfQAnBOB78SA12J/5o/0Zt90d5UAXBoCqDlc6aE7V70XwC3EsK45ueoG8CPbACz/BrlYAL4TAuoOCz5jc/EA/EgMqDis5MG6qwrAzwSB1+KwkoHfVACAuTwRCMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAMIEAG66/gVZ2SkgdHd/oAAAAABJRU5ErkJggg=="
# --- Existing Helpers & Serial Connections ---
def select_and_connect_port(baud_rate=BAUD_RATE):
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        raise IOError(
            "❌ Nenhuma porta serial detectada no computador. Verifique conexões USB."
        )

    matching_ports = []
    for port in ports:
        desc = (port.description or "").lower()
        mfg = (port.manufacturer or "").lower()
        dev = (port.device or "").lower()
        if any(
            kw in desc or kw in mfg or kw in dev for kw in ARDUINO_KEYWORDS
        ):
            matching_ports.append(port)

    selected_port_name = None
    if len(matching_ports) == 1:
        auto_port = matching_ports[0]
        print(
            f"🤖 Dispositivo auto-detectado: {auto_port.device} ({auto_port.description})"
        )
        selected_port_name = auto_port.device
    else:
        print("\n--- Portas Serial Disponíveis ---")
        for idx, port in enumerate(ports):
            match_tag = " (Sugestão)" if port in matching_ports else ""
            print(f" [{idx + 1}] {port.device} - {port.description}{match_tag}")
        while True:
            try:
                choice = int(input("\nSelecione o número da porta para conectar: ")) - 1
                if 0 <= choice < len(ports):
                    selected_port_name = ports[choice].device
                    break
            except ValueError:
                pass
            print("Seleção inválida.")

    print(f"Conectando com {selected_port_name} a {baud_rate} baud...")
    ser = serial.Serial(selected_port_name, baud_rate, timeout=1)
    time.sleep(2)
    print("✅ Conexão estabelecida com sucesso!")
    return ser


def process_packet(payload):
    checksum = 0
    for byte in payload[0:6]:
        checksum ^= byte
    if checksum != payload[6]:
        print("Erro de checksum! Pacote descartado.")
        return None

    data_bytes = payload[1:6]
    pin_states = []
    for i in range(NUM_PINS):
        byte_idx = i // 8
        bit_idx = i % 8
        is_on = bool((data_bytes[byte_idx] >> bit_idx) & 1)
        pin_states.append(is_on)
    return pin_states


def get_time(use_deciseconds=True):
    if use_deciseconds:
        return datetime.now().strftime("%Y-%m-%d--%Hh%Mm%S,%f")[:-5]+'s'
    else:
        return datetime.now().strftime("%Y-%m-%d--%Hh%Mm%Ss")

def comp_time(t1, t2, res=1):
    return [f'{(int(val) - int(t2))/1000:.{res}f}' for val in t1]

def get_unix_time_ms():
    return time.time_ns() // 1000000


def print_active_pins(pins, message_count):
    active_count = sum(pins)
    pins = ''.join([('1' if pin==True else '0') for pin in pins])
    pin_blocks = ' '.join([pins[i:i+10] for i in range(0, len(pins), 10)])
    print(f"[{message_count}] Pins ativos: {active_count}/40  |  {pin_blocks}")


# --- Logic Classes ---
class Reader:

    def __init__(self, gtr_pin, swt_pin, direc):
        self.gtr_pin = gtr_pin
        self.swt_pin = swt_pin
        self.port_num = int(gtr_pin // 2 + 1)

        self.gtr_reads = []
        self.swt_reads = []
        self.gtr_switch_times = {}

        self.enabled = False
        self.directory = Path(direc)
        self.current_gtr_state = False

    def read_from_packet(self, pin_data, unix_time):
        nxt_swt_reads = pin_data[self.swt_pin]
        nxt_gtr_reads = pin_data[self.gtr_pin]
        self.swt_reads.append(nxt_swt_reads)
        self.current_gtr_state = nxt_gtr_reads

        self.state_machine(nxt_gtr_reads, unix_time)

    def run_enable(self, unix_time=None):
        if unix_time is None:
            unix_time = get_unix_time_ms()
        self.enabled = True
        self.gtr_reads = []
        self.gtr_switch_times = {unix_time: "LIGADO"}

    def run_disable(self):
        self.enabled = False

    def run_reset(self, unix_time=None):
        if unix_time is None:
            unix_time = get_unix_time_ms()
        self.gtr_switch_times[unix_time] = "RESET"
        self.save_port_data(temp=False, filetype="xlsx", use_deciseconds=False)
        self.gtr_reads = []
        self.gtr_switch_times = {unix_time: "RESET"}

    def state_machine(self, nxt_gtr_reads, unix_time):
        n_set = 2
        n_dis = 10
        set_reset_check = (self.swt_reads[-n_set:].count(True) == n_set) and (
            not self.swt_reads[-(n_set+1)] if len(self.swt_reads) >= (n_set+1) else False
        )
        disable_check = (self.swt_reads[-n_dis:].count(True) == n_dis) and (
            not self.swt_reads[-(n_dis+1)] if len(self.swt_reads) >= (n_dis+1) else False
        )

        if self.enabled and disable_check:
            self.run_disable()
        elif not self.enabled and set_reset_check:
            self.run_enable(unix_time)
        elif self.enabled and set_reset_check:
            self.run_reset(unix_time)

        if self.enabled:
            self.gtr_reads.append(nxt_gtr_reads)
            if len(self.gtr_reads) >= 2:
                if self.gtr_reads[-1] != self.gtr_reads[-2]:
                    self.gtr_switch_times[unix_time] = (
                        "On" if nxt_gtr_reads else "Off"
                    )

    def save_port_data(self, timestamp=None, temp=False, filetype='csv', use_deciseconds=True):
        if not self.gtr_switch_times:
            return None

        if timestamp is None:
            timestamp = get_time(use_deciseconds)

        port_name = f"port-{self.port_num}--{timestamp}"
        keys_list = list(self.gtr_switch_times.keys())
        port_txt_l1 = ",".join(comp_time(keys_list, keys_list[0]))
        port_txt_l2 = ",".join(self.gtr_switch_times.values())
        port_txt = f"{port_txt_l1}\n{port_txt_l2}"

        save_dir = self.directory / "medicoes"
        if temp:
            save_dir = save_dir / ".temp"

        save_dir.mkdir(parents=True, exist_ok=True)
        if filetype in ('csv', '.csv'):
            with open(save_dir / f"{port_name}.csv", "w", encoding="utf-8") as f:
                f.write(port_txt)
        elif filetype in ('xlsx', '.xlsx'):
            df = pd.read_csv(StringIO(port_txt))
            df.to_excel(save_dir / f"{port_name}.xlsx", index=False)
        else:
            raise AssertionError("Variável 'filetype' deve ser 'csv' ou 'xlsx'.")
        return port_txt


class DataProcessor:

    def __init__(self, directory):
        self.directory = Path(directory)
        self.readers = [
            Reader(port, port + 1, self.directory)
            for port in range(0, NUM_PINS, 2)
        ]
        self.processed_files = set()
        (self.directory / "medicoes" / ".temp").mkdir(
            parents=True, exist_ok=True
        )

    def process_data(self, files=None):
        if files is None:
            data_dir = self.directory / "data"
            files = sorted(
                [
                    f
                    for f in data_dir.glob("*.bin")
                    if f not in self.processed_files
                ],
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
            reader.save_port_data(timestamp, temp=True)


# --- GUI Implementation ---
class PortCard(tk.LabelFrame):

    def __init__(self, parent, reader_instance, border_color):
        self.reader = reader_instance
        super().__init__(
            parent,
            text=f" Porta {self.reader.port_num} ",
            font=("Arial", 10, "bold"),
            highlightbackground=border_color,
            highlightcolor=border_color,
            highlightthickness=3,
            bd=1,
            relief="solid",
            padx=10,
            pady=8,
        )

        # GTR Reading Label (ON / OFF)
        self.status_label = tk.Label(
            self, text="OFF", font=("Arial", 11, "bold"), fg="gray"
        )
        self.status_label.pack(anchor="e", pady=(0, 4))

        # Toggle Button
        self.enable_btn = tk.Button(
            self,
            text="Enable",
            width=8,
            command=self.gui_toggle_enable,
            bg="#e0e0e0",
            relief="groove",
        )
        self.enable_btn.pack(pady=2)

        # Reset Button
        self.reset_btn = tk.Button(
            self,
            text="Reset",
            width=8,
            command=self.gui_trigger_reset,
            bg="#e0e0e0",
            relief="groove",
        )
        self.reset_btn.pack(pady=2)

    def gui_toggle_enable(self):
        """User clicked the Enable/Disable button in GUI."""
        if self.reader.enabled:
            self.reader.run_reset()
            self.reader.run_disable()
        else:
            self.reader.run_enable()
        self.refresh_ui()

    def gui_trigger_reset(self):
        """User clicked the Reset button in GUI."""
        if self.reader.enabled:
            self.reader.run_reset()
            self.refresh_ui()

    def refresh_ui(self):
        """Syncs the card visual components with current Reader values."""
        # 1. Update GTR state label
        if self.reader.current_gtr_state:
            self.status_label.config(text="ON", fg="black")
        else:
            self.status_label.config(text="OFF", fg="gray")

        # 2. Update toggle button appearance & Reset button interaction
        if self.reader.enabled:
            self.enable_btn.config(text="Disable", bg="#d9534f", fg="white")
            # Enable Reset button
            self.reset_btn.config(
                state="normal", bg="#e0e0e0", fg="black", cursor="hand2"
            )
        else:
            self.enable_btn.config(text="Enable", bg="#e0e0e0", fg="black")
            # Gray-out and disable Reset button
            self.reset_btn.config(
                state="disabled",
                bg="#F8F8F8",
                disabledforeground="#A1A1A1",
                cursor="",
            )


class AppGUI(tk.Tk):

    def __init__(self, data_processor, serial_conn):
        super().__init__()
        self.title("Timer Timer - Monitor e controle de portas")
        self.configure(bg="#e6e6e6")

        try:
            # Load directly from embedded string data
            icon_img = tk.PhotoImage(data=ICON_DATA)
            self.iconphoto(False, icon_img)
        except Exception as e:
            print(f"Icone não pode ser carregado: {e}")

        self.processor = data_processor
        self.ser = serial_conn
        self.cards = []
        self.is_running = True

        # Render grid of 'ncols' columns x '20//ncols' rows
        ncols = 5
        grid_frame = tk.Frame(self, bg="#D0D0D0", padx=10, pady=10)
        grid_frame.pack()

        for idx, reader in enumerate(self.processor.readers):
            row = idx // ncols
            col = idx % ncols
            color = PORT_COLORS[idx % len(PORT_COLORS)]

            card = PortCard(grid_frame, reader, border_color=color)
            card.grid(row=row, column=col, padx=6, pady=6)
            self.cards.append(card)

        # Start thread reading serial
        self.reader_thread = threading.Thread(
            target=self.serial_listen_loop, daemon=True
        )
        self.reader_thread.start()

        # GUI update loop (Runs every 100ms)
        self.poll_gui_updates()

        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def serial_listen_loop(self):
        cwd = self.processor.directory
        pending_files = []

        message_count = 0
        while self.is_running:
            try:
                byte_in = self.ser.read(1)
                if not byte_in:
                    continue

                if byte_in[0] == HEADER:
                    remaining_bytes = self.ser.read(6)
                    if len(remaining_bytes) == 6:
                        message_count += 1
                        read_time_ms = get_unix_time_ms()
                        full_packet = bytearray([HEADER]) + remaining_bytes
                        pins = process_packet(full_packet)

                        if pins is not None:
                            filepath = cwd / "data" / f"{read_time_ms}.bin"
                            with open(filepath, "wb") as f:
                                f.write(full_packet)

                            if PRINT_ACTIVE_PINS:
                                print_active_pins(pins, message_count)

                            pending_files.append(filepath)

                if pending_files:
                    self.processor.process_data(pending_files)
                    pending_files = []

            except serial.SerialException:
                break
            except Exception as e:
                print(f"Erro lendo a stream serial: {e}")

    def poll_gui_updates(self):
        """Periodically refreshes the UI cards to mirror hardware state machines."""
        for card in self.cards:
            card.refresh_ui()

        if self.is_running:
            self.after(100, self.poll_gui_updates)

    def on_close(self):
        self.is_running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.destroy()


# --- Main Entry Point ---
def main():
    cwd = Path.cwd()
    (cwd / "data").mkdir(parents=True, exist_ok=True)
    (cwd / "medicoes").mkdir(parents=True, exist_ok=True)

    print(r"""
===============================================================================
  _______ _____ __  __ ______ _____     _______ _____ __  __ ______ _____  
 |__   __|_   _|  \/  |  ____|  __ \   |__   __|_   _|  \/  |  ____|  __ \ 
    | |    | | | \  / | |__  | |__) |     | |    | | | \  / | |__  | |__) |
    | |    | | | |\/| |  __| |  _  /      | |    | | | |\/| |  __| |  _  / 
    | |   _| |_| |  | | |____| | \ \      | |   _| |_| |  | | |____| | \ \ 
    |_|  |_____|_|  |_|______|_|  \_\     |_|  |_____|_|  |_|______|_|  \_\
    
===============================================================================
""")

    # Establish Serial
    ser = select_and_connect_port(BAUD_RATE)

    # Initialize Processor and GUI
    data_processor = DataProcessor(cwd)
    app = AppGUI(data_processor, ser)
    app.mainloop()


if __name__ == "__main__":
    main()