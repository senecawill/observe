I'll help you create the UI components for the WellTrack iOS app. We'll create several views to handle different aspects of the application. Let's start with the main views:

1. First, let's create the main tab view controller:

```swift:WellTrackiOS/WellTrackiOS/Views/MainTabView.swift
import SwiftUI

struct MainTabView: View {
    @State private var selectedTab = 0
    @StateObject private var wellListViewModel = WellListViewModel()
    @StateObject private var syncViewModel = SyncViewModel()
    
    var body: some View {
        TabView(selection: $selectedTab) {
            WellListView(viewModel: wellListViewModel)
                .tabItem {
                    Label("Wells", systemImage: "drop.fill")
                }
                .tag(0)
            
            HouseListView()
                .tabItem {
                    Label("Houses", systemImage: "house.fill")
                }
                .tag(1)
            
            CompressorListView()
                .tabItem {
                    Label("Compressors", systemImage: "gear")
                }
                .tag(2)
            
            TimeEntryView()
                .tabItem {
                    Label("Time", systemImage: "clock.fill")
                }
                .tag(3)
            
            SettingsView(syncViewModel: syncViewModel)
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(4)
        }
        .alert("Sync Error", isPresented: $syncViewModel.showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(syncViewModel.errorMessage)
        }
    }
}
```


1. Now, let's create the Well List view and its view model:

```swift:WellTrackiOS/WellTrackiOS/ViewModels/WellListViewModel.swift
import Foundation
import GRDB

@MainActor
class WellListViewModel: ObservableObject {
    /// Database instance
    private let database = WellTrackDatabase.shared
    
    /// Published wells list
    @Published private(set) var wells: [Well] = []
    
    /// Loading state
    @Published private(set) var isLoading = false
    
    /// Error state
    @Published var error: Error?
    
    /// Initialize view model
    init() {
        Task {
            await loadWells()
        }
    }
    
    /// Load wells from database
    func loadWells() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            wells = try await database.queue.read { db in
                try Well.fetchAll(db, sql: """
                    SELECT * FROM T_Well_List
                    WHERE Deleted = 0
                    ORDER BY Well_Number
                    """)
            }
        } catch {
            self.error = error
        }
    }
    
    /// Add new well
    func addWell(_ well: Well) async {
        do {
            try await database.queue.write { db in
                try well.insert(db)
            }
            await loadWells()
        } catch {
            self.error = error
        }
    }
    
    /// Update existing well
    func updateWell(_ well: Well) async {
        do {
            try await database.queue.write { db in
                try well.update(db)
            }
            await loadWells()
        } catch {
            self.error = error
        }
    }
    
    /// Delete well
    func deleteWell(_ well: Well) async {
        do {
            try await database.queue.write { db in
                // Soft delete
                try db.execute(sql: """
                    UPDATE T_Well_List
                    SET Deleted = 1, Deleted_Date = datetime('now')
                    WHERE _id = ?
                    """, arguments: [well.id])
            }
            await loadWells()
        } catch {
            self.error = error
        }
    }
    
    /// Search wells
    func searchWells(_ query: String) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            wells = try await database.queue.read { db in
                try Well.fetchAll(db, sql: """
                    SELECT * FROM T_Well_List
                    WHERE Deleted = 0
                    AND (Well_Number LIKE ? OR Well_Name LIKE ?)
                    ORDER BY Well_Number
                    """, arguments: ["%\(query)%", "%\(query)%"])
            }
        } catch {
            self.error = error
        }
    }
}
```

