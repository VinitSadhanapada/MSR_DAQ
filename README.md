# MFM_random_reading

Install dependencies:
pip install pymodbus paho-mqtt windows-curses

Run Client_Rpi_Modbus_SM.py with terminal full screen to get output. 

Log into HiveMQ with the details given on mqtt_client.py. 




## 🔹 **1. Imports and Setup**

```python
from pymodbus.client import ModbusSerialClient as ModbusClient
import time, datetime, csv, os
from termcolor import colored
import curses
import elmeasure_LG6400 as LG6400
import elmeasure_LG5220 as LG5220
import elmeasure_LG5310 as LG5310
import elmeasure_EN8410 as EN8410
import elmeasure_iELR300 as ELR300
import mqtt_client as mqtt
import random
```

### ✅ Purpose:

* **Standard modules**: Handle time, dates, file I/O, terminal behavior.
* **Custom modules**: Provide device-specific meter reading functions.
* **`mqtt_client`**: Custom MQTT publisher.
* **`random`**: Used to generate fake meter readings in simulation mode.

---

## 🔹 **2. Global Constants and Configuration**

```python
UNIT = 0x1
PORT = "COM8"
```

* Placeholder Modbus device ID and COM port.

```python
# Device model constants
DEV_ELM_LG6400 = "LG6400"
DEV_ELM_LG5310 = "LG+5310"
DEV_ELM_LG5220 = "LG+5220"
DEV_ELM_EN8400 = "EN8400"
DEV_ELM_EN8100 = "EN8100"
DEV_ELM_EN8410 = "EN8410"
DEV_ELM_ELR300 = "ELR300"
```

```python
NoOfDevices = 3
deviceModels = [DEV_ELM_ELR300, DEV_ELM_ELR300, DEV_ELM_ELR300]
deviceNames = ["Device 1", ..., "Device 15"]
```

* Defines:

  * Number of devices to simulate.
  * Each device's model.
  * Names for display/logging purposes.

```python
readingInterval = 10
intervalBwReadings = 0
intervalBwMeter = 0.1
published_msg = 0
```

* **Timing controls**:

  * `readingInterval`: total delay between reading cycles.
  * `intervalBwMeter`: delay between devices.
  * `intervalBwReadings`: additional delay (currently 0).

```python
ERROR_FILE_NAME = "error_log.txt"
```

* File to log errors.

---

## 🔹 **3. Parameter and Register Mapping**

```python
Parameters = ['Time', LG6400.WATTS_TOTAL_STR, ..., LG6400.A_B_HARMO_STR]
regAdress = [LG6400.WATTS_TOTAL_ADD, ..., LG6400.A_B_HARMO_ADD]
```

* **List of parameter names and corresponding register addresses**.
* Used originally to read real data from Modbus meters (now simulated).

```python
regValue   = [0] * len(Parameters)
allRegValues = []
```

* **Placeholder arrays** to store values for each device per cycle.

---

## 🔹 **4. Display Functions**

### 🖥 `printRegValues_1(TotalReadings)`

* Clears the screen and prints register values using `print()` with colors.
* Divided into sections:

  * Voltage & Current
  * Frequency & Intrusion count
  * Power (Watts)
  * Harmonics

> ✅ Useful for **basic terminal** environments.

---

### 🖥 `printRegValues_2(TotalReadings, stdscr)`

* Uses the **`curses`** library to display in a full-screen style.
* Similar output structure to `printRegValues_1` but formatted with precise cursor positions.

> ✅ Offers **real-time data dashboard** feel for terminal interfaces.

---

## 🔹 **5. Utility Functions**

### 🧮 `pack(tup)`

```python
def pack(tup):
    return (tup[0]<<16)|tup[1]
```

* Combines two 16-bit values into one 32-bit integer.
* Useful for meters that split large values across two registers.

---

### 🕒 `format_seconds_to_hhmmss(seconds)`

```python
def format_seconds_to_hhmmss(seconds):
    ...
```

* Converts raw seconds into `hh:mm:ss` format for display.

---

## 🔹 **6. Meter Reading Functions**

### 📟 `ReadMeterDataDefault(client, Address, deviceID)`

```python
def ReadMeterDataDefault(...):
    return [0] * len(Parameters)
```

* Fallback dummy reader if no known model matches the ID.

---

### 🔁 `SimulateMeterData()`

```python
def SimulateMeterData():
    ...
```

* Returns a list of fake meter data:

  * First value: timestamp
  * Remaining: random float values (0–500)

> ✅ Used to simulate real meter behavior.

---

## 🔹 **7. Data Handling & Publishing**

### 📤 `ReadAndProcessMeterData(client, deviceID, csvFilePointer)`

* This function is supposed to:

  1. Read data from a meter based on `deviceModels`.
  2. Insert timestamp.
  3. Save to CSV.
  4. Publish to MQTT.

```python
regValue = SimulateMeterData()
csvFilePointer.writerow(regValue)
published_msg = mqtt.publish_message(...)
allRegValues[deviceID-1] = regValue.copy()
```

> ⚠️ Currently skips actual reading — always simulates.

---

## 🔹 **8. Main Execution Loop**

### 🧠 `mainFunction(stdscr)`

The core function wrapped with `curses.wrapper`.

#### Workflow:

1. Initialize MQTT.
2. Open CSV files for all devices and write headers.
3. Generate initial dummy values for all devices.
4. Loop:

   * For each device:

     * Simulate data
     * Log it
     * Publish via MQTT
     * Save to `allRegValues` for display
   * Call `printRegValues_2()` to show on screen
   * Wait `readingInterval` seconds

```python
while connected:
    for x in range(NoOfDevices):
        regValue = SimulateMeterData()
        ...
    printRegValues_2(...)
    time.sleep(readingInterval)
```

---

## 🔹 **9. Application Start**

```python
try:
    curses.wrapper(mainFunction)
except KeyboardInterrupt:
    print("exiting the thread")
    mqtt.mqtt_close()
```

* Starts the app in a `curses` environment.
* Cleans up MQTT on Ctrl+C interrupt.

---

## 🧩 Summary of Major Functional Sections

| Section           | Purpose                                                       |
| ----------------- | ------------------------------------------------------------- |
| Imports           | Bring in needed functionality (device reading, display, MQTT) |
| Config            | Set up devices, intervals, and parameters                     |
| Display Functions | Render data in terminal or console                            |
| Simulation        | Generate fake data for testing                                |
| MQTT + CSV        | Send and store the data                                       |
| Main Loop         | Run everything in a loop and control timing                   |

---
