# Schema Migration Guide: Industrial Screw Tightening Data

## 📋 New Data Schema

Your IoT devices now send **industrial quality control data** for screw tightening operations:

```json
{
  "Timestamp": "2025-11-18T10:30:00.000Z",
  "MachineID": "screw-robot-001",
  "ProductID": "PROD-A100",
  "ScrewPosition": 3,
  "TargetTorque": 20.5,
  "ActualTorque": 20.8,
  "TargetAngle": 1080,
  "ActualAngle": 1095,
  "PulseCount": 12,
  "CycleOK": true,
  "CycleTime_ms": 2340,
  "SpindleRotationCounter": 3,
  "BitRotationCounter": 45678,
  "ErrorCode": 0
}
```

---

## 🔄 Field Descriptions

| Field | Type | Description | Range/Values |
|-------|------|-------------|--------------|
| **Timestamp** | ISO 8601 | UTC timestamp of the operation | - |
| **MachineID** | string | Unique machine identifier | `screw-robot-001` to `010` |
| **ProductID** | string | Product being assembled | `PROD-A100`, `PROD-B150`, etc. (8 variants) |
| **ScrewPosition** | int | Screw position on product (1-8) | 1-8 |
| **TargetTorque** | decimal | Target torque in Newton-meters (Nm) | 15.0 - 25.0 Nm |
| **ActualTorque** | decimal | Measured torque achieved | ±15% of target (normal), ±30% (anomaly) |
| **TargetAngle** | int | Target rotation angle in degrees | Multiple of 360° |
| **ActualAngle** | int | Measured rotation angle | ±15° (normal), ±45° (anomaly) |
| **PulseCount** | int | Encoder pulse count | 4 pulses per rotation |
| **CycleOK** | boolean | Quality status of cycle | `true` = Pass, `false` = Fail |
| **CycleTime_ms** | int | Cycle duration in milliseconds | 1000-3000ms (normal), <1000 or >3000 (anomaly) |
| **SpindleRotationCounter** | int | Rotations in this cycle | 1-5 rotations typical |
| **BitRotationCounter** | int | Cumulative bit rotations (wear) | Increments with each operation |
| **ErrorCode** | int | Error classification | 0=OK, 1=Torque, 2=Angle, 3=Timeout, 4=Multiple |

---

## 🎯 Quality Control Logic

### **CycleOK Determination**
A cycle is marked as `CycleOK=true` when ALL conditions are met:

1. **Torque tolerance**: `|ActualTorque - TargetTorque| ≤ 10%`
2. **Angle tolerance**: `|ActualAngle - TargetAngle| ≤ 30°`
3. **Time range**: `1000ms ≤ CycleTime_ms ≤ 3000ms`

### **Error Codes**
```
0 = No error (CycleOK=true)
1 = Torque error (outside ±10% tolerance)
2 = Angle error (outside ±30° tolerance)
3 = Timeout error (cycle time outside range)
4 = Multiple errors (combination of above)
```

---

## 🔧 IoT Hub Configuration Updates

### **Message Routing Properties**

Your IoT Hub messages now include these **custom properties** for routing:

```json
{
  "deviceType": "screw-robot",
  "alertLevel": "warning",      // "normal" or "warning"
  "qualityStatus": "NOK",        // "OK" or "NOK"
  "errorCode": "1",              // "0" to "4"
  "iothub-creation-time-utc": "2025-11-18T10:30:00.000Z"
}
```

### **Recommended Message Routes**

Create these routes in Azure IoT Hub for quality control:

#### **Route 1: Failed Cycles to Quality Alerts**
```
Name: QualityFailures
Data source: Device Telemetry Messages
Routing query: qualityStatus = 'NOK'
Endpoint: EventHub-QualityAlerts (or Eventstream)
```

#### **Route 2: All Operations to Analytics**
```
Name: AllOperations
Data source: Device Telemetry Messages
Routing query: deviceType = 'screw-robot'
Endpoint: EventHub-Analytics (or Eventstream)
```

#### **Route 3: Error Code Filtering**
```
Name: TorqueErrors
Data source: Device Telemetry Messages
Routing query: errorCode = '1'
Endpoint: EventHub-TorqueAnalysis
```

### **Azure Portal Setup**

1. Go to: **IoT Hub** → `lab-iot01` → **Message routing**
2. Click **+ Add** → **Route**
3. Configure query and endpoint
4. **Save**

