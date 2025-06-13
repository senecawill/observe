
If you imagine a group of people using walkie-talkies, they must agree on the same channel (frequency), how loud to speak (TX power), how quickly they talk (spreading factor), how carefully they enunciate (coding rate), how many times they say “hello” before the message (preamble), and if they’re listening or speaking at a given moment (RX or TX mode).

`// Settings for LoRa P2P and LoRa Mesh`

`g_lorawan_settings.p2p_tx_power = 22;		  // Max TX power`
`g_lorawan_settings.p2p_bandwidth = 0;		  // 0 = 125kHz, can try 3 (62.5kHz) or 4 (41.67kHz) for longer range`
`g_lorawan_settings.p2p_sf = 7;				  // Can try 8, 9, 10 for longer range`
`g_lorawan_settings.p2p_cr = 1;				  // Can try 2, 3 or 4 for longer range`
`g_lorawan_settings.p2p_preamble_len = 8;	  // "standard"`
`g_lorawan_settings.p2p_symbol_timeout = 0;	  // "standard"`

`// Force listening`
`g_lora_p2p_rx_mode = RX_MODE_RX;`

Think of these parameters as the “knobs” on a walkie-talkie, where you tune the channel, transmission power, and other details so that LoRa devices can reliably talk to each other.

---

## 1. `p2p_frequency = 909600000`

- **What it is:** This is the radio channel the device will use to send and receive data (in Hz).
- **Why it matters:** LoRa devices must all “agree” on the same frequency in order to communicate.
- **Possible values:**
        - EU: 868,000,000 to 868,600,000 Hz (868 MHz band)
        - US: 902,000,000 to 928,000,000 Hz (915 MHz band)
- **How to choose:** Different regions have different regulations for which frequencies are allowed. 909.6 MHz is an example that might be used in certain regions or experimental setups.

**Analogy:** Tuning your FM radio to 100.3 MHz. If you want to hear a station, you must be on its exact frequency.

---

## 2. `p2p_tx_power = 22`

- **What it is:** The transmit power in decibels relative to 1 milliwatt (dBm).
- **Why it matters:** Higher power generally means your signal can travel further, but uses more battery and might be limited by local regulations.
- **Possible values:** Typically **2 dBm to 22 dBm** for sub-GHz modules.
- **How to choose:** If battery life is critical, or regulations limit power, you’d use a lower number. If you want maximum range and can legally do so, you set it higher.

**Analogy:** Shouting vs. whispering. You can be heard further away if you shout, but it drains your energy faster, and you might not be allowed to shout too loudly in some places.

---

## 3. `p2p_bandwidth = 0`

- **What it is:** LoRa bandwidth setting. “0” corresponds to 125 kHz. Other possible values might correspond to narrower bandwidths like 62.5 kHz or 41.7 kHz.
- **Why it matters:** Narrower bandwidth (larger numerical value in code) gives better range at the expense of lower data rate (you transmit less data per second).
- **Possible values:**
	- `0` = 125 kHz _(default and most common)_
	- `1` = 250 kHz
	- `2` = 500 kHz
	- `3` = 62.5 kHz
	- `4` = 41.7 kHz
	- `5` = 31.25 kHz
	- `6` = 20.8 kHz
	- `7` = 15.6 kHz
	- `8` = 10.4 kHz
	- `9` = 7.8 kHz _(extremely narrow, very long range, very slow data)_
- **How to choose:** For short distance or faster data, use 125 kHz. For very long distances or ultra-low-power scenarios, you might select a narrower bandwidth like 62.5 kHz.

**Analogy:** The width of a pipe for water flow. A wider pipe lets more water through faster, but may not reach as far if water pressure is low.

---

## 4. `p2p_sf = 7`

- **What it is:** The “spreading factor” (SF) in LoRa. Higher spreading factor = better sensitivity (longer range) but slower data rate.
- **Why it matters:** SF7 is a good balance of speed and distance. If you need more range, you can increase it to SF8, SF9, etc.—but your transmissions will be slower.
- **Possible values:** `6` to `12`.
		***Note:** Some modules/support start at SF5, but SF6 is more typical as a lower bound.*
