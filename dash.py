import os
import subprocess
import re
import random
from collections import deque
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Label, Input, DataTable, TabbedContent, TabPane, ProgressBar
from textual.containers import Grid, VerticalScroll
from textual_plotext import PlotextPlot

class PingGraph(Static):
    target_ip = None

    def compose(self) -> ComposeResult:
        yield Label("=== TARGET PING (MS) ===", id="ping-title")
        yield Input(placeholder="KETIK IP LALU ENTER...", id="ping-input")
        yield PlotextPlot(id="ping-plot")
        yield Label("LAST: 0.0MS | MIN: 0.0MS | MAX: 0.0MS | AVG: 0.0MS", id="ping-stats")

    def on_mount(self) -> None:
        self.ping_data = None
        self.set_interval(1.0, self.update_ping)

    @on(Input.Submitted, "#ping-input")
    def ganti_ip(self, event: Input.Submitted) -> None:
        self.target_ip = event.value
        if self.ping_data is None:
            self.ping_data = deque([0] * 30, maxlen=30)
        else:
            self.ping_data.clear()
            self.ping_data.extend([0] * 30)

        self.update_plot()
        self.query_one("#ping-stats", Label).update("LAST: 0.0MS | MIN: 0.0MS | MAX: 0.0MS | AVG: 0.0MS")
        self.app.notify(f"TARGET PING DIUBAH KE {self.target_ip}", title="PING UPDATE", severity="information")

    def update_plot(self) -> None:
        if self.ping_data is None: return
        plot_widget = self.query_one("#ping-plot", PlotextPlot)
        plt = plot_widget.plt
        plt.clear_figure()
        plt.plot(list(self.ping_data), color="blue")
        plt.canvas_color("black")
        plt.axes_color("black")
        plt.ticks_color("green")
        plt.frame(False)
        plt.title("")
        plot_widget.refresh()

    def update_ping(self) -> None:
        if self.target_ip is None or self.ping_data is None: return
        try:
            result = subprocess.run(["ping", "-c", "1", "-W", "1", self.target_ip], capture_output=True, text=True)
            match = re.search(r'time=([\d\.]+)', result.stdout)
            ms = float(match.group(1)) if match else 0.0
        except Exception:
            ms = 0.0

        self.ping_data.append(ms)
        valid_data = [x for x in self.ping_data if x > 0]
        if valid_data:
            stats_text = f"LAST: {ms:.1f}MS | MIN: {min(valid_data):.1f}MS | MAX: {max(valid_data):.1f}MS | AVG: {(sum(valid_data)/len(valid_data)):.1f}MS"
        else:
            stats_text = "LAST: 0.0MS | MIN: 0.0MS | MAX: 0.0MS | AVG: 0.0MS"

        self.query_one("#ping-stats", Label).update(stats_text)
        self.update_plot()

