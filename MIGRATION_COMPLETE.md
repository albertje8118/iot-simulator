# ✅ Schema Migration Complete

## What Changed

### ✅ **New Industrial Schema Implemented**

**Old Schema (Sensor-focused):**
- deviceId, eventId, timestamp
- rotationCount, duration, speed
- temperature, vibration, powerConsumption
- operationalHours, componentHealth
- isAnomaly, anomalyType (pre-classified)

**New Schema (Quality Control-focused):**
- **Timestamp** - ISO 8601 UTC
- **MachineID** - Device identifier
- **ProductID** - 8 product variants (PROD-A100 to PROD-G190)
- **ScrewPosition** - 1-8 positions on assembly
- **TargetTorque** - Target torque in Nm (15-25 Nm)
- **ActualTorque** - Measured torque with variance
- **TargetAngle** - Target rotation angle (degrees)
- **ActualAngle** - Measured angle with variance
- **PulseCount** - Encoder pulses (4 per rotation)
- **CycleOK** - Boolean quality status
- **CycleTime_ms** - Cycle duration in milliseconds
- **SpindleRotationCounter** - Rotations per cycle
- **BitRotationCounter** - Cumulative wear tracking
- **ErrorCode** - 0=OK, 1=Torque, 2=Angle, 3=Timeout, 4=Multiple

---

## Files Updated

### ✅ Core Application Files

1. **`telemetry_generator.py`**
   - Added product catalog (8 variants)
   - Torque calculations (target 15-25 Nm based on speed)
   - Angle calculations (target = rotations × 360°)
   - Quality determination logic (±10% torque, ±30° angle, 1-3s time)
   - Error code classification
   - Bit rotation counter tracking

2. **`device_simulator.py`**
   - Updated message properties: `qualityStatus` (OK/NOK), `errorCode`
   - Alert level based on `CycleOK` instead of health score
   - Log messages show CycleOK and ErrorCode

3. **`generate_historical_data.py`**
   - Updated CSV columns to new schema
   - Removed flattening logic (no nested structures)
   - Added bit rotation counter to statistics

4. **`main.py`**
   - No changes needed (uses generator interface)

---

## Testing Results

### ✅ Real-Time Simulator
```
✅ All 10 devices connected successfully
✅ Messages sent with new schema
✅ Custom properties: qualityStatus, errorCode, alertLevel
✅ Logs show: "Sent message #1 (CycleOK: True, Error: 0)"
✅ BitRotationCounter increments correctly
```

### ✅ Historical Data Generator
```
✅ Generated sample_quality_data.csv (1 day, 14,410 records)
✅ File size: 1.52 MB
✅ 14 columns matching new schema
✅ CSV header verified
✅ Sample data shows products, positions, torque/angle values
```

---

## IoT Hub & Eventstream Configuration

### 🔄 **What to Update**

#### **1. IoT Hub (No Changes Required)**
- ✅ Connection remains same: `lab-iot01.azure-devices.net`
- ✅ Devices still authenticated
- ✅ Messages flowing normally
- ✅ New custom properties automatically included

#### **2. Message Routing (Optional - Add These)**

**Quality Failures Route:**
```
Name: QualityFailures
Query: qualityStatus = 'NOK'
Endpoint: EventHub or Eventstream
```

**Error Type Routing:**
```
Name: TorqueErrors
Query: errorCode = '1'
Endpoint: Separate analysis endpoint
```

#### **3. Eventstream Updates (Required)**

**Current State:**
- Source: IoT Hub (`lab-iot01`) ✅ Keep as-is
- Consumer Group: `fabric-eventstream` ✅ Already created
- Format: JSON ✅ Correct

**Action Required:**
- **Create NEW Lakehouse table**: `quality_control_data`
- **Update destination** to point to new table
- **Publish changes**

**Why New Table?**
- Old schema had 15 columns (nested componentHealth)
- New schema has 14 columns (flat structure)
- Schema incompatibility would cause ingestion errors
- Preserves old data if needed

**Steps:**
1. In Eventstream editor, **Add destination** → **Lakehouse**
2. Select/create: `quality_control_data` table
3. Input format: JSON
4. **Publish**
5. Wait 5-10 minutes for first data
6. Verify in Lakehouse

#### **4. Recommended Transformations**

**Filter Failed Cycles:**
```
Filter: CycleOK == false
→ Route to quality_alerts table
```

**Calculate Deviations:**
```
Manage Fields:
  Add: TorqueDeviation = ABS(ActualTorque - TargetTorque) / TargetTorque * 100
  Add: AngleDeviation = ABS(ActualAngle - TargetAngle)
```

**Aggregate Quality Metrics:**
```
Group By: ProductID, MachineID
Window: Tumbling 5 minutes
Aggregations:
  - COUNT(*) as TotalCycles
  - COUNTIF(CycleOK == false) as FailedCycles
  - AVG(ActualTorque) as AvgTorque
```

---

## Power BI Dashboard Updates

### 🎯 **New Visualizations to Create**