- **How to choose:** If you’re operating in a place where you need maximum distance and can tolerate slow data, go higher. If you have shorter range requirements and want faster data, keep it lower.

**Analogy:** Think of this like slow, clear speech vs. fast, mumbled speech. Slower, clearer speech can be understood farther away but takes more time to say the same thing.

---

## 5. `p2p_cr = 1`

- **What it is:** The “coding rate” for LoRa. Internally, LoRa uses forward error correction. A setting of “1” typically represents a coding rate of 4/5 (one extra bit of error correction for every four bits of data). Larger values correspond to more robust error correction.  The value in code typically corresponds to “4/x” in LoRa terminology:
- **Why it matters:** More error correction (higher coding rate) improves reliability at long range or in noisy environments but further reduces throughput.
- **Possible values:** 
	- `1` = 4/5
	- `2` = 4/6
	- `3` = 4/7
	- `4` = 4/8
- **How to choose:** If your transmissions are often corrupted by interference or you need extreme reliability, increase it. If you have a robust signal or time is critical, keep it lower.

**Analogy:** Repeating yourself a few times to make sure you’re understood, but it takes longer to get the message across.

---

## 6. `p2p_preamble_len = 8`

- **What it is:** The length of the “preamble” in LoRa packets. The preamble is a series of symbols that help the receiver sync up with the incoming signal.
- **Why it matters:** A standard setting is often 8. Increasing it can improve detection of very weak signals but adds a small overhead to the transmission time.
- **Possible values:**
	- `6` to `65535` (in theory), but **8** is standard.
- **How to choose:** If you’re missing data due to poor synchronization or extreme range, you might increase this. Otherwise, 8 is a standard, balanced choice.

**Analogy:** Saying “Hello… hello… hello…” at the start of every conversation. It gives the listener time to tune in.

---

## 7. `p2p_symbol_timeout = 0`

- **What it is:** This is the timeout for the receiver’s symbol detection. When set to 0, it often means “no special timeout,” i.e., it will keep looking for incoming signals.
- **Why it matters:** If you set a non-zero symbol timeout, the radio might stop listening if it doesn’t detect anything within a certain time. Keeping it at 0 is a typical choice for continuous listening.
- **Possible values:**
	- `0` to `65535`.
	- `0` usually means “no specific timeout” or “continuous reception” (depending on the firmware).
- **How to choose:** Use 0 if your device should continuously listen. If you want to save power by briefly listening and then sleeping, you might use a nonzero timeout.

**Analogy:** It’s like waiting indefinitely for someone to speak, rather than hanging up the phone if nobody talks immediately.

---

## 8. `g_lora_p2p_rx_mode = RX_MODE_RX`

- **What it is:** This forces the device to remain in Receive mode for LoRa P2P (point-to-point).
- **Why it matters:** Without this, the device might switch between transmitting and receiving based on other conditions. This ensures it’s always listening for incoming signals (like a walkie-talkie that stays on the “listen” channel).
- **Possible values:**
	- `RX_MODE_NONE` (not receiving),
	- `RX_MODE_RX` or `RX_MODE_CONTINUOUS` (constantly listening),
	- `RX_MODE_SINGLE` (listen for a single packet then stop),
	- `TX_MODE_TX` (transmit mode).
- **How to choose:** In a simple setup, if you want to be ready to receive at all times, you’d set it to “RX.” If you have a device that’s predominantly transmitting, you’d change this logic accordingly.

**Analogy:** A walkie-talkie that’s locked into “listening” mode, waiting for someone else to talk.

---

## Putting It All Together

These settings work together to define:

1. **Where** to communicate (frequency).
2. **How loudly** to talk (transmit power).
3. **How wide** the signal bandwidth is.
4. **How slow/fast** (spreading factor)
5. **How much error correction** (coding rate).
6. **How to start** the transmission (preamble)
7. **How long to wait** (symbol timeout).
8. **What the device is doing** listening, transmitting, or both (RX mode).


That’s the essence of the LoRa P2P settings. Think of it as configuring a digital walkie-talkie for maximum reliability and range under the constraints of battery usage, data speed, and local regulations.