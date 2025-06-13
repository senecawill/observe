# **Seneca Meter Web User Interface Specification Document**

---

## **1. Overview**

The Seneca Meter Web User Interface provides oil and gas production managers and well tenders with real-time and historical data from IoT-connected natural gas meters. This interface will display data in a dashboard format, allowing users to monitor key performance indicators (KPIs), analyze trends, and export data for reporting.

---

## **2. User Roles and Permissions**

These may be unnecessary as users and roles can be integrated with WellTrack

### **Roles**
- **Admin**
  - Permissions:
    - Add, edit, and delete customers.
    - Modify all tables.
    - Manage all users and assign roles.
    - Access all customer and device data.
  - Intended Users: System administrators.

- **Customer Admin**
  - Permissions:
    - Add, edit, and delete users within their company.
    - Assign roles to company users (limited to `customer_user`).
    - Modify customer-specific data (e.g., device settings).
    - View all data related to their company's devices.
    - Deleted records will be marked with the deleted flag in the tables rather than being removed.
  - Intended Users: Production managers.

- **Customer User**
  - Permissions:
    - View-only access to data related to their company's devices.
    - Cannot modify any data.
  - Intended Users: Well tenders and other operational staff.

### **Authentication and Authorization**
- Secure login with username and password.
- Role-based access to control the functionalities available to each user.
- Password reset functionality.

---

## **3. Screen Descriptions**

### **3.1 Main Dashboard**

**Purpose:** Provides an overview of key metrics, device statuses, and alerts.

**Layout:**

```
+----------------------------------------------------------------------------------------+
| Navigation Menu                                                                        |
| [Dashboard] [Devices] [Reports] [User Management] [Settings] [Help] [Logout]           |
+----------------------------------------------------------------------------------------+
|                                                                                        |
|  Key Performance Indicators (KPIs):                                                    |
|  +----------------------+----------------------+----------------------+----------------+
|  |   Total MCFD Today   |   Total BPD Today    |  Average Pressure    | Active Devices |
|  |      1,250 MCF       |       500 BBL        |      40.5 PSI        |       15       |
|  +----------------------+----------------------+----------------------+----------------+
|                                                                                        |
|  Data Visualization:                                                                   |
|                                                                                        |
|  [Select Time Range: Last 24 Hours ▼ ]   [Select Variables: MCFD ☐ BPD ☐ Pressure ☐    |
|                                                                                        |
|  -- Bar Chart Displaying Selected Process Variables --                                |
|  |                                                                                     |
|  | [Graph with Device on X-axis and selected variables (e.g., MCFD, Pressure) on Y-axis|
|  |                                                                                     |
|                                                                                        |
|  Device Summary:                                                                       |
|  +----------+-------------+-----------+--------------+----------------+---------------+
|  | DeviceID | Device Name | Status    | Last Reading | MCFD           | Pressure (PSI)|
|  +----------+-------------+-----------+--------------+----------------+---------------+
|  | dev12345 | Well A      | Active    | 10/17 13:26  | 11.65          | 38.57         |
|  | dev67890 | Well B      | Maintenance|10/17 13:25  | 9.34           | 40.08         |
|  | ...                                                                                |
|  +-----------------------------------------------------------------------------------+
|                                                                                        |
|  Alerts and Notifications:                                                             |
|  - [!] Device dev67890 is scheduled for maintenance tomorrow.                          |
|  - [!] Device dev54321 has exceeded pressure threshold.                                |
|                                                                                        |
+----------------------------------------------------------------------------------------+
```

**Features:**
- **KPIs Section:** Displays key metrics like production (MCFD, BPD), average pressure, and active devices.
- **Data Visualization:** Line chart with multi-variable selection for MCFD, BPD, Pressure, Differential Pressure, and Tank Volume.
- **Device Summary Table:** Includes latest readings for each device.
- **Alerts Section:** Highlights important notifications.

---

### **3.2 Device Detail Page**

**Purpose:** Displays detailed information and historical data for a specific device.

**Layout:**

```
+----------------------------------------------------------------------------------------+
| Device Details: [Device Name] (Device ID: dev12345)                                    |
|                                                                                        |
|  +-------------------+----------------------------------------------------------------+
|  | Status: Active    | Installation Date: 01/15/2024                                   |
|  | Type: Orifice Meter| Well Tender: John Doe                                          |
|  +-------------------+----------------------------------------------------------------+
|  Latest Readings:                                                                      |
|  +------------------------+------------------------+------------------------+
|  | MCFD: 11.65            | Pressure: 38.57 PSI    | Differential Pressure: 3.22 PSI   |
|  | Tank Volume: 150 BBL   | BPD: 20.45            |                                    |
|  +------------------------+------------------------+------------------------+
|                                                                                        |
|  Data Analysis:                                                                        |
|  +---------------------------+----------------------------------------+
|  | Select Time Period:         [Last 24 Hours ▼ ]                    |
|  +---------------------------+----------------------------------------+
|                                                                                        |
|  Metrics Summary for Selected Period:                                                  |
|  +---------------------+-------------------------+-------------------------+
|  | Metric              | Average Value          | Cumulative Value        |
|  +---------------------+-------------------------+-------------------------+
|  | MCFD               | 10.75                  | 258.00                  |
|  | BPD                | 19.25                  | 462.00                  |
|  | Pressure (PSI)     | 38.45                  | N/A                     |
|  | Differential (PSI) | 3.18                   | N/A                     |
|  | Tank Volume (BBL)  | 145.00                 | N/A                     |
|  +---------------------+-------------------------+-------------------------+
|                                                                                        |
|  Data Visualization:                                                                   |
|  [Select Data Types: MCFD ☐ BPD ☐ Pressure ☐ Differential ☐ Tank Volume ☐ ]            |
|                                                                                        |
|  -- Line Chart Displaying Selected Process Variables --                                |
|                                                                                        |
|  Historical Data Table:                                                                |
|  +----------+----------+--------+-----------+------------+-------------+---------------+
|  | Date     | Time     | MCFD   | Pressure | Diff Press | Tank Vol (BBL)| Daily Flow   |
|  +----------+----------+--------+-----------+------------+-------------+---------------+
|  | 10/17/24 | 13:26:03 | 11.65  | 38.57    | 3.22       | 150          | 20.45        |
|  | ...                                                                                 |
|  +------------------------------------------------------------------------------------+
|                                                                                        |
|  [Export Data ▼ ]  [Excel] [CSV] [PDF]                                                 |
+----------------------------------------------------------------------------------------+
```

**Features:**
- **Select Time Period:** Dropdown to choose or define a custom time range.
- **Metrics Summary:** Displays average and cumulative values for selected metrics over the chosen time period.
- **Multi-Variable Chart:** Allows comparison of MCFD, BPD, Pressure, Differential Pressure, and Tank Volume.
- **Historical Data Table:** Detailed records for the selected time range.