```swift:WellTrackiOS/WellTrackiOS/Views/WellListView.swift
import SwiftUI

struct WellListView: View {
    @ObservedObject var viewModel: WellListViewModel
    @State private var searchText = ""
    @State private var showingAddWell = false
    @State private var selectedWell: Well?
    
    var body: some View {
        NavigationView {
            List {
                if viewModel.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, alignment: .center)
                } else if viewModel.wells.isEmpty {
                    Text("No wells found")
                        .foregroundColor(.secondary)
                        .frame(maxWidth: .infinity, alignment: .center)
                } else {
                    ForEach(viewModel.wells) { well in
                        WellRowView(well: well)
                            .contentShape(Rectangle())
                            .onTapGesture {
                                selectedWell = well
                            }
                    }
                    .onDelete { indexSet in
                        Task {
                            if let index = indexSet.first {
                                await viewModel.deleteWell(viewModel.wells[index])
                            }
                        }
                    }
                }
            }
            .navigationTitle("Wells")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showingAddWell = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .searchable(text: $searchText)
            .onChange(of: searchText) { newValue in
                Task {
                    if newValue.isEmpty {
                        await viewModel.loadWells()
                    } else {
                        await viewModel.searchWells(newValue)
                    }
                }
            }
            .refreshable {
                await viewModel.loadWells()
            }
            .sheet(isPresented: $showingAddWell) {
                WellFormView(mode: .add) { well in
                    Task {
                        await viewModel.addWell(well)
                    }
                }
            }
            .sheet(item: $selectedWell) { well in
                WellFormView(mode: .edit(well)) { updatedWell in
                    Task {
                        await viewModel.updateWell(updatedWell)
                    }
                }
            }
            .alert("Error", isPresented: .constant(viewModel.error != nil)) {
                Button("OK", role: .cancel) {
                    viewModel.error = nil
                }
            } message: {
                if let error = viewModel.error {
                    Text(error.localizedDescription)
                }
            }
        }
    }
}

struct WellRowView: View {
    let well: Well
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(well.wellNumber)
                .font(.headline)
            
            if let wellName = well.wellName {
                Text(wellName)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            HStack {
                if let meterNumber = well.meterNumber {
                    Text("Meter: \(meterNumber)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if well.turnIn == 1 {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

struct WellFormView: View {
    enum Mode {
        case add
        case edit(Well)
    }
    
    let mode: Mode
    let onSave: (Well) -> Void
    
    @Environment(\.dismiss) private var dismiss
    @State private var wellNumber = ""
    @State private var wellName = ""
    @State private var meterNumber = ""
    @State private var latitude = 0.0
    @State private var longitude = 0.0
    @State private var notify = ""
    @State private var notifyMessage = ""
    @State private var comments = ""
    @State private var turnIn = false
    
    var title: String {
        switch mode {
        case .add:
            return "Add Well"
        case .edit:
            return "Edit Well"
        }
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Well Information")) {
                    TextField("Well Number", text: $wellNumber)
                    TextField("Well Name", text: $wellName)
                    TextField("Meter Number", text: $meterNumber)
                }
                
                Section(header: Text("Location")) {
                    HStack {
                        Text("Latitude")
                        Spacer()
                        TextField("Latitude", value: $latitude, format: .number)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.decimalPad)
                    }
                    
                    HStack {
                        Text("Longitude")
                        Spacer()
                        TextField("Longitude", value: $longitude, format: .number)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.decimalPad)
                    }
                }
                
                Section(header: Text("Notifications")) {
                    TextField("Notify", text: $notify)
                    TextField("Notify Message", text: $notifyMessage)
                }
                
                Section(header: Text("Additional Information")) {
                    TextEditor(text: $comments)
                        .frame(height: 100)
                    
                    Toggle("Turn In", isOn: $turnIn)
                }
            }
            .navigationTitle(title)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        let well = Well(
                            id: mode.well?.id ?? 0,
                            wellNumber: wellNumber,
                            meterNumber: meterNumber,
                            wellName: wellName,
                            latitude: latitude,
                            longitude: longitude,
                            notify: notify,
                            notifyMessage: notifyMessage,
                            comments: comments,
                            turnIn: turnIn ? 1 : 0,
                            deleted: 0,
                            deletedDate: nil
                        )
                        onSave(well)
                        dismiss()
                    }
                    .disabled(wellNumber.isEmpty)
                }
            }
            .onAppear {
                if case .edit(let well) = mode {
                    wellNumber = well.wellNumber
                    wellName = well.wellName ?? ""
                    meterNumber = well.meterNumber ?? ""
                    latitude = well.latitude
                    longitude = well.longitude
                    notify = well.notify ?? ""
                    notifyMessage = well.notifyMessage ?? ""
                    comments = well.comments ?? ""
                    turnIn = well.turnIn == 1
                }
            }
        }
    }
}

private extension WellFormView.Mode {
    var well: Well? {
        switch self {
        case .add:
            return nil
        case .edit(let well):
            return well
        }
    }
}
```


