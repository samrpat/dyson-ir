# -----------------------------
# Dyson AM09 IR Blaster Pico W
# Full IR + Web UI + Cooldowns
# -----------------------------

import network
import socket
from machine import Pin, PWM
import time

# -----------------------------
# Wi-Fi Setup
# -----------------------------
SSID = "YOURWIFI"
PASSWORD = "YOURPASSWORD"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting WiFi...")
while not wlan.isconnected():
    time.sleep(0.2)

ip = wlan.ifconfig()[0]
print("Connected:", ip)

# -----------------------------
# IR Setup (GP13)
# -----------------------------
ir = Pin(13, Pin.OUT)
pwm = PWM(ir)
pwm.freq(38000)
pwm.duty_u16(0)

CARRIER_DUTY = int(0.33 * 65535)
last_sent_power = 0
last_sent_other = 0

def sleep_us_safe(us):
    while us > 0:
        t = min(us, 50000)
        time.sleep_us(t)
        us -= t

def send_ir(pattern):
    for i, dur in enumerate(pattern):
        pwm.duty_u16(CARRIER_DUTY if i % 2 == 0 else 0)
        sleep_us_safe(dur)
    pwm.duty_u16(0)
    print("IR sent")

def send_power():
    global last_sent_power
    now = time.ticks_ms()
    if time.ticks_diff(now, last_sent_power) < 3000:  # 3s cooldown
        print("Ignoring duplicate POWER trigger")
        return
    last_sent_power = now
    send_ir(POWER)

def send_other(pattern):
    global last_sent_other
    now = time.ticks_ms()
    if time.ticks_diff(now, last_sent_other) < 1000:  # 1s cooldown
        print("Ignoring duplicate trigger")
        return
    last_sent_other = now
    send_ir(pattern)

# -----------------------------
# IR COMMANDS
# -----------------------------
POWER = [
    2219,732,750,729,753,722,749,1384,
    755,1374,755,705,746,708,753,697,
    754,754,749,731,751,723,749,721,
    750,715,746,713,748,1370,749,701,749,
    99627,
    2216,735,747,732,750,725,747,1387,
    753,1376,753,706,755,700,751,698,
    753,755,748,732,750,725,747,722,
    749,716,745,714,747,1372,747,702,749
]

FAN_UP = [2215,734,748,731,751,723,748,1384,755,1372,747,712,749,705,745,703,747,759,754,1389,750,723,748,1384,755,709,752,1371,747,1370,748,700,750]
FAN_DOWN = [2216,735,747,732,750,724,747,1385,754,1374,755,704,746,708,753,696,754,1416,754,1389,750,1387,752,1381,748,1380,749,1374,755,699,751,1362,746]
COOL = [2218,732,749,729,752,721,750,1382,747,1380,748,710,751,703,747,702,748,1422,748,730,752,1386,753,716,745,1382,747,712,749,1369,749,1363,755]
HEAT_UP = [2218,732,750,728,753,720,751,1381,747,1379,749,710,751,702,748,701,749,757,745,1396,753,1384,755,1378,751,1376,753,706,754,699,751,698,752]
HEAT_DOWN = [2213,738,754,723,748,725,746,1386,753,1374,754,704,746,707,754,695,745,1425,745,1397,752,721,750,718,753,1374,755,1368,750,703,747,1365,753]
TIMER = [2215,735,746,730,751,722,749,1383,745,1381,747,711,749,704,746,702,748,1422,748,730,751,722,749,720,751,712,748,1373,745,1372,746,702,748]
OSCILLATE = [2221,729,752,725,746,727,754,1377,751,1375,753,706,755,699,751,697,753,753,749,729,752,1384,755,1377,751,713,747,711,749,1367,751,1361,746]
NARROW = [2214,736,745,732,749,724,747,1383,756,1371,747,712,748,705,745,703,747,759,754,1387,752,722,749,719,752,1375,753,705,745,708,752,696,754]
WIDE = [2220,731,750,725,746,727,754,1377,751,1376,752,705,745,709,751,696,754,1416,754,724,747,1389,750,1382,746,717,754,1368,750,703,747,1365,753]