---

## 📊 Fabric Eventstream Configuration

### **Phase 1: Update Eventstream Source**

Your existing IoT Hub source remains the same:
- **IoT Hub**: `lab-iot01.azure-devices.net`
- **Consumer group**: `fabric-eventstream`
- **Data format**: **JSON**

✅ No changes needed to source configuration!

### **Phase 2: Add Transformations (Recommended)**

#### **Transformation 1: Filter Failed Cycles**
```
Operation: Filter
Condition: CycleOK == false
Purpose: Route only quality failures for immediate analysis
```

#### **Transformation 2: Calculate Tolerances**
```
Operation: Manage Fields
Add fields:
  - TorqueDeviation = ABS(ActualTorque - TargetTorque) / TargetTorque * 100
  - AngleDeviation = ABS(ActualAngle - TargetAngle)
Purpose: Pre-calculate deviations for easier Power BI analysis
```

#### **Transformation 3: Aggregate by Product**
```
Operation: Group By
Group by: ProductID, MachineID
Window: Tumbling 5 minutes
Aggregations:
  - COUNT(*) as TotalCycles
  - COUNTIF(CycleOK == false) as FailedCycles
  - AVG(ActualTorque) as AvgTorque
  - AVG(CycleTime_ms) as AvgCycleTime
Purpose: Real-time quality metrics per product
```

### **Phase 3: Lakehouse Destination Updates**

#### **Option A: Create New Table (Recommended)**

Create a fresh table with the new schema:

1. **Add destination** → **Lakehouse**
2. Configure:
   ```
   Destination name: screw-tightening-quality
   Lakehouse: [Your lakehouse]
   Delta table: quality_control_data (NEW TABLE)
   Input data format: JSON
   ```
3. **Advanced settings**:
   ```
   Minimum rows: 5,000
   Maximum duration: 300 seconds (5 minutes)
   ```

The new table schema will be:
```
Timestamp: timestamp
MachineID: string
ProductID: string
ScrewPosition: int
TargetTorque: decimal
ActualTorque: decimal
TargetAngle: int
ActualAngle: int
PulseCount: int
CycleOK: boolean
CycleTime_ms: int
SpindleRotationCounter: int
BitRotationCounter: int
ErrorCode: int
```

#### **Option B: Keep Historical Data (Migration Approach)**

If you want to preserve old data:

1. **Rename old table**: `screw_robots_telemetry` → `screw_robots_telemetry_legacy`
2. **Create new table**: `quality_control_data` with new schema
3. **Use both** in Power BI with separate datasets

---

## 📈 Power BI Analytics Updates

### **New Visualizations**

#### **1. Quality Dashboard**
```dax
// Key Metrics
Pass Rate % = 
DIVIDE(
    COUNTROWS(FILTER('quality_control_data', 'quality_control_data'[CycleOK] = TRUE)),
    COUNTROWS('quality_control_data')
) * 100

Failed Cycles = 
COUNTROWS(FILTER('quality_control_data', 'quality_control_data'[CycleOK] = FALSE))

// Error Distribution
Error Type Count = 
SWITCH(
    TRUE(),
    'quality_control_data'[ErrorCode] = 0, "OK",
    'quality_control_data'[ErrorCode] = 1, "Torque Error",
    'quality_control_data'[ErrorCode] = 2, "Angle Error",
    'quality_control_data'[ErrorCode] = 3, "Timeout",
    'quality_control_data'[ErrorCode] = 4, "Multiple",
    "Unknown"
)
```

#### **2. Torque Analysis**
```dax
Avg Torque Deviation % = 
AVERAGEX(
    'quality_control_data',
    ABS('quality_control_data'[ActualTorque] - 'quality_control_data'[TargetTorque]) 
    / 'quality_control_data'[TargetTorque] * 100
)

Torque Out of Spec = 
CALCULATE(
    COUNTROWS('quality_control_data'),
    ABS('quality_control_data'[ActualTorque] - 'quality_control_data'[TargetTorque])
    > 'quality_control_data'[TargetTorque] * 0.1
)
```

#### **3. Product Quality Matrix**
```dax
// Matrix: Products vs Machines
Quality Score = 
VAR PassedCycles = COUNTROWS(FILTER('quality_control_data', 'quality_control_data'[CycleOK] = TRUE))
VAR TotalCycles = COUNTROWS('quality_control_data')
RETURN DIVIDE(PassedCycles, TotalCycles, 0)
```

