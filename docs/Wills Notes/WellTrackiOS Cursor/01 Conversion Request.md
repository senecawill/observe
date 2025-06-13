I'll help you create an iOS equivalent of the WellTrack application that maintains compatibility with the existing database server and synchronization protocols. Let's break this down into steps and create a modern iOS application using Swift and SwiftUI.

First, let me explore the existing codebase to understand the database structure and synchronization protocols.

Ran tool


Let me analyze the synchronization protocol and database structure to ensure we create a compatible iOS application. From the code, I can see that:

1. The database synchronization protocol uses:
- Socket-based communication on ports 5301, 5302, 5303
- Server address: wtdb.senecatech.com
- Custom text-based protocol for syncing
- SQLite database for local storage
- GZIP compression for database transfers

1. The sync protocol sequence:
```
Connect -> Send:
- Company_ID
- Tender_Name
- Version
- Database Date
- Database Signature

Loop until complete:
- Send Update Byte Count + Update
- Receive "OK" for success

Server responses:
- "OK" = Success
- "MEH" = Byte count mismatch
- "RX" = Receive Updates (SQL statements)
- "RD" = Receive replacement database
```

Let me search for the database schema to understand the table structure.

Ran tool


Based on the code analysis, I can now outline the key components needed for the iOS application to maintain compatibility with the existing system:

1. Database Schema:
Main tables:
- T_Well_List: Well information
- T_Well_Visitation: Well visit records
- T_House_List: House information
- T_House_Meter_Visit: House meter visits
- T_Compressor_List: Compressor information
- T_Compressor: Compressor records
- T_Vehicle_Maintenance: Vehicle maintenance records
- T_List_Vehicle: Vehicle list
- T_Time: Time records
- T_Expense: Expense records
- T_Swabbing: Swabbing operations
- T_Hauling: Hauling operations
- T_WellInspection: Well inspection records
- T_DB: Database metadata
- T_Prefs: Application preferences

1. Synchronization Protocol:
```swift
// Core sync protocol implementation
class WellTrackSync {
    private let serverAddress = "wtdb.senecatech.com"
    private let serverPorts = [5301, 5302, 5303]
    
    // Tables that need to be synced for additions
    private let addTables = [
        "T_WellInspection",
        "T_Well_Visitation",
        "T_Compressor",
        "T_Expense",
        "T_Vehicle_Maintenance", 
        "T_Hauling",
        "T_House_Meter_Visit",
        "T_Time",
        "T_Swabbing"
    ]
    
    // Tables that need to be synced for updates
    private let updateTables = [
        "T_Well_List",
        "T_Compressor_List", 
        "T_House_List",
        "T_List_Vehicle"
    ]
    
    private let updateTableKeys = [
        "Well_Name",
        "Compressor",
        "House_Name",
        "_id"
    ]
    
    func sync() async throws {
        // 1. Connect to server
        guard let socket = try await connectToServer() else {
            throw SyncError.connectionFailed
        }
        
        // 2. Send initial handshake
        try await sendHandshake(socket: socket)
        
        // 3. Process server updates first
        try await processServerUpdates(socket: socket)
        
        // 4. Send local changes
        try await sendLocalChanges(socket: socket)
        
        // 5. Handle database replacement if needed
        try await handleDatabaseReplacement(socket: socket)
    }
}

// Database manager
class WellTrackDatabase {
    private var db: SQLiteDatabase
    
    // Record status flags
    private let TURN_IN_FLAG = 1
    private let TURNED_IN_FLAG = 2
    
    init() throws {
        // Initialize SQLite database
        let dbPath = FileManager.default
            .urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("WellTrack.db")
        
        db = try SQLiteDatabase(path: dbPath)
    }
    
    func markRecordForSync(table: String, id: Int) throws {
        try db.execute(
            "UPDATE ? SET Turn_In = ? WHERE _id = ?",
            [table, TURN_IN_FLAG, id]
        )
    }
    
    func getRecordsForSync(table: String) throws -> [Record] {
        return try db.query(
            "SELECT * FROM ? WHERE Turn_In = ?",
            [table, TURN_IN_FLAG]
        )
    }
}

// Core data models
struct Well: Codable {
    var id: Int
    var wellNumber: String
    var meterNumber: String
    var latitude: Double
    var longitude: Double
    var turnIn: Int
    // ... other fields
}

struct WellVisit: Codable {
    var id: Int
    var visitDate: Date
    var wellTender: String
    var wellNumber: String
    var meterNumber: String
    var turnIn: Int
    // ... other fields
}
```

1. iOS App Architecture:
```swift
// Main app structure
@main
struct WellTrackApp: App {
    @StateObject private var dataManager = DataManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(dataManager)
        }
    }
}

// Data manager
class DataManager: ObservableObject {
    private let database: WellTrackDatabase
    private let syncManager: WellTrackSync
    
    @Published var wells: [Well] = []
    @Published var visits: [WellVisit] = []
    
    init() {
        database = try! WellTrackDatabase()
        syncManager = WellTrackSync()
        
        // Start background sync timer
        Timer.scheduledTimer(withTimeInterval: 300, repeats: true) { _ in
            Task {
                try? await self.sync()
            }
        }
    }
    
    func sync() async throws {
        try await syncManager.sync()
        await refreshData()
    }
}

// Main navigation view
struct ContentView: View {
    @EnvironmentObject var dataManager: DataManager
    
    var body: some View {
        TabView {
            WellListView()
                .tabItem { 
                    Label("Wells", systemImage: "list.bullet")
                }
            
            CompressorListView()
                .tabItem {
                    Label("Compressors", systemImage: "gear")
                }
            
            VehicleListView()
                .tabItem {
                    Label("Vehicles", systemImage: "car")
                }
            
            TimeSheetView()
                .tabItem {
                    Label("Time", systemImage: "clock")
                }
        }
    }
}
```

1. Key Features to Implement:
- SQLite database with identical schema
- Socket-based sync protocol
- Background sync service
- Offline capability
- GPS location tracking
- File attachments
- Data validation
- Error handling
- User authentication
- Secure data transmission

Would you like me to proceed with implementing any specific part of this system? I can:

1. Create the database schema and migrations
2. Implement the sync protocol
3. Build the UI components
4. Set up the data models
5. Create the networking layer

Let me know which aspect you'd like to focus on first.