#### **1. Quality KPIs (Cards)**
```dax
Pass Rate % = 
DIVIDE(
    COUNTROWS(FILTER(quality_control_data, quality_control_data[CycleOK] = TRUE)),
    COUNTROWS(quality_control_data)
) * 100

Failed Cycles Today = 
CALCULATE(
    COUNTROWS(FILTER(quality_control_data, quality_control_data[CycleOK] = FALSE)),
    quality_control_data[Timestamp] >= TODAY()
)
```

#### **2. Error Analysis (Donut Chart)**
```dax
Error Type = 
SWITCH(
    quality_control_data[ErrorCode],
    0, "OK",
    1, "Torque Error",
    2, "Angle Error",
    3, "Timeout",
    4, "Multiple Errors",
    "Unknown"
)
```

#### **3. Product Quality Matrix**
```
Rows: ProductID
Columns: MachineID
Values: Pass Rate %
Conditional Formatting: Green >95%, Yellow 90-95%, Red <90%
```

#### **4. Torque Control Chart (Line Chart)**
```
X-axis: Timestamp
Y-axis: ActualTorque
Series: MachineID
Reference lines: TargetTorque ±10%
```

#### **5. Tool Maintenance Tracker (Table)**
```
Columns: MachineID, BitRotationCounter, Avg CycleTime_ms
Sort by: BitRotationCounter DESC
Alert: BitRotationCounter > 100,000
```

---

## Migration Checklist

### ✅ **Completed**
- [x] Updated `telemetry_generator.py` with industrial schema
- [x] Updated `device_simulator.py` with quality properties
- [x] Updated `generate_historical_data.py` for CSV export
- [x] Tested real-time simulator (10 devices working)
- [x] Generated sample CSV (14,410 records, 1.52 MB)
- [x] Verified new schema in logs and CSV
- [x] Created migration guide documentation

### 🔄 **Todo: Eventstream & Lakehouse**
- [ ] **Stop old Eventstream ingestion** (or keep for comparison)
- [ ] **Create new Lakehouse table**: `quality_control_data`
- [ ] **Update Eventstream destination** to new table
- [ ] **Add quality control transformations** (optional but recommended)
- [ ] **Publish Eventstream** changes
- [ ] **Wait 5-10 minutes** for data to appear
- [ ] **Query new table** to verify schema

### 🔄 **Todo: Power BI**
- [ ] **Create new dataset** from `quality_control_data`
- [ ] **Build quality dashboard** with KPIs
- [ ] **Add error analysis** visuals
- [ ] **Create product-machine matrix**
- [ ] **Set up alerts** for pass rate < 95%

### 🔄 **Todo: Historical Data**
- [ ] **Generate full 30-day dataset**:
  ```powershell
  python generate_historical_data.py --days 30 --output quality_30days.csv
  ```
- [ ] **Upload CSV to Lakehouse** (Files section)
- [ ] **Load as Delta table** or append to existing table

---

## Quick Commands

### **Start Real-Time Simulator**
```powershell
python main.py
```

### **Generate Historical Data**
```powershell
# 7 days (for testing)
python generate_historical_data.py --days 7 --output quality_7days.csv

# Full 30 days (~60 MB)
python generate_historical_data.py --days 30 --output quality_30days.csv

# 5-minute resolution (smaller file)
python generate_historical_data.py --interval 5 --output quality_5min.csv
```

### **Monitor IoT Hub Messages**
```powershell
# Real-time monitoring
az iot hub monitor-events --hub-name lab-iot01 --consumer-group $Default

# With all properties
az iot hub monitor-events --hub-name lab-iot01 --properties all

# Specific device
az iot hub monitor-events --hub-name lab-iot01 --device-id screw-robot-001
```

### **Stop Simulator**
```powershell
# Graceful shutdown
Press Ctrl+C in simulator window

# Force stop
Get-Process python | Stop-Process -Force
```

---

## Business Benefits

### 📊 **Quality Control**
- **Real-time pass/fail tracking** with `CycleOK` field
- **Immediate error classification** with `ErrorCode`
- **Product-specific quality metrics** via `ProductID`
- **Position analysis** to identify problematic assembly points

### 🔧 **Predictive Maintenance**
- **Bit wear tracking** with `BitRotationCounter`
- **Cycle time monitoring** for performance degradation
- **Torque trending** to detect motor issues
- **Angle deviation** to identify mechanical wear

### 📈 **Process Optimization**
- **Target vs Actual comparison** for torque and angle
- **Per-product yield analysis**
- **Machine-to-machine comparison**
- **Shift and operator performance tracking** (add shift field later)

---

## Support Documentation

1. **`SCHEMA_MIGRATION_GUIDE.md`** - Detailed field descriptions, IoT Hub routing, Eventstream transformations, Power BI DAX measures
2. **`FABRIC_EVENTSTREAM_SETUP.md`** - Original Eventstream setup guide (still valid for source configuration)
3. **`README.md`** - Original project documentation

---

## Next Steps

1. ✅ **Simulator is running** with new schema
2. 🔄 **Update Eventstream** to ingest to new Lakehouse table
3. 🔄 **Build Power BI dashboard** with quality metrics
4. 🔄 **Generate 30-day historical data** for training
5. 🔄 **Set up alerts** for quality failures

---

**Your IoT solution now follows industrial automation standards for quality control! 🏭✅**
