Below is **well-documented pseudocode** that captures the core functionality of your **LoRa Mesh Repeater / Gateway subset**. It omits low-level details and specific library calls (e.g., `Serial`, `MYLOG`, `Wire`) while illustrating the overall data flow, branching logic, and function responsibilities.

---

## High-Level Overview

1. **Global Settings & Buffers**
    
    - Mesh retry count, buffer sizes, and flags to indicate whether the device is a **Gateway** or **Repeater (Sender)**.
    - A data array (`dataArr`) buffers incoming or outgoing `SensorData` items.
2. **Initialization**
    
    - `setup_app()` sets up serial logs and configures **LoRa** for P2P (Mesh) mode.
    - `init_app()` loads settings, initializes mesh callbacks (if enabled), and starts BLE for debugging or configuration.
3. **Data Forwarding**
    
    - **Repeaters**: Attempt to forward each new reading to the gateway via mesh.
    - **Gateways**: Send data to Blues.
4. **Buffer Management**
    
    - If an immediate send fails, data is stored in a local buffer (`dataArr`).
    - `check_buffer()` and `send_reading_mesh()` flush any leftover buffered data.
5. **Event Handlers**
    
    - Handlers for **mesh data**, **mesh map changes**, **BLE** events, and **LoRa** events are included.

---

## Pseudocode