class NetworkInfo(Static):
    def compose(self) -> ComposeResult:
        yield Label("=== INFO INTERFACE & IP ===", id="net-title")
        yield Label("MENCARI INFO...", id="net-info-text")
        yield Label("=== DAFTAR PORT TERBUKA ===", id="port-title")
        yield DataTable(id="port-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("PROTO", "LOKAL IP", "PORT")
        self.update_info()
        self.set_interval(5.0, self.update_info)

    def update_info(self) -> None:
        try:
            route_out = subprocess.run(["ip", "route", "get", "1.1.1.1"], capture_output=True, text=True).stdout
            ip_match = re.search(r'src ([\d\.]+)', route_out)
            dev_match = re.search(r'dev (\w+)', route_out)
            main_ip = ip_match.group(1) if ip_match else "OFFLINE"
            main_dev = dev_match.group(1) if dev_match else "-"
            info_text = f"INTERFACE AKTIF : {main_dev}\nIP ADDRESS LOKAL: {main_ip}"
        except Exception:
            info_text = "GAGAL MENGAMBIL INFO JARINGAN"

        self.query_one("#net-info-text", Label).update(info_text)

        try:
            ss_out = subprocess.run(["ss", "-tuln"], capture_output=True, text=True).stdout
            lines = ss_out.split('\n')[1:]
            table = self.query_one(DataTable)
            table.clear()
            for line in lines:
                if not line.strip(): continue
                parts = line.split()
                if len(parts) >= 5:
                    proto = parts[0].upper()
                    local_addr_port = parts[4]
                    if local_addr_port.rfind(':') != -1:
                        addr = local_addr_port[:local_addr_port.rfind(':')]
                        port = local_addr_port[local_addr_port.rfind(':')+1:]
                    else:
                        addr = local_addr_port
                        port = "-"
                    if addr == "*": addr = "0.0.0.0"
                    if addr == "[::]": addr = "IPv6"
                    table.add_row(proto, addr, port)
        except Exception:
            pass

class GlobeAnimation(Static):
    frames = [
        "     ⢀⣀⣤⠤⠶⠶⠶⠤⣤⣀⡀     \n   ⣠⠖⠋⠁⢀⣀⡀⠀⠀⠀⠀⠈⠙⠲⣄   \n  ⢸⡇⣠⣾⣿⣿⣄⠀⠀⠀⠀⠀⢸⡇  \n  ⢸⡇⢿⣿⣿⣿⡿⠀⠀⠀⠀⠀⢸⡇  \n   ⠈⠳⣄⠈⠙⠛⠋⠀⠀⠀⠀⠀⣠⠞⠁   \n     ⠈⠉⠛⠒⠒⠒⠒⠒⠛⠉⠁     ",
        "     ⢀⣀⣤⠤⠶⠶⠶⠤⣤⣀⡀     \n   ⣠⠖⠋⠁⠀⠀⢀⣀⡀⠀⠀⠀⠈⠙⠲⣄   \n  ⢸⡇⠀⠀⣠⣾⣿⣿⣄⠀⠀⠀⢸⡇  \n  ⢸⡇⠀⠀⢿⣿⣿⣿⡿⠀⠀⠀⢸⡇  \n   ⠈⠳⣄⠀⠀⠈⠙⠛⠋⠀⠀⠀⣠⠞⠁   \n     ⠈⠉⠛⠒⠒⠒⠒⠒⠛⠉⠁     ",
        "     ⢀⣀⣤⠤⠶⠶⠶⠤⣤⣀⡀     \n   ⣠⠖⠋⠁⠀⠀⠀⠀⢀⣀⡀⠀⠈⠙⠲⣄   \n  ⢸⡇⠀⠀⠀⠀⣠⣾⣿⣿⣄⠀⢸⡇  \n  ⢸⡇⠀⠀⠀⠀⢿⣿⣿⣿⡿⠀⢸⡇  \n   ⠈⠳⣄⠀⠀⠀⠀⠈⠙⠛⠋⠀⣠⠞⠁   \n     ⠈⠉⠛⠒⠒⠒⠒⠒⠛⠉⠁     ",
        "     ⢀⣀⣤⠤⠶⠶⠶⠤⣤⣀⡀     \n   ⣠⠖⠋⠁⠀⠀⠀⠀⠀⢀⣀⠈⠙⠲⣄   \n  ⢸⡇⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣄⠀⠀⢸⡇  \n  ⢸⡇⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⡿⠀⠀⢸⡇  \n   ⠈⠳⣄⠀⠀⠀⠀⠀⠀⠈⠙⠛⣠⠞⠁   \n     ⠈⠉⠛⠒⠒⠒⠒⠒⠛⠉⠁     ",
        "     ⢀⣀⣤⠤⠶⠶⠶⠤⣤⣀⡀     \n   ⣠⠖⠋⠁⡀⠀⠀⠀⠀⠀⠀⠈⠙⠲⣄   \n  ⢸⡇⣿⣄⠀⠀⠀⠀⠀⠀⣠⣾⢸⡇  \n  ⢸⡇⣿⡿⠀⠀⠀⠀⠀⠀⢿⣿⢸⡇  \n   ⠈⠳⣄⠋⠀⠀⠀⠀⠀⠀⠈⠙⣠⠞⠁   \n     ⠈⠉⠛⠒⠒⠒⠒⠒⠛⠉⠁     ",
        "     ⢀⣀⣤⠤⠶⠶⠶⠤⣤⣀⡀     \n   ⣠⠖⠋⠁⣀⡀⠀⠀⠀⠀⠀⠈⠙⠲⣄   \n  ⢸⡇⣿⣿⣄⠀⠀⠀⠀⠀⠀⣠⢸⡇  \n  ⢸⡇⣿⣿⡿⠀⠀⠀⠀⠀⠀⢿⢸⡇  \n   ⠈⠳⣄⠛⠋⠀⠀⠀⠀⠀⠀⠈⣠⠞⠁   \n     ⠈⠉⠛⠒⠒⠒⠒⠒⠛⠉⠁     "
    ]

    def compose(self) -> ComposeResult:
        yield Label("=== GLOBAL NODE ===", id="globe-title")
        yield Label(self.frames[0], id="globe-view")

    def on_mount(self) -> None:
        self.index = 0
        self.set_interval(0.4, self.update_globe)

    def update_globe(self) -> None:
        self.index = (self.index + 1) % len(self.frames)
        lat = f"LAT : {random.uniform(-90, 90):.4f}"
        lon = f"LON : {random.uniform(-180, 180):.4f}"
        sat = f"SAT : {random.randint(4, 12)} TERKONEKSI"
        view = f"{self.frames[self.index]}\n\n{lat}\n{lon}\n{sat}"
        self.query_one("#globe-view", Label).update(view)

class SystemctlMenu(Static):
    apache_service = "httpd"

    def on_mount(self) -> None:
        try:
            result = subprocess.run(["systemctl", "list-unit-files", "apache2.service"], capture_output=True, text=True)
            if "apache2.service" in result.stdout:
                self.apache_service = "apache2"
        except:
            pass

        self.query_one("#btn-start", Button).label = f"▶ START {self.apache_service.upper()}"
        self.query_one("#btn-stop", Button).label = f"■ STOP {self.apache_service.upper()}"
        self.query_one("#btn-restart", Button).label = f"↻ RESTART {self.apache_service.upper()}"
        self.query_one("#btn-status", Button).label = f"ℹ STATUS {self.apache_service.upper()}"

    def compose(self) -> ComposeResult:
        yield Label("=== KONTROL SYSTEMCTL ===", id="sys-title")
        with VerticalScroll(id="sys-scroll"):
            yield Button("▶ START HTTPD", id="btn-start", variant="success")
            yield Button("■ STOP HTTPD", id="btn-stop", variant="error")
            yield Button("↻ RESTART HTTPD", id="btn-restart", variant="warning")
            yield Button("ℹ STATUS HTTPD", id="btn-status", variant="primary")

    @on(Button.Pressed)
    def execute_command(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        command = []
        # Sekarang command-nya pake variabel dinamis self.apache_service
        if button_id == "btn-start": command = ["sudo", "systemctl", "start", self.apache_service]
        elif button_id == "btn-stop": command = ["sudo", "systemctl", "stop", self.apache_service]
        elif button_id == "btn-restart": command = ["sudo", "systemctl", "restart", self.apache_service]
        elif button_id == "btn-status": command = ["systemctl", "is-active", self.apache_service]

        if command:
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode == 0:
                    self.app.notify(f"BERHASIL: {' '.join(command)}", title="SUKSES", severity="information")
                else:
                    self.app.notify(f"GAGAL/TIDAK AKTIF: {' '.join(command)}\n{result.stderr}", title="INFO", severity="error")
            except Exception as e:
                self.app.notify(f"SYSTEM ERROR: {e}", title="FATAL", severity="error")

class WebLogTracker(Static):
    # Default path log untuk Arch Linux
    log_path = "/var/log/httpd/access_log"

    def on_mount(self) -> None:
        # DETEKSI OTOMATIS: Cek path log Ubuntu/Debian
        if os.path.exists("/var/log/apache2/access.log"):
            self.log_path = "/var/log/apache2/access.log"

        self.set_interval(2.0, self.update_log)

    def compose(self) -> ComposeResult:
        yield Label("=== LIVE WEB LOG ===", id="log-title")
        with VerticalScroll(id="log-scroll"):
            yield Label("MENUNGGU LOG...", id="log-content")

    def update_log(self) -> None:
        try:
            # Sekarang tail baca log dinamis sesuai OS
            result = subprocess.run(["sudo", "tail", "-n", "8", self.log_path], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                log_text = result.stdout
            else:
                log_text = f"WEB SERVER MATI ATAU BELUM ADA AKSES.\n(Memantau Path: {self.log_path})"
        except Exception as e:
            log_text = f"ERROR MEMBACA LOG: {e}\nPastikan path log ada di mesin ini."

        self.query_one("#log-content", Label).update(log_text)
        scroll = self.query_one("#log-scroll", VerticalScroll)
        scroll.scroll_end(animate=False)

class WebPerfMonitor(Static):
    def compose(self) -> ComposeResult:
        yield Label("=== LOCALHOST HEALTH ===", id="perf-title")
        yield Label("SCANNING...", id="perf-content")

    def on_mount(self) -> None:
        self.set_interval(3.0, self.update_perf)

    def update_perf(self) -> None:
        try:
            cmd = ["curl", "-o", "/dev/null", "-s", "-w", "%{http_code}|%{size_download}|%{time_total}", "http://127.0.0.1"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                data = result.stdout.split('|')
                status = data[0]
                size_bytes = float(data[1])
                time_sec = float(data[2])
                if size_bytes > 1024 * 1024: size_str = f"{size_bytes / (1024*1024):.2f} MB"
                elif size_bytes > 1024: size_str = f"{size_bytes / 1024:.2f} KB"
                else: size_str = f"{size_bytes:.0f} B"
                time_ms = time_sec * 1000
                color = "green" if status == "200" else "red"
                text = f"[{color}]STATUS CODE: {status}[/]\n\nPAGE SIZE  : {size_str}\n\nRESP. TIME : {time_ms:.0f} ms"
            else:
                text = "[red]SERVER OFFLINE\n(HTTPD MATI)[/]"
        except Exception:
            text = "[red]ERROR / TIMEOUT[/]"
        self.query_one("#perf-content", Label).update(text)

class SystemHardware(Static):
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="hw-container"):
            yield Label("=== CPU USAGE (%) ===", classes="hw-title")
            yield ProgressBar(total=100, id="cpu-bar", show_eta=False)

            yield Label("=== RAM USAGE (MB) ===", classes="hw-title")
            yield ProgressBar(total=100, id="ram-bar", show_eta=False)

            yield Label("=== SWAP USAGE (MB) ===", classes="hw-title")
            yield ProgressBar(total=100, id="swap-bar", show_eta=False)

            yield Label("=== CPU TEMP (°C) ===", classes="hw-title")
            yield ProgressBar(total=100, id="temp-bar", show_eta=False)

            yield Label("MENGAMBIL DATA SENSOR...", id="hw-details")

    def on_mount(self) -> None:
        self.set_interval(2.0, self.update_hw)

    def update_hw(self) -> None:
        try:
            free_out = subprocess.run(["free", "-m"], capture_output=True, text=True).stdout.splitlines()
            mem_data = free_out[1].split()
            swap_data = free_out[2].split()

            ram_total = float(mem_data[1])
            ram_used = float(mem_data[2])
            ram_pct = (ram_used / ram_total) * 100

            swap_total = float(swap_data[1])
            swap_used = float(swap_data[2])
            swap_pct = (swap_used / swap_total) * 100 if swap_total > 0 else 0
        except Exception:
            ram_pct, swap_pct, ram_total, ram_used, swap_used = 0, 0, 0, 0, 0

        # 2. AMBIL CPU
        try:
            top_out = subprocess.run(["top", "-bn1"], capture_output=True, text=True).stdout
            match = re.search(r'(\d+\.\d+)\s+id', top_out)
            cpu_pct = 100.0 - float(match.group(1)) if match else 0.0
        except Exception:
            cpu_pct = 0.0

        # 3. AMBIL SUHU DARI SENSOR KERNEL
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                # File ini ngeluarin angka dalam millidegree (misal 45000 = 45°C)
                temp_c = float(f.read().strip()) / 1000.0
        except Exception:
            temp_c = 0.0

        # Batasin bar mentok di 100°C aja biar grafiknya gak error
        bar_temp = min(temp_c, 100.0)

        # UPDATE PROGRESS BAR
        self.query_one("#cpu-bar", ProgressBar).update(progress=cpu_pct)
        self.query_one("#ram-bar", ProgressBar).update(progress=ram_pct)
        self.query_one("#swap-bar", ProgressBar).update(progress=swap_pct)
        self.query_one("#temp-bar", ProgressBar).update(progress=bar_temp)

        # UPDATE DETAIL TEKS DI BAWAH
        details = f"[cyan]CPU:[/] {cpu_pct:.1f}%  |  [cyan]RAM:[/] {ram_used:.0f}/{ram_total:.0f} MB  |  [cyan]SWAP:[/] {swap_used:.0f} MB  |  [red]SUHU:[/] {temp_c:.1f}°C"
        self.query_one("#hw-details", Label).update(details)

# ==========================================
# APLIKASI UTAMA
# ==========================================

class DashboardApp(App):
    CSS = """
    TabbedContent { height: 1fr; }
    TabPane { height: 1fr; padding: 0; }

    #main-grid {
        grid-size: 4 3;
        grid-columns: 1fr 1fr 1fr 1fr;
        grid-rows: 1fr 1fr 0.8fr;
        height: 1fr;
        width: 1fr;
        background: #111111;
    }

    #ping-panel { column-span: 1; row-span: 2; border: solid #7a04eb; height: 100%; padding: 1; }
    #ping-title { text-align: center; width: 100%; text-style: bold; color: #7a04eb; padding-bottom: 1; }
    #ping-input { width: 100%; margin-bottom: 1; border: solid #7a04eb; color: #7a04eb; }
    #ping-plot { width: 100%; height: 1fr; color: #7a04eb; }
    #ping-stats { width: 100%; text-align: center; color: #7a04eb; text-style: bold; margin-top: 1; }

    #info-panel { column-span: 2; row-span: 2; border: solid #00aaff; height: 100%; padding: 1; }
    #net-title, #port-title { text-align: center; width: 100%; text-style: bold; color: #00aaff; padding-bottom: 1; }
    #net-info-text { text-align: center; width: 100%; color: white; padding-bottom: 1; }
    #port-table { height: 1fr; width: 100%; }

    #globe-panel { column-span: 1; row-span: 1; border: solid #ff00a0; height: 100%; padding: 1; }
    #globe-title { text-align: center; width: 100%; text-style: bold; color: #ff00a0; padding-bottom: 1; }
    #globe-view { text-align: center; width: 100%; color: #ff00a0; }

    #sys-panel { column-span: 1; row-span: 1; background: $surface-darken-3; border: solid red; height: 100%; padding: 1; }
    #sys-title { text-align: center; width: 100%; text-style: bold; padding-bottom: 1; color: auto; }
    Button { width: 100%; margin-bottom: 1; }

    #log-panel { column-span: 2; row-span: 1; border: solid magenta; height: 100%; padding: 1; }
    #log-title { text-align: center; width: 100%; text-style: bold; color: magenta; padding-bottom: 1; }
    #log-content { color: #ff00ff; width: 100%; }

    #perf-panel { column-span: 2; row-span: 1; border: solid cyan; height: 100%; padding: 1; }
    #perf-title { text-align: center; width: 100%; text-style: bold; color: cyan; padding-bottom: 1; }
    #perf-content { text-align: center; width: 100%; color: white; margin-top: 1; }

    /* STYLING TAB 2: BIKIN KE TENGAH SEMPURNA */
    #hardware-panel {
        height: 1fr;
        width: 1fr;
        border: solid orange;
        padding: 2 4;
        background: #0a0a0a;
        /* DUA BARIS INI KUNCI BUAT BIKIN CENTER DI TEXTUAL */
        align: center middle;
    }

    #hw-container {
        height: auto; /* Biar tingginya pas ngikutin isi */
        width: 70%; /* Biar lebarnya dibatasin, gak terlalu melar */
        border: solid #333333; /* Kasih bingkai tipis biar estetik */
        padding: 1 3;
    }

    .hw-title {
        text-align: left;
        width: 100%;
        text-style: bold;
        color: orange;
        margin-top: 1;
        margin-bottom: 1;
    }
    #hw-details {
        text-align: center;
        width: 100%;
        text-style: bold;
        margin-top: 2;
        padding: 1;
        border: dashed yellow;
    }

    ProgressBar { width: 100%; margin-bottom: 1; }
    ProgressBar > .progress--bar { color: orange; }

    /* GANTI WARNA BAR SUHU JADI MERAH BIAR KERASAN BAHAYANYA */
    #temp-bar > .progress--bar { color: red; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="tab-dash"):
            with TabPane("🌐 DASHBOARD", id="tab-dash"):
                with Grid(id="main-grid"):
                    yield PingGraph(id="ping-panel")
                    yield NetworkInfo(id="info-panel")
                    yield GlobeAnimation(id="globe-panel")
                    yield SystemctlMenu(id="sys-panel")
                    yield WebLogTracker(id="log-panel")
                    yield WebPerfMonitor(id="perf-panel")

            with TabPane("💻 HARDWARE MATRIX", id="tab-hw"):
                yield SystemHardware(id="hardware-panel")

        yield Footer()

if __name__ == "__main__":
    app = DashboardApp()
    app.title = "ArchNet Dash"
    app.run()