#### **4. Bit Wear Tracking**
```dax
// Tool maintenance indicator
Avg Bit Rotations = 
AVERAGE('quality_control_data'[BitRotationCounter])

Machines Need Bit Change = 
CALCULATE(
    DISTINCTCOUNT('quality_control_data'[MachineID]),
    'quality_control_data'[BitRotationCounter] > 100000
)
```

### **Recommended Visuals**

1. **Card**: Pass Rate %, Failed Cycles, Avg Cycle Time
2. **Donut Chart**: Error Code distribution
3. **Line Chart**: Pass Rate % over time
4. **Matrix**: ProductID × MachineID with Quality Score
5. **Scatter Plot**: ActualTorque vs ActualAngle (colored by CycleOK)
6. **Bar Chart**: Failed cycles by MachineID
7. **Gauge**: BitRotationCounter (for maintenance alerts)
8. **Table**: Recent failures with ErrorCode details

---

## 🔄 Migration Checklist

### **Pre-Migration**
- [ ] Stop current simulator: `Get-Process python | Stop-Process -Force`
- [ ] Backup current Lakehouse table (if exists)
- [ ] Document current Eventstream configuration

### **Code Updates** ✅
- [x] Updated `telemetry_generator.py` with new schema
- [x] Updated `device_simulator.py` with quality properties
- [x] Updated `generate_historical_data.py` for CSV export

### **Testing**
- [ ] Test simulator with new schema
- [ ] Verify JSON payload in IoT Hub monitoring
- [ ] Check custom properties in message

### **Eventstream Updates**
- [ ] Create new Lakehouse table `quality_control_data`
- [ ] Update Eventstream destination to new table
- [ ] Add quality control transformations
- [ ] Publish changes
- [ ] Verify data ingestion (5-10 minutes)

### **Power BI Updates**
- [ ] Create new dataset from `quality_control_data` table
- [ ] Build quality dashboard with new measures
- [ ] Add torque/angle analysis visuals
- [ ] Configure alerts for pass rate drops

### **Historical Data**
- [ ] Regenerate CSV with new schema
- [ ] Upload to Lakehouse
- [ ] Import as separate table or append to main table

---

## 🚀 Quick Start Commands

### **1. Test New Schema**
```powershell
# Restart simulator with new schema
python main.py
```

### **2. Generate New Historical Data**
```powershell
# Generate 7 days for testing
python generate_historical_data.py --days 7 --output quality_data_7days.csv

# Full 30-day dataset
python generate_historical_data.py --days 30 --output quality_data_30days.csv
```

### **3. Monitor IoT Hub**
```powershell
# Watch messages in real-time
az iot hub monitor-events --hub-name lab-iot01 --consumer-group $Default

# Check specific device
az iot hub monitor-events --hub-name lab-iot01 --device-id screw-robot-001
```

### **4. Verify Message Properties**
```powershell
# Monitor with properties
az iot hub monitor-events --hub-name lab-iot01 --properties all
```

---

## 📚 Key Improvements

### **Business Value**

1. **Quality Control**: Immediate `CycleOK` flag for pass/fail tracking
2. **Root Cause Analysis**: `ErrorCode` identifies specific failure types
3. **Product Tracking**: `ProductID` enables per-product quality metrics
4. **Position Analysis**: `ScrewPosition` reveals problematic assembly points
5. **Tool Maintenance**: `BitRotationCounter` predicts bit replacement needs
6. **Torque Verification**: Actual vs Target comparison validates process
7. **Angle Monitoring**: Ensures proper thread engagement

### **Technical Benefits**

1. **Standard Schema**: Matches industrial automation standards
2. **Flat Structure**: No nested objects, easier SQL queries
3. **Integer Timestamps**: Millisecond precision for cycle time
4. **Boolean Flags**: Simple filtering in Power BI/SQL
5. **Error Codes**: Categorical analysis of failure modes
6. **Cumulative Counters**: Predictive maintenance indicators

---

## 🎯 Next Steps

1. **Run simulator** to verify new data format
2. **Monitor IoT Hub** to confirm messages arriving
3. **Update Eventstream** with new Lakehouse table
4. **Create Power BI dashboard** with quality metrics
5. **Set up alerts** for pass rate drops below 95%
6. **Generate historical data** for training ML models

---

**Your data now follows industrial IoT best practices for quality control! 🏭**