```pseudo
GLOBAL CONSTANTS:
    MESH_RETRY_COUNT  = 3       // Attempts to send over mesh
    MAX_BUFFER_SIZE   = 60      // Maximum sensor data records buffered

GLOBAL FLAGS & VARIABLES:
    MESH_ENABLED      = false   // Enable mesh usage
    MESH_GATEWAY      = false   // This node is a gateway to Blues
    MESH_SENDER       = false   // This node is a repeater/relay
    dataArr[]         // Array of SensorData for buffering
    arrSize           // Number of valid entries in dataArr
    has_blues         = false   // Indicates whether a Blues Notecard is available
    data_buffer[]     // General buffer for optional data transmissions
    map_changed       = false   // Flag to track mesh topology changes
    g_ble_dev_name    = "METER" // BLE advertisement name
    g_master_node_addr= 0x00    // Address of the gateway/master in the mesh
    convert_value     // Union used for byte packing/unpacking 64-bit values

----------------------------------------------------------------------
FUNCTION setup_app():
    1. Initialize serial communication (for logs).
    2. Wait briefly for serial port to become ready or timeout.
    3. Print an initial log message (“==== Mesh Repeater/Gateway Subset Code ====”).
    4. Force LoRa into P2P (mesh) mode by disabling LoRaWAN:
        - read existing credentials
        - set `lorawan_enable = false`
        - update credentials
    5. Enable BLE for debugging (optional).

END FUNCTION setup_app

----------------------------------------------------------------------
FUNCTION init_app() RETURNS bool:
    1. Load any stored settings from flash (`st_init_flash`).
    2. Read `g_master_node_addr` from file or memory (`read_master_node`).
    3. Optionally initialize I2C if hardware is needed (`Wire.begin`).
    4. If `MESH_ENABLED`:
        a. Set up mesh callbacks (`on_mesh_data` for incoming data, `map_changed_cb` for topology changes).
        b. Put radio in receive mode.
        c. Call `init_mesh` to initialize mesh stack.
    5. Else (mesh disabled):
        - Generate a fallback device address from unique hardware ID.
        - Log that mesh is disabled.
    6. If using Blues (e.g., on gateway):
        - Call `init_blues()` to detect and initialize the Notecard.
        - Optionally fetch location (`blues_get_location`).
    7. Start BLE advertising indefinitely (`restart_advertising(0)`).
    8. Example: set LoRa send interval to 60 seconds, then `save_settings()`.
    9. Return `true` to indicate successful initialization.

END FUNCTION init_app

----------------------------------------------------------------------
FUNCTION SendReadingsToBlues(dataArr, arrSize) RETURNS bool:
    // Called by a gateway node to upload sensor data to Blues
    1. If `arrSize == 0`, return `false` (no data).
    2. Begin forming a Notecard request (`"note.add"`).
    3. Add a string entry specifying the file name (e.g., `"seneca7.qo"`).
    4. Build a CSV string (`csvString`) from each SensorData record:
       For i in [0..arrSize-1]:
         - Convert node_id to hex string
         - Append columns: diff_adc, diff_pressure, press_adc, pressure, mcfd, read_date, read_time
    5. Add the CSV string to the request body (`"readings"`).
    6. Attempt to send the request to Blues.
        - If successful, optionally send `"card.status"` to confirm connectivity.
        - If unsuccessful, log the failure.
    7. Return `true` if the request was successful, otherwise `false`.

END FUNCTION SendReadingsToBlues

----------------------------------------------------------------------
FUNCTION st_sm_update_from_mesh(sensor_data) RETURNS bool:
    // Gateway forwarding function
    1. Log receipt of data from another mesh node.
    2. Forward that single SensorData record to Blues (via `SendReadingsToBlues`).
    3. Return result of the send attempt.

END FUNCTION st_sm_update_from_mesh

----------------------------------------------------------------------
FUNCTION addReading(node_id, diff_adc, diff_pressure, press_adc, pressure, mcfd, read_date, read_time):
    // Called when a new reading is generated or received from upstream
    1. Create a new `SensorData` struct with the passed parameters.
    2. Log that a new reading is being forwarded.
    3. Initialize `sendSuccess = false`.
    4. If `MESH_ENABLED` and **not** `MESH_GATEWAY` (i.e., Repeater):
        - Attempt up to `MESH_RETRY_COUNT` times to send to `g_master_node_addr`:
            a. If a direct route exists, send unicast.
            b. Otherwise, broadcast.
            c. If all attempts fail, `sendSuccess` remains `false`.
    5. Else if `MESH_GATEWAY`:
        - Call `SendReadingsToBlues` directly.
    6. If sending ultimately fails (or mesh is disabled):
        - If `arrSize < MAX_BUFFER_SIZE`, store new reading in `dataArr[arrSize]`.
        - Increment `arrSize`.
        - Log that the reading is buffered.

END FUNCTION addReading

----------------------------------------------------------------------
FUNCTION send_reading_mesh():
    // For repeaters: send the **first** buffered reading, if any
    1. If `arrSize > 0`:
        a. Send the first element `dataArr[0]` via mesh broadcast to gateway.
        b. If send succeeds:
            - Shift all remaining elements left by 1.
            - Decrement `arrSize`.
        c. Else log an error.

END FUNCTION send_reading_mesh

----------------------------------------------------------------------
FUNCTION check_buffer():
    // Attempt to flush **all** buffered readings
    1. While `arrSize > 0`:
        a. Attempt to send `dataArr[0]` to gateway:
            - If Repeater: unicast if route found, else broadcast.
            - If Gateway: call `SendReadingsToBlues`.
        b. If send succeeds:
            - Shift array left by 1.
            - Decrement `arrSize`.
        c. Else break to retry next time.

END FUNCTION check_buffer

----------------------------------------------------------------------
FUNCTION send_mesh_data():
    // Optional function for sending dummy “keepalive” data over mesh
    1. Prepare some fixed or dummy values in `data_buffer`.
    2. Check if route to `g_master_node_addr` is known:
        - If yes, unicast
        - Otherwise, broadcast
    3. Attempt to enqueue packet for sending.
    4. Log success/failure.

END FUNCTION send_mesh_data

----------------------------------------------------------------------
FUNCTION app_event_handler():
    // Called periodically or upon certain system events
    1. If `STATUS` flag is set:
        a. Clear `STATUS` flag.
        b. If `MESH_ENABLED`, call `send_reading_mesh()` to flush one reading.
           Optionally call `send_mesh_data()` to keep mesh alive.
    2. If `MESH_MAP_CHANGED` flag is set:
        a. Clear `MESH_MAP_CHANGED`.
        b. Print or log that the mesh map has changed (`print_mesh_map()`).

END FUNCTION app_event_handler

----------------------------------------------------------------------
FUNCTION ble_data_handler():
    // Processes BLE data if BLE is enabled
    1. If BLE is enabled and `BLE_DATA` flag is set:
        a. Clear the flag.
        b. Read available bytes from BLE UART, passing each to `at_serial_input()`.
        c. Finally, send a newline character to trigger command parsing.

END FUNCTION ble_data_handler

----------------------------------------------------------------------
FUNCTION lora_data_handler():
    // Handles LoRa events, bridging them into mesh logic
    1. If `LORA_JOIN_FIN` flag set:
        - Clear it.
        - If joined successfully, log “joined.” Otherwise, retry `lmh_join()`.
    2. If `LORA_TX_FIN` flag set:
        - Clear it.
        - Log TX success/fail, handle confirmed messaging if needed.
        - Call `mesh_check_tx()` so the mesh stack knows TX is done.
    3. If `LORA_DATA` flag set:
        - Clear it.
        - Process inbound LoRa data with `mesh_check_rx()`.

END FUNCTION lora_data_handler

----------------------------------------------------------------------
FUNCTION on_mesh_data(fromID, rxPayload, rxSize, rxRssi, rxSnr):
    // Mesh callback when data is received from another node
    1. Check `rxSize` matches `sizeof(SensorData)`.
       - If not, log invalid size and return.
    2. Copy payload into a local `SensorData` object.
    3. Log that mesh data arrived with RSSI/SNR info.
    4. If this node is `MESH_GATEWAY`, call `st_sm_update_from_mesh()` to forward to Blues.
    5. Else if this node is `MESH_SENDER`, call `addReading()` to forward data upstream.

END FUNCTION on_mesh_data

----------------------------------------------------------------------
FUNCTION map_changed_cb():
    // Callback for changes to the mesh topology
    1. Set `map_changed = true`.

END FUNCTION map_changed_cb

----------------------------------------------------------------------
FUNCTION generate_device_address(device_address):
    // Example function to build an 8-byte address from hardware-specific IDs
    1. Read a 32-bit register (`NRF_FICR->INFO.VARIANT`) for device variant.
    2. Extract device-specific IDs and store into `device_address[0..7]`.
    3. This ensures unique addresses per device.

END FUNCTION generate_device_address
```

### Key Takeaways

1. **Roles**
    
    - **Mesh Repeater (MESH_SENDER = true)** tries to forward each data packet up the chain to a master gateway (i.e., `g_master_node_addr`).
    - **Mesh Gateway (MESH_GATEWAY = true)** immediately sends data to Blues.
2. **Buffering**  
    If immediate transmission fails—either over mesh (Repeater) or to Blues (Gateway)—the data is **stored in `dataArr`**.
    
    - `send_reading_mesh()` or `check_buffer()` tries to flush these buffered readings on subsequent attempts.
3. **Event-Driven**  
    The function `app_event_handler()` runs whenever the `STATUS` event is flagged, and `ble_data_handler()` / `lora_data_handler()` run on their respective triggers.
    

This pseudocode should help you or your team quickly grasp how the Repeater/Gateway firmware handles events, data forwarding, and mesh operations.