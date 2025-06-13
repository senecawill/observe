# Setting Up a 3-Node LoRa Mesh Network Tutorial

## Prerequisites
- 3 Seneca Meter devices
- 1 Cellular modem (RAK5860) for the gateway node
- 1 Blues Notecard for the gateway node
- USB cables for programming
- Computer with PlatformIO installed

## Step 1: Prepare the Gateway Node

1. Connect the gateway device to your computer via USB
2. Open the project in PlatformIO
3. Configure the gateway node by sending these AT commands:
```bash
# Enable mesh networking
AT+MESHEN=1

# Set as gateway node
AT+MESHGW=1

# Set reading interval (in minutes)
AT+READINT=1

# Set send interval (in minutes)
AT+SENDINT=60

# Save settings
AT+SAVE
```

1. Install the cellular modem (RAK5860) and Blues Notecard
2. Power cycle the device

## Step 2: Prepare Node 1

1. Connect Node 1 to your computer via USB
2. Open the project in PlatformIO
3. Configure Node 1 by sending these AT commands:
```bash
# Enable mesh networking
AT+MESHEN=1

# Set as sender node
AT+MESHSD=1

# Set reading interval (in minutes)
AT+READINT=1

# Set send interval (in minutes)
AT+SENDINT=60

# Save settings
AT+SAVE
```

1. Power cycle the device

## Step 3: Prepare Node 2

1. Connect Node 2 to your computer via USB
2. Open the project in PlatformIO
3. Configure Node 2 by sending these AT commands:
```bash
# Enable mesh networking
AT+MESHEN=1

# Set as sender node
AT+MESHSD=1

# Set reading interval (in minutes)
AT+READINT=1

# Set send interval (in minutes)
AT+SENDINT=60

# Save settings
AT+SAVE
```

1. Power cycle the device

## Step 4: Network Setup

1. Power on the gateway node first
2. Wait for the gateway to initialize (about 30 seconds)
3. Power on Node 1
4. Power on Node 2
5. Verify network formation by checking the gateway's display:
   - It should show network status as "Up"
   - The mesh map should show all three nodes

## Step 5: Verify Network Operation

1. On the gateway node, send this AT command to view the mesh map:
```bash
AT+MESH
```

Expected output:
```
Mesh Map:
Node 1: [address] - Direct
Node 2: [address] - Direct
Gateway: [address] - Direct
```

1. Test data transmission:
   - Each node should be reading sensor data
   - Data should be visible on each node's display
   - Gateway should be forwarding data to the cloud

## Step 6: Troubleshooting

If nodes aren't connecting:

1. Check mesh status on each node:
```bash
AT+MESHEN?
```

1. Verify node roles:
```bash
AT+MESHGW?
AT+MESHSD?
```

1. Check signal strength:
```bash
AT+MESH
```
Look for RSSI values in the output

1. Common issues and solutions:
   - If a node shows "Down" status:
     - Power cycle the node
     - Check antenna connection
     - Verify mesh is enabled
   - If data isn't reaching the gateway:
     - Check cellular connectivity on gateway
     - Verify Blues Notecard is properly configured
     - Check send intervals match

## Step 7: Monitoring

1. Regular checks:
   - Monitor network status on displays
   - Check data transmission logs
   - Verify cloud data reception

2. Maintenance:
   - Keep firmware updated
   - Monitor battery levels
   - Check cellular connectivity

## Step 8: Network Expansion

To add more nodes:
1. Configure new node with same settings as Node 1 or 2
2. Power on in range of existing network
3. Verify addition to mesh map
4. Check data routing

## Important Notes

1. **Power Management**:
   - Gateway node should have reliable power
   - Battery-powered nodes should be monitored
   - Consider power-saving settings for battery nodes

2. **Network Stability**:
   - Keep gateway node powered on
   - Monitor signal strength between nodes
   - Consider node placement for optimal coverage

3. **Data Management**:
   - Gateway buffers data if cellular connection is lost
   - Data is stored locally until transmission
   - Consider buffer size for extended outages

4. **Security**:
   - Each node has a unique address
   - Messages are validated before processing
   - Network topology is regularly verified

## Support

If you encounter issues:
1. Check the device logs
2. Verify all connections
3. Contact support at will@senecatechnologies.com

This tutorial provides a basic setup for a 3-node mesh network. The network can be expanded by adding more nodes following the same configuration process.