# -----------------------------
# Dyson-themed Web UI (red->blue)
# -----------------------------
WEB_UI = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dyson AM09 Remote</title>
<style>
body {
  background: linear-gradient(180deg, #7a0f0f, #0a1c3d);
  font-family: "SF Pro Rounded", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;
}
.remote {
  background: linear-gradient(180deg, #3a3a3a, #151515);
  width: 260px;
  padding: 22px;
  border-radius: 42px;
  box-shadow:
    inset 0 2px 4px rgba(255,255,255,0.12),
    0 30px 70px rgba(0,0,0,0.9);
  text-align: center;
}
.logo {
  color: #dcdcdc;
  letter-spacing: 4px;
  font-size: 18px;
  margin-bottom: 18px;
  font-weight: 500;
}
.btn {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  border: none;
  background: radial-gradient(circle at top, #5a5a5a, #222);
  color: #f0f0f0;
  font-size: 13px;
  font-weight: 500;
  margin: 8px;
  box-shadow:
    inset 0 2px 3px rgba(255,255,255,0.15),
    0 10px 18px rgba(0,0,0,0.7);
}
.btn:active {
  transform: scale(0.94);
  box-shadow:
    inset 0 5px 8px rgba(0,0,0,0.7);
}
.power {
  background: radial-gradient(circle at top, #ff4d4d, #8b0000);
  font-weight: 600;
}
.row {
  display: flex;
  justify-content: center;
}
.small {
  width: 72px;
  height: 72px;
  font-size: 12px;
}
.footer {
  margin-top: 14px;
  font-size: 11px;
  color: #9a9a9a;
}
</style>
</head>
<body>
<div class="remote">
  <div class="logo">DYSON</div>
  <button class="btn power" onclick="send('/power')">POWER</button>
  <div class="row">
    <button class="btn small" onclick="send('/fan_up')">FAN +</button>
    <button class="btn small" onclick="send('/fan_down')">FAN -</button>
  </div>
  <div class="row">
    <button class="btn small" onclick="send('/heat_up')">HEAT +</button>
    <button class="btn small" onclick="send('/heat_down')">HEAT -</button>
  </div>
  <div class="row">
    <button class="btn small" onclick="send('/cool')">COOL</button>
    <button class="btn small" onclick="send('/oscillate')">OSC</button>
  </div>
  <div class="row">
    <button class="btn small" onclick="send('/wide')">WIDE</button>
    <button class="btn small" onclick="send('/narrow')">NARROW</button>
  </div>
  <button class="btn small" onclick="send('/timer')">TIMER</button>
  <div class="footer">AM09 Infrared Remote</div>
</div>
<script>
function send(url) { fetch(url); }
</script>
</body>
</html>
"""

# -----------------------------
# HTTP SERVER
# -----------------------------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print("HTTP server ready at", ip)

while True:
    cl, addr = s.accept()
    req = cl.recv(1024).decode()
    try:
        if "GET / " in req:
            cl.send("HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n")
            cl.send(WEB_UI)
        elif "/power" in req:
            send_power()
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/fan_up" in req:
            send_other(FAN_UP)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/fan_down" in req:
            send_other(FAN_DOWN)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/heat_up" in req:
            send_other(HEAT_UP)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/heat_down" in req:
            send_other(HEAT_DOWN)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/cool" in req:
            send_other(COOL)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/oscillate" in req:
            send_other(OSCILLATE)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/wide" in req:
            send_other(WIDE)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/narrow" in req:
            send_other(NARROW)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
        elif "/timer" in req:
            send_other(TIMER)
            cl.send("HTTP/1.1 200 OK\r\n\r\nOK")
    except:
        pass
    cl.close()