1. Let's create the Well model:

```swift:WellTrackiOS/WellTrackiOS/Models/Well.swift
import Foundation
import GRDB

struct Well: Identifiable, Codable {
    let id: Int64
    let wellNumber: String
    let meterNumber: String?
    let wellName: String?
    let latitude: Double
    let longitude: Double
    let notify: String?
    let notifyMessage: String?
    let comments: String?
    let turnIn: Int
    let deleted: Int
    let deletedDate: Date?
    
    enum CodingKeys: String, CodingKey {
        case id = "_id"
        case wellNumber = "Well_Number"
        case meterNumber = "Meter_Number"
        case wellName = "Well_Name"
        case latitude = "Latitude"
        case longitude = "Longitude"
        case notify = "Notify"
        case notifyMessage = "Notify_Message"
        case comments = "Comments"
        case turnIn = "Turn_In"
        case deleted = "Deleted"
        case deletedDate = "Deleted_Date"
    }
}

// MARK: - GRDB Support
extension Well: TableRecord, FetchableRecord, PersistableRecord {
    static let databaseTableName = "T_Well_List"
    
    func encode(to container: inout PersistenceContainer) {
        container[CodingKeys.id] = id
        container[CodingKeys.wellNumber] = wellNumber
        container[CodingKeys.meterNumber] = meterNumber
        container[CodingKeys.wellName] = wellName
        container[CodingKeys.latitude] = latitude
        container[CodingKeys.longitude] = longitude
        container[CodingKeys.notify] = notify
        container[CodingKeys.notifyMessage] = notifyMessage
        container[CodingKeys.comments] = comments
        container[CodingKeys.turnIn] = turnIn
        container[CodingKeys.deleted] = deleted
        container[CodingKeys.deletedDate] = deletedDate
    }
    
    init(row: Row) {
        id = row[CodingKeys.id]
        wellNumber = row[CodingKeys.wellNumber]
        meterNumber = row[CodingKeys.meterNumber]
        wellName = row[CodingKeys.wellName]
        latitude = row[CodingKeys.latitude]
        longitude = row[CodingKeys.longitude]
        notify = row[CodingKeys.notify]
        notifyMessage = row[CodingKeys.notifyMessage]
        comments = row[CodingKeys.comments]
        turnIn = row[CodingKeys.turnIn]
        deleted = row[CodingKeys.deleted]
        deletedDate = row[CodingKeys.deletedDate]
    }
}
```


1. Let's create the Settings view and its view model for sync control:

```swift:WellTrackiOS/WellTrackiOS/ViewModels/SyncViewModel.swift
import Foundation

@MainActor
class SyncViewModel: ObservableObject {
    /// Sync service
    private let syncService = SyncService.shared
    
    /// Loading state
    @Published private(set) var isSyncing = false
    
    /// Error state
    @Published var showError = false
    @Published var errorMessage = ""
    
    /// Last sync time
    @Published private(set) var lastSyncTime: Date?
    
    /// Start sync process
    func sync() async {
        guard !isSyncing else { return }
        
        isSyncing = true
        defer { isSyncing = false }
        
        do {
            try await syncService.startSync()
            lastSyncTime = Date()
        } catch {
            showError = true
            errorMessage = error.localizedDescription
        }
    }
    
    /// Reset database
    func resetDatabase() async {
        do {
            try await WellTrackDatabase.shared.reset()
            lastSyncTime = nil
        } catch {
            showError = true
            errorMessage = error.localizedDescription
        }
    }
    
    /// Backup database
    func backupDatabase() async {
        do {
            try await WellTrackDatabase.shared.backup()
        } catch {
            showError = true
            errorMessage = error.localizedDescription
        }
    }
    
    /// Restore database
    func restoreDatabase() async {
        do {
            try await WellTrackDatabase.shared.restore()
        } catch {
            showError = true
            errorMessage = error.localizedDescription
        }
    }
}
```

