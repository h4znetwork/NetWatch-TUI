# 🌐 NetWatch TUI (Terminal Dev Dashboard)

A cyberpunk-themed, terminal-based dashboard for local web development, network monitoring, and system resource tracking. Built with Python and Textual.

## ✨ Features
- **📡 Dynamic Ping Monitor:** Real-time ping graph tracking using Braille ASCII blocks.
- **🌍 Global Node:** Aesthetic rotating Braille globe with randomized satellite telemetry.
- **🛡️ Network Scanner:** Auto-detects active network interface, local IP, and scans open ports in real-time via `ss`.
- **⚙️ Local Server Controller:** Start, stop, and restart your local web server (`httpd` or `apache2`) with a single click. (Auto-detects distro service).
- **📜 Live Web Log:** Real-time tracking of Apache access logs for seamless web development debugging.
- **🩺 Localhost Health:** Scans localhost performance including HTTP Status Code, Page Size, and Response Time.
- **💻 Hardware Matrix:** Dedicated tab for monitoring CPU, RAM, SWAP usage, and CPU Temperature in real-time.

## 🚀 Installation & Setup

It is highly recommended to use a Python Virtual Environment (`env`) to avoid conflicts with your system packages.

**1. Clone the repository**
git clone [https://github.com/USERNAME_LO/NetMatrix-TUI.git](https://github.com/USERNAME_LO/NetMatrix-TUI.git)
cd NetMatrix-TUI

**2. How to run the script**
1. Create and activate a Virtual Environment :
command :   - python -m venv env
            - source env/bin/activate
            
2. Install dependencies :
command :   - pip install -r requirements.txt

3. Run the script :
command :   - sudo env/bin/python dash.py 
(To ensure the systemctl control and live log reading work perfectly, run the script using sudo with the virtual environment's Python)
