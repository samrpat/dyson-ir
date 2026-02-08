# dyson-ir
![Image](https://github.com/user-attachments/assets/3cfbf777-da7c-4bbf-8bb9-5791ed1e42e0)
## A raspberry pi pico code + pcb to control a Dyson AM09, providing a web ui for controls and endpoints for smart home control.
## Features

- Power ON/OFF

- Fan speed up / down

- Heat up / down

- Cool mode

- Oscillation

- Timer

- Wide / Narrow airflow

- Built-in web UI (With Dyson-style remote theme)

- Raw IR timings (no protocol guessing)

- Cooldown protection to prevent double sends

## Parts Needed
- Raspberry Pi Pico W or Pico 2 W	Both compatible
- IR LED 940 nm recommended
- 2N2222 NPN transistor
- 82 Ω resistor
- 470 Ω resistor
- Breadboard / PCB	Optional
- Jumper wires	Depends on Breadboard/PCB
## Setup

1. Flash MicroPython for Pico W / Pico 2 W, I suggest using Thonny

2. Copy main.py to the Pico

3. Edit Wi-Fi credentials:

  SSID = "YourWiFi"
  PASSWORD = "YourPassword"
  
4. Reboot the Pico

5. Check the serial console in Thonny for the IP address
## IR Codes
### Credit to jaylikesbundaGot, with ir codes from https://github.com/Lucaslhm/Flipper-IRDB/blob/f4fdb72281da42920ecede238bd19c088e7e8f6b/Fans/Dyson/Dyson_AM09.ir#L3
## Double-Send Protection

Repeat Commands are slightly delayed

Prevents Dyson from interpreting one press as two

Fixes the “turns on then off” issue I ran into previously with the power IR code

## HTTP Endpoints

Each endpoint sends one IR command with Double-Send protection.



| Endpoint  | Action |
| ------------- | ------------- |
| /power  | Power toggle  |
| /fan_up  | Fan speed +  |
| /fan_down  | Fan speed -  |
| /heat_up  | Heat +  |
| /heat_down  | Heat -  |
| /cool | Cool mode  |
| /oscillate  | Oscillation |
| /timer  | Timer  |
| /wide  | Wide Airflow  |
| /narrow  | Narrow Airflow  |

![Image](https://github.com/user-attachments/assets/ff17c217-09e2-4ab5-9914-1eb546d8db68)


