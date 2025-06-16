# Program Flow

## 1. Initialization Phase

### 1.1 Hardware Setup (`setup_app()`)
1. Sets API version
2. Enables module power
3. Initializes serial communication
4. Forces LoRa P2P mode for mesh networking
5. Initializes the e-paper display (RAK14000)
6. Enables BLE (Bluetooth Low Energy)

### 1.2 Application Initialization (`init_app()`)
1. Loads settings from internal flash storage
2. Initializes user AT commands
3. Reads master node address for mesh networking
4. Initializes I2C communication
5. Sets up RAK13015 module for 4-20mA sensor readings
6. Initializes mesh networking if enabled:
   - Sets up mesh data and map-changed callbacks
   - Starts radio listening
   - Initializes mesh task
7. Sets up cellular connectivity (RAK5860) if available
8. Initializes Blues Notecard for cellular connectivity
9. Clears display and sets initial values
10. Sets up reading interval timer
11. Starts BLE advertising
12. Configures LoRaWAN settings

## 2. Main Operation Loop

### 2.1 Sensor Reading (`st_sm_update()`)
1. Reads differential pressure sensor (Channel 1)
2. Reads high-side pressure sensor (Channel 2)
3. Converts ADC readings to physical values:
   - Differential pressure in inH2O
   - High-side pressure in PSI
4. Calculates gas flow rate (MCFD) using orifice plate equation
5. Updates display with current readings
6. Adds reading to buffer for transmission

### 2.2 Data Transmission
1. Mesh Network (if enabled):
   - Sends data to master node or broadcasts
   - Handles data routing through mesh network
   - Forwards data to Blues Notecard if gateway node

2. Cellular Network (if available):
   - Sends data through Blues Notecard
   - Handles APN configuration
   - Manages cellular connectivity

### 2.3 Event Handling (`app_event_handler()`)
1. Handles status events:
   - Updates sensor readings
   - Sends data through mesh network
2. Handles mesh map changes:
   - Updates network topology
   - Prints mesh map

### 2.4 BLE Communication (`ble_data_handler()`)
1. Handles incoming BLE data
2. Processes AT commands
3. Manages cellular connectivity checks

## 3. Background Tasks

### 3.1 Mesh Network Management
1. Maintains network topology
2. Handles message routing
3. Manages node discovery
4. Synchronizes network map

### 3.2 Data Buffering
1. Stores readings in buffer
2. Manages buffer overflow
3. Handles retransmission of failed sends

### 3.3 Display Updates
1. Updates e-paper display with current readings
2. Shows network status
3. Displays battery level
4. Shows device identification

## 4. Configuration Management

### 4.1 Settings Storage
1. Stores settings in internal flash
2. Manages default values
3. Handles settings updates

### 4.2 AT Command Interface
1. Processes user commands
2. Updates device configuration
3. Provides status information

## 5. Error Handling

### 5.1 Sensor Errors
1. Validates sensor readings
2. Handles communication errors
3. Manages sensor calibration

### 5.2 Network Errors
1. Handles mesh network failures
2. Manages cellular connectivity issues
3. Implements retry mechanisms

### 5.3 System Errors
1. Handles power management
2. Manages memory allocation
3. Implements watchdog timer

This program flow ensures reliable operation of the gas flow measurement system while maintaining robust communication capabilities through both mesh and cellular networks. The system is designed to be configurable and maintainable through various interfaces (BLE, AT commands) while providing real-time monitoring through the e-paper display.
