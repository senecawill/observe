# LoRa Functionality in Detail

## 1. Network Architecture

### 1.1 Network Modes
The system supports two LoRa modes:
1. **LoRaWAN Mode** (disabled by default)
2. **P2P (Peer-to-Peer) Mode** (used for mesh networking)

### 1.2 Node Types
1. **Regular Node**: Basic mesh participant
2. **Gateway Node**: Has cellular connectivity to forward data
3. **Sender Node**: Can send data through the mesh

## 2. Message Types

### 2.1 Data Message Structure (`data_msg_s`)
```cpp
struct data_msg_s {
    uint8_t mark1 = 'L';    // Message marker
    uint8_t mark2 = 'o';    // Message marker
    uint8_t mark3 = 'R';    // Message marker
    uint8_t type;          // Message type
    uint32_t dest;         // Destination address
    uint32_t from;         // Source address
    uint32_t orig;         // Original sender
    uint8_t data[243];     // Payload data
};
```

### 2.2 Message Types
1. `LORA_INVALID` (0): Invalid message
2. `LORA_DIRECT` (1): Direct message to specific node
3. `LORA_FORWARD` (2): Forwarded message
4. `LORA_BROADCAST` (3): Broadcast message
5. `LORA_NODEMAP` (4): Network topology map
6. `LORA_MAP_REQ` (5): Request for network map

## 3. Network Management

### 3.1 Node Identification
- Each node has a unique 32-bit address
- Address is generated from device MAC address
- Broadcast ID is derived from node address

### 3.2 Network Map
- Maintains topology of connected nodes
- Maximum 30 nodes in network
- Map synchronization:
  - Initial sync: Every 30 seconds
  - Normal sync: Every 10 minutes

### 3.3 Message Routing
1. **Direct Messages**:
   - Sent directly to target node
   - Uses node's address for routing

2. **Broadcast Messages**:
   - Sent to all nodes in network
   - Uses broadcast ID
   - Prevents message loops

3. **Forwarded Messages**:
   - Relayed through intermediate nodes
   - Maintains original sender information

## 4. Communication Flow

### 4.1 Message Sending
```cpp
bool send_to_mesh(bool is_broadcast, uint32_t target_addr, uint8_t *tx_data, uint8_t data_size)
```
1. Validates message size (max 243 bytes)
2. Prepares message header
3. Adds to send queue
4. Triggers transmission

### 4.2 Message Reception
```cpp
void mesh_check_rx(uint8_t *rxPayload, uint16_t rxSize, int16_t rxRssi, int8_t rxSnr)
```
1. Validates message format
2. Processes based on message type:
   - Direct messages: Delivers to target
   - Broadcast messages: Forwards to network
   - Map messages: Updates network topology

### 4.3 Queue Management
- Send queue size: 4 messages
- Message buffer size: 256 bytes
- Implements retry mechanism (3 attempts)

## 5. Error Handling

### 5.1 Network Errors
1. **Unknown Nodes**:
   - Triggers map update request
   - Updates network topology

2. **Failed Transmissions**:
   - Implements retry mechanism
   - Logs failure for debugging

### 5.2 Message Validation
1. **Format Validation**:
   - Checks message markers
   - Validates message type
   - Verifies message size

2. **Duplicate Prevention**:
   - Tracks broadcast messages
   - Prevents message loops

## 6. Performance Optimization

### 6.1 Power Management
- Implements sleep modes
- Optimizes transmission timing
- Manages radio state machine

### 6.2 Bandwidth Optimization
- Maximum payload size: 243 bytes
- Efficient message headers
- Optimized network map updates

## 7. Integration with Application

### 7.1 Sensor Data Transmission
1. Reads sensor values
2. Formats data for transmission
3. Sends through mesh network
4. Handles acknowledgments

### 7.2 Gateway Functionality
1. Receives data from mesh
2. Forwards to cellular network
3. Manages data buffering
4. Handles transmission failures

## 8. Configuration

### 8.1 Network Settings
- Mesh enabled/disabled
- Gateway mode
- Sender mode
- Reading interval
- Send interval

### 8.2 Regional Settings
- Automatic band selection based on location
- Supports multiple regions:
  - US (Band 5)
  - Europe (Band 4)
  - Australia (Band 6)
  - Japan (Band 8)
  - Philippines (Band 10)

This LoRa implementation provides a robust, scalable mesh networking solution that can handle various communication scenarios while maintaining efficient power usage and reliable data transmission.
