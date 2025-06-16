# AT Command Protocol

  

The firmware supports an AT command interface for user interaction, configuration, and debugging. This includes both custom commands defined in this project and the standard WisBlock API v2 AT commands provided by the WisBlock firmware base.

  

---

  

## Key Features

- Serial Interface: Commands are sent over a serial connection (UART/USB).

- Text-Based: Commands follow the classic "AT+<COMMAND>" format.

- Extensible: New commands can be added in `user_at_cmd.cpp` (custom) or are available via the WisBlock API v2 base.

  

---

  

## Command Format

- Query: `AT+CMD?` returns the current value.

- Set: `AT+CMD=<value>` sets a new value.

- Execute: `AT+CMD` runs the command (no value).

  

---

  

# 1. Custom/User AT Commands

  

These are defined in `user_at_cmd.cpp` and are specific to this project:

  

| Command | Description | Query | Set | Exec | Perm | Notes |

|-----------|-----------------------------------|-------|-----|------|------|-------------------------|

| +FRESET | Flash Reset | | | Yes | W | Factory reset flash |

| +SETTINGS | Get current settings | Yes | | | W | Dumps all config values |

| +MASTER | Set/get Master Node address | Yes | Yes | | RW | 8 hex digits |

| +NODE | Get this Node address | Yes | | | R | 8 hex digits |

| +MESH | Get the mesh map | Yes | | | R | Returns mesh topology |

| +BUID | Set/get Blues product UID | Yes | Yes | | RW | 25+ char string |

| +BREQ | Send a Blues Notecard Request | | Yes | | W | Flexible Blues request |

| +BR | Remove all Blues Settings | | | Yes | W | Clears Blues config |

| +BRES | Factory reset Blues Notecard | | | Yes | W | |

| +MESHEN | Set/get Mesh Enabled | Yes | Yes | | RW | 0/1 |

| +MESHGW | Set/get Mesh Gateway | Yes | Yes | | RW | 0/1 |

| +MESHSD | Set/get Mesh Sender | Yes | Yes | | RW | 0/1 |

| +CRES | Factory Reset Config File | | | Yes | R | |

| +DADC4 | Set/get Differential ADC 4mA | Yes | Yes | | RW | float |

| +DADC20 | Set/get Differential ADC 20mA | Yes | Yes | | RW | float |

| +DMIN | Set/get Differential Min inH2O | Yes | Yes | | RW | float |

| +DMAX | Set/get Differential Max inH2O | Yes | Yes | | RW | float |

| +DSCALE | Set/get Differential Scale | Yes | Yes | | RW | SQRT/LINEAR |

| +PADC4 | Set/get Pressure ADC 4mA | Yes | Yes | | RW | float |

| +PADC20 | Set/get Pressure ADC 20mA | Yes | Yes | | RW | float |

| +PMIN | Set/get Pressure Min psi | Yes | Yes | | RW | float |

| +PMAX | Set/get Pressure Max psi | Yes | Yes | | RW | float |

| +PSCALE | Set/get Pressure Scale | Yes | Yes | | RW | SQRT/LINEAR |

| +OPS | Set/get Orifice Plate Size | Yes | Yes | | RW | float |

| +MRS | Set/get Meter Run Size | Yes | Yes | | RW | int |

| +TEMP | Set/get Temperature | Yes | Yes | | RW | int |

| +SG | Set/get Specific Gravity | Yes | Yes | | RW | float |

| +AP | Set/get Atmospheric Pressure | Yes | Yes | | RW | float |

| +READINT | Set/get Reading Interval | Yes | Yes | | RW | int (minutes) |

| +UPINT | Set/get Blues Modem Send Interval | Yes | Yes | | RW | int (minutes) |

  

Legend: Query: `AT+CMD?` | Set: `AT+CMD=<val>` | Exec: `AT+CMD` | Perm: R=Read, W=Write, RW=Read/Write

  

---

  

# 2. WisBlock API v2 Standard AT Commands

  

