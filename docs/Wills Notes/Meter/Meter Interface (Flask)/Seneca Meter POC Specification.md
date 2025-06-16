# **Seneca Meter Web UI – Single-File POC Specification**

**Language & Framework:**

- **Backend:** Python 3.10+ using Flask (all in a single `app.py` file).
- **Frontend:** HTML/Bootstrap 5, Vanilla JavaScript (ES6).
- **Charting Library:** **Chart.js** (selected for its ease of customization).

> **Note:** This is a minimal proof of concept (POC). All references to security, authentication, and role-based access are omitted. Database schema examples (Customers, Devices, Events, EventData, etc.) are provided for context. No production-level code is included here; this is **a specification** for the development team.

---

## **1. Project Overview**

This POC demonstrates a simple Flask application that shows how to:

1. List **Customers**.
2. Display a **Main Dashboard** for a selected customer, presenting production metrics and a summary of devices belonging to that customer.
3. Show a **Device Detail** page with more granular information, including trending charts from real (or mocked) sensor data.

All functionality (routes, data handling, and HTML rendering) will be contained in a single file: **`app.py`**.

---

## **2. Data Model Overview**

The following MySQL tables and views are relevant to this POC. They are referenced by the single Flask app for queries or can be replaced with mock data if a live database is unavailable:

1. **`Customers`**
    
    - Columns include `customer_id`, `name`, `address`, etc.
    - **POC Usage**: The homepage (`/`) will query this table to display a list of customers.
2. **`Devices`**
    
    - Columns include `device_id`, `customer_id`, `device_name`, `status`, etc.
    - **POC Usage**: After selecting a customer, the main dashboard uses this table to list devices for that customer.
3. **`Events`** and **`EventData`**
    
    - Store time-series production readings (e.g., MCFD, pressure).
    - **POC Usage**: The device detail page can query these to chart metrics over time.
4. **Views**:
    
    - **`monthly_production`** and **`monthly_volume_24_month`**: Provide aggregated production data for reporting.
    - **POC Usage**: Optional. Can be used to show monthly or 24-month trends on the device detail page.

---

## **3. Application Flow**

1. **Homepage**: Displays a **Customer List** (from `Customers` table).
    
    - **Route**: `GET /`
    - **Content**:
        - A simple Bootstrap table or list group showing each `customer_id`, `name`.
        - Clicking on a customer navigates to that customer’s dashboard (e.g., `/customers/<customer_id>/dashboard`).
2. **Customer Main Dashboard**: Displays summary metrics for the selected customer, plus the devices that belong to them.
    
    - **Route**: `GET /customers/<int:customer_id>/dashboard`
    - **Content**:
        - **KPI Cards**: Summaries for that customer (e.g., total daily MCFD, average pressure, count of active devices).
            - These can be computed from either live queries (e.g., `Devices` + `EventData`) or from aggregated views.
        - **Device Summary**: A table listing each device for this customer (`device_id`, `device_name`, `status`, latest reading, etc.).
            - Each row links to the device detail page (`/customers/<customer_id>/devices/<device_id>`).
        
3. **Device Detail**: Shows real-time or historical data for a specific device.
    
    - **Route**: `GET /customers/<int:customer_id>/devices/<device_id>`
    - **Content**:
        - **Device Overview**: Name, ID, type (e.g., “Orifice Meter”), installation date, location, status.
        - **Latest Readings**: MCFD, Pressure, Differential Pressure, etc.
        - **Time-Range Selection**: Dropdown or date picker to filter historical data (e.g., “Last 24 Hours”, “Last 7 Days”).
        - **Metrics Summary**: Table with average or cumulative values for the chosen range (MCFD, Pressure, etc.).
        - **Chart.js Visualization**: A line chart showing data points over time.
	        - For the selected device, show total MCFD, pressure, and differential pressure over time (customer-wide) using `monthly_production`
            - Toggling metrics (MCFD, Pressure, etc.) can be done via checkboxes or simple UI elements.
        - **Historical Data Table**: For the selected device, A table listing the last 24 months of production from the `monthly_volume_24_month` view.
        - **Data Visualization (Chart.js)**: For the selected device, show total MCFD, pressure, and differential pressure over time (customer-wide) using `monthly_production`
        - **Export Options** (Optional): Buttons to export the current data to CSV, Excel, or PDF if desired.

---

## **4. `app.py` Structure**

All routes and logic will be contained in a single file:

```plaintext
app.py
```

**Suggested Layout (Pseudocode Only):**

1. **Imports**
    
    - `from flask import Flask, request, render_template_string, ...`
    - Possibly `import mysql.connector` or other library for DB queries, or a mock data approach.
2. **Create Flask App**
    
    ```python
    app = Flask(__name__)
    ```
    
3. **(Optional) Database Connection Setup**
    
    - A simple MySQL or other DB client initialization.
    - For the POC, can be replaced with local Python dictionaries/lists.
4. **Homepage Route** (`/`)
    
    - **Logic**: Query or mock `Customers`.
    - **Template**: Render a table or list of customers. Each link points to `/customers/<customer_id>/dashboard`.
5. **Customer Dashboard Route** (`/customers/<int:customer_id>/dashboard`)
    
    - **Logic**: Query or mock the specific customer’s devices from `Devices` where `customer_id = :id`.
        - Aggregate any top-level KPIs (e.g., sum of MCFD) using `Events` + `EventData` or the monthly production views.
    - **Template**:
        - Display KPI cards for the selected customer.
        - Possibly a Chart.js snippet for an overall production trend.
        - Show a table listing devices. Link each row to `/customers/<int:customer_id>/devices/<device_id>`.
6. **Device Detail Route** (`/customers/<int:customer_id>/devices/<device_id>`)
    
    - **Logic**:
        - Retrieve device info from `Devices` by `device_id`.
        - Query historical data from `Events` + `EventData` (or from the aggregated monthly views).
        - Optionally parse query params (e.g., `start_date`, `end_date`) for a custom time range.
    - **Template**:
        - Display device metadata.
        - Chart.js line chart with relevant metrics.
        - Table of historical readings.
        - Buttons or links to export data (optional).
7. **(Optional) Export Routes**
    
    - Example: `GET /customers/<int:customer_id>/devices/<device_id>/export?format=csv`
    - Generate and return CSV/Excel/PDF data.
8. **Run the App**
    
    ```python
    if __name__ == "__main__":
        app.run(debug=True)
    ```
    

---

## **5. Frontend Considerations**

Since this is a single-file POC:

- **HTML** is provided via `render_template_string()` or minimal external templates.
- **Bootstrap 5** can be included via CDN links in the rendered string.
- **Chart.js** also included via CDN:
    
    ```html
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    ```
    
- **Vanilla JavaScript**: Inline `<script>` blocks for dynamic behaviors (e.g., building the chart, responding to user selections).

---

## **6. Data Access Methods**

1. **Live DB Queries**
    
    - The database resides on a MySQL server.  Server location should be specified in an database.ini file configuration file.
    - Use SQL statements to fetch data from `Customers`, `Devices`, `Events`, `EventData`, etc.
    - For aggregated monthly/daily stats, the queries could hit the views (`monthly_production`, `monthly_volume_24_month`).

---

## **7. Sample Flow (User Experience)**

1. **User visits** `http://localhost:5000/`
    
    - Sees a list of customers (e.g., “Berry Energy”).
    - Clicks on a customer name/link → `/customers/1/dashboard`.
2. **Customer Dashboard** (`/customers/1/dashboard`)
    
    - Sees summary metrics (e.g., total MCFD = 1,250, average pressure = 40.5 PSI).
    - A chart showing daily or monthly production for Berry Energy.
    - A device table (e.g., “dev:864049051634238 / B1030M”).
    - User clicks the device name → `/customers/1/devices/dev:864049051634238`.
3. **Device Detail** (`/customers/1/devices/dev:864049051634238`)
    
    - Shows metadata: installation date, location, status, etc.
    - Renders a Chart.js line chart of MCFD and pressure over the last 24 hours (or any chosen range).
    - Displays a table of recent readings.
    - (Optional) Buttons to export data or refine date range.

---

## **8. Future Enhancements**

1. **Authentication & Authorization**: Add user login, roles, and secure routes.
2. **Real-Time Streaming**: Replace manual data fetches with WebSockets or server-sent events (SSE).
3. **Robust Frontend Structure**: Move HTML to a dedicated `templates/` folder, JavaScript/CSS to `static/`.
4. **Expanded Reporting**: Use the advanced monthly views to create monthly or yearly production charts and detailed reports.
5. **GIS/Mapping**: Plot device locations on a map if lat/long is available.

---

### **Summary**

This single-file Flask POC outlines how to display a **Customer List** at the homepage, then navigate to a **Main Dashboard** for the selected customer, and finally drill down into **Device Details** with Chart.js visualizations. The underlying MySQL database schema (Customers, Devices, Events, EventData, plus views like monthly_production) is referenced for data retrieval. Bootstrap 5 and minimal JavaScript (ES6) keep the UI simple yet functional.

The POC’s goal is to demonstrate a basic end-to-end flow—listing customers, viewing production metrics, and drilling into device data—without the overhead of a full production code structure.