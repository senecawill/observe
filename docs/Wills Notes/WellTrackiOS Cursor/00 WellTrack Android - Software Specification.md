Write a detailed specification document for the XXX detailed enough to allow the reader to duplicate the functionality exactly in Swift for iPhone. Do not write the swift code, only describe the existing application.
# WellTrack Android Application - Software Specification

## 1. System Overview
WellTrack is an Android application designed for managing and monitoring well operations, equipment maintenance, and field operations in the oil and gas industry. The application provides comprehensive functionality for tracking wells, meters, compressors, and various field activities.

## 2. Core Modules

### 2.1 Application Core
- **Main Application (`WellTrackApplication.java`)**
  - Handles application lifecycle
  - Manages global application state
  - Initializes core services and components

- **Base Activity (`WTActivity.java`)**
  - Provides common functionality for all activities
  - Handles navigation and UI state management

### 2.2 Data Management
- **Database Module**
  - `MyDatabase.java`: Core database management
  - `DatabaseSendRecord.java`: Handles data synchronization
  - `DataSqlExporter.java`: Manages data export functionality
  - Multiple specialized database handlers for different entities:
    - `dbWell_List.java`: Well management
    - `dbCompressor_List.java`: Compressor tracking
    - `dbAST_Site.java`: AST site management
    - `dbHouse_Visit.java`: House visit records
    - `dbWell_Visitation.java`: Well visitation tracking

### 2.3 Well Operations
- **Well Management**
  - `Activity_WellOrMeter.java`: Well and meter management interface
  - `Activity_WellVisitation.java`: Well visit tracking and reporting
  - `Activity_WellHistory.java`: Historical well data and analytics
  - `Activity_WellInspection.java`: Well inspection procedures

### 2.4 Equipment Management
- **Compressor Module**
  - `Activity_Compressor.java`: Compressor management
  - `Activity_Compressor_Select.java`: Compressor selection interface
  - `Activity_CompressorHistory.java`: Compressor maintenance history

- **Vehicle Management**
  - `Activity_List_Vehicles.java`: Vehicle listing and management
  - `Activity_Vehicle_Maintenance.java`: Vehicle maintenance tracking
  - `Activity_VehicleHistory.java`: Vehicle history records

### 2.5 Field Operations
- **Site Activities**
  - `Activity_AST_Select.java`: AST site selection and management
  - `Activity_Hauling.java`: Hauling operations management
  - `Activity_Swabbing.java`: Swabbing operations tracking
  - `Activity_House_Meter_Visit.java`: House meter visit management

### 2.6 Monitoring and Calculations
- **Calculation Tools**
  - `Activity_BblCalc.java`: Barrel calculations
  - `Activity_RateCalc.java`: Rate calculations
  - `Activity_TankMonthlyEPA.java`: EPA compliance calculations
  - `Activity_TankAnnualEPA.java`: Annual EPA reporting

### 2.7 Time and Expense Tracking
- **Time Management**
  - `Activity_Time.java`: Time tracking interface
  - `Activity_TimeHistory.java`: Time history records
  - `Activity_Expenses.java`: Expense tracking and management

### 2.8 Data Visualization
- **Graphing Components**
  - `GraphView.java`: Base graphing functionality
  - `LineGraphView.java`: Line graph implementation
  - `BarGraphView.java`: Bar graph implementation
  - `GraphViewSeries.java`: Data series management
  - `GraphViewStyle.java`: Graph styling utilities

### 2.9 UI Components
- **Custom Views**
  - `TableView.java`: Custom table view implementation
  - `SearchableSpinner.java`: Enhanced spinner with search
  - `SearchableListDialog.java`: Searchable list dialog
  - `View_Switcher.java`: View switching utility

### 2.10 Network and Services
- **Network Management**
  - `Service_Network.java`: Network service management
  - `Receiver_Netwatch.java`: Network monitoring
  - `BootReceiver.java`: Boot-time initialization

## 3. Technical Specifications

### 3.1 Database Structure
- SQLite database implementation
- Multiple tables for different data entities
- Sync capabilities with remote server

### 3.2 User Interface
- Material Design implementation
- Responsive layouts for different screen sizes
- Support for both portrait and landscape orientations
- Localization support (English and Spanish)

### 3.3 Data Synchronization
- Background sync service
- Offline capability with local storage
- Conflict resolution handling

### 3.4 Security
- User authentication
- Secure data transmission
- Role-based access control

## 4. Dependencies
- Android SDK
- SQLite database
- Custom graphing libraries
- Network communication libraries

## 5. Performance Requirements
- Fast data retrieval and storage
- Efficient memory management
- Responsive UI interactions
- Reliable background services

## 6. Compatibility
- Minimum Android API level support
- Multiple screen size support
- Various Android device compatibility

This specification provides a comprehensive overview of the WellTrack Android application's architecture and functionality. Each module is designed to work independently while maintaining cohesive integration with the overall system. The application follows Android best practices and provides a robust solution for well tracking and field operations management.

Would you like me to dive deeper into any specific module or component?