These are provided by the WisBlock firmware base and are available on all WisBlock API v2 devices. For full details, see the [RAKwireless WisBlock API v2 AT Command Manual](https://docs.rakwireless.com/Product-Categories/WisBlock/RAK4631/AT-Command-Manual/).

  

## System Commands

  

| Command | Description |

|------------|------------------------------|

| AT+VER? | Get firmware version |

| AT+HELP | List all AT commands |

| AT+BOOT | Reboot the device |

| AT+SLEEP | Enter sleep mode |

| AT+UART | Set UART baud rate |

| AT+DEBUG | Enable/disable debug output |

| AT+DEFAULT | Restore default settings |

| AT+RUN | Start application |

| AT+STOP | Stop application |

| AT+TIME | Get/set system time |

  

## LoRa P2P Commands

  

| Command | Description |

|-------------|-----------------------------|

| AT+LORA | Set LoRa P2P parameters |

| AT+SEND | Send data in LoRa P2P mode |

| AT+RX | Receive data in LoRa P2P |

| AT+FREQ | Set LoRa frequency |

| AT+BW | Set LoRa bandwidth |

| AT+SF | Set LoRa spreading factor |

| AT+CR | Set LoRa coding rate |

| AT+PREAMBLE | Set LoRa preamble length |

| AT+POWER | Set LoRa TX power |

  

## LoRaWAN Commands

  

| Command | Description |

|------------|--------------------------------------|

| AT+NWM | Set network mode (LoRaWAN or P2P) |

| AT+JOIN | Join LoRaWAN network |

| AT+SEND | Send data in LoRaWAN mode |

| AT+RX | Receive data in LoRaWAN mode |

| AT+APPKEY | Set LoRaWAN AppKey |

| AT+APPEUI | Set LoRaWAN AppEUI |

| AT+DEVEUI | Set LoRaWAN DevEUI |

| AT+DEVADDR | Set LoRaWAN DevAddr |

| AT+NWKSKEY | Set LoRaWAN NwkSKey |

| AT+APPSKEY | Set LoRaWAN AppSKey |

| AT+ADR | Enable/disable Adaptive Data Rate |

| AT+DR | Set data rate |

| AT+CLASS | Set LoRaWAN class (A/B/C) |

| AT+BAND | Set LoRaWAN frequency band |

| AT+CH | Set LoRaWAN channel |

| AT+PORT | Set LoRaWAN port |

| AT+LINKCHK | Link check |

| AT+REJOIN | Force rejoin |

| AT+RESET | Reset LoRaWAN stack |

  

## BLE Commands

  

| Command | Description |

|------------|----------------------------|

| AT+BLE | Enable/disable BLE |

| AT+BLENAME | Set BLE device name |

| AT+BLERST | Reset BLE |

| AT+BLERX | Receive data over BLE |

| AT+BLESEND | Send data over BLE |

  

## GPIO/Peripheral Commands

  

| Command | Description |

|-----------|----------------------------|

| AT+GPIO | Set/get GPIO state |

| AT+ADC | Read ADC value |

| AT+I2C | I2C scan or read/write |

| AT+SPI | SPI read/write |

| AT+PWM | Set PWM output |

  

## Other/Utility Commands

  

| Command | Description |

|-----------|----------------------------|

| AT+BAT | Get battery voltage |

| AT+VDD | Get supply voltage |

| AT+RSSI | Get last packet RSSI |

| AT+SNR | Get last packet SNR |

| AT+MAC | Get device MAC address |

| AT+SN | Get device serial number |

| AT+FW | Get firmware version |

| AT+HW | Get hardware version |

  

---

  

## Response Format

- OK: Command succeeded (e.g., `OK`)

- ERROR: Command failed (e.g., `ERROR: <reason>`)

- Data: Some commands return data (e.g., `ID: 12345`)

  

## Extending the Protocol

- Add new command handlers in `user_at_cmd.cpp` for custom commands.

- Follow the existing pattern for parsing, validating, and responding to commands.

  

---

  

For the most up-to-date and detailed information, see the [RAKwireless WisBlock API v2 AT Command Manual](https://docs.rakwireless.com/Product-Categories/WisBlock/RAK4631/AT-Command-Manual/).