```swift:WellTrackiOS/WellTrackiOS/Views/SettingsView.swift
import SwiftUI

struct SettingsView: View {
    @ObservedObject var syncViewModel: SyncViewModel
    @State private var showingResetConfirmation = false
    @State private var showingRestoreConfirmation = false
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Synchronization")) {
                    HStack {
                        Text("Last Sync")
                        Spacer()
                        if let lastSync = syncViewModel.lastSyncTime {
                            Text(lastSync, style: .relative)
                                .foregroundColor(.secondary)
                        } else {
                            Text("Never")
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    Button {
                        Task {
                            await syncViewModel.sync()
                        }
                    } label: {
                        HStack {
                            Text("Sync Now")
                            if syncViewModel.isSyncing {
                                Spacer()
                                ProgressView()
                            }
                        }
                    }
                    .disabled(syncViewModel.isSyncing)
                }
                
                Section(header: Text("Database")) {
                    Button {
                        Task {
                            await syncViewModel.backupDatabase()
                        }
                    } label: {
                        Text("Backup Database")
                            .foregroundColor(.blue)
                    }
                    
                    Button {
                        showingRestoreConfirmation = true
                    } label: {
                        Text("Restore from Backup")
                            .foregroundColor(.orange)
                    }
                    
                    Button {
                        showingResetConfirmation = true
                    } label: {
                        Text("Reset Database")
                            .foregroundColor(.red)
                    }
                }
                
                Section(header: Text("About")) {
                    HStack {
                        Text("Version")
                        Spacer()
                        Text(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown")
                            .foregroundColor(.secondary)
                    }
                    
                    HStack {
                        Text("Build")
                        Spacer()
                        Text(Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "Unknown")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .navigationTitle("Settings")
            .alert("Reset Database", isPresented: $showingResetConfirmation) {
                Button("Cancel", role: .cancel) {}
                Button("Reset", role: .destructive) {
                    Task {
                        await syncViewModel.resetDatabase()
                    }
                }
            } message: {
                Text("Are you sure you want to reset the database? This action cannot be undone.")
            }
            .alert("Restore Database", isPresented: $showingRestoreConfirmation) {
                Button("Cancel", role: .cancel) {}
                Button("Restore", role: .destructive) {
                    Task {
                        await syncViewModel.restoreDatabase()
                    }
                }
            } message: {
                Text("Are you sure you want to restore from backup? Current data will be replaced.")
            }
        }
    }
}
```


I've implemented the core UI components for the WellTrack iOS app. Here's a breakdown of what each component does:

1. **MainTabView**:
   - Main navigation container using SwiftUI's `TabView`
   - Five main sections: Wells, Houses, Compressors, Time, and Settings
   - Each tab has its own navigation stack
   - Handles sync error alerts

2. **WellListView**:
   - Displays list of wells with search functionality
   - Pull-to-refresh support
   - Add/Edit/Delete well operations
   - Shows well details in a custom row view
   - Error handling with alerts

3. **WellFormView**:
   - Form for adding/editing wells
   - Input validation
   - Location input with decimal keyboard
   - Sections for different types of information
   - Cancel/Save actions

4. **SettingsView**:
   - Sync controls with status indicator
   - Database management (backup/restore/reset)
   - Confirmation dialogs for destructive actions
   - App version information

The UI follows iOS design guidelines and includes:
- Modern SwiftUI components
- Proper navigation hierarchy
- Error handling and user feedback
- Loading states and progress indicators
- Form validation
- Confirmation dialogs for destructive actions
- Pull-to-refresh
- Search functionality

To complete the UI, we still need to implement:
1. House list and form views
2. Compressor list and form views
3. Time entry view
4. Well visit form
5. House meter visit form
6. Compressor maintenance form

Would you like me to implement any of these remaining views next?

Note: The current implementation assumes the existence of corresponding models and view models for the other sections. We should create those as needed when implementing the remaining views.
