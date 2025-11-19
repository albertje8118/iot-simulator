# Microsoft Fabric Eventstream Setup Guide

## 📋 Quick Reference - Your IoT Hub Details

**⚠️ Replace these placeholder values with your actual IoT Hub details:**

```
IoT Hub Name: YOUR_IOT_HUB_NAME
Hostname: YOUR_IOT_HUB_NAME.azure-devices.net
Policy Name: service (or iothubowner)
Access Key: YOUR_SHARED_ACCESS_KEY_HERE
Connection String: HostName=YOUR_IOT_HUB_NAME.azure-devices.net;SharedAccessKeyName=service;SharedAccessKey=YOUR_SHARED_ACCESS_KEY_HERE
```

---

## 🚀 Step-by-Step Setup (30 minutes)

### **Phase 1: Create Consumer Group (5 minutes)**

It's best practice to use a dedicated consumer group for Eventstream instead of `$Default`.

**Option A: Azure Portal**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your IoT Hub (e.g., `YOUR_IOT_HUB_NAME`)
3. Select: **Hub settings** → **Built-in endpoints** → **Events**
4. Under **Consumer groups**, add: `fabric-eventstream`
5. Click **Save**

**Option B: Azure CLI** (Run this now)
```powershell
az iot hub consumer-group create --hub-name YOUR_IOT_HUB_NAME --name fabric-eventstream --event-hub-name events
```

---

### **Phase 2: Create Eventstream in Fabric (10 minutes)**

#### **2.1 Access Microsoft Fabric**
1. Go to [Microsoft Fabric Portal](https://app.fabric.microsoft.com)
2. Switch to **Real-Time Intelligence** workload (bottom left)
3. Select your workspace (or create new one)

#### **2.2 Create Eventstream**
1. Click **+ New item** → **Eventstream**
2. Name it: `iot-screw-robots-stream`
3. Click **Create**
4. Eventstream opens in **Edit mode**

#### **2.3 Add IoT Hub Source**
1. Click **Add source** → **External sources**
2. Select **Azure IoT Hub** tile → Click **Connect**

**Configure Connection:**
```
Source name: YOUR_IOT_HUB_NAME-source
IoT Hub: YOUR_IOT_HUB_NAME.azure-devices.net

Connection:
  Connection name: YOUR_IOT_HUB_NAME-connection
  Authentication: Shared Access Key
  Shared Access Key Name: service
  Shared Access Key: YOUR_SHARED_ACCESS_KEY_HERE

Data:
  Consumer group: fabric-eventstream (or $Default if not created)
  Data format: JSON
```

3. Click **Next** → **Review + Create** → **Add**
4. Click **Publish** (top right) to activate

#### **2.4 Verify Data Preview**
- Click on the IoT Hub source node
- Select **Data preview** tab
- You should see messages from your 10 screw robots! 🎉

---

### **Phase 3: Add Transformations (Optional, 10 minutes)**

Add operators to filter and shape your data before storing:

#### **Example 1: Filter Failed Cycles (for Quality Issues)**
1. Click **Operations** → **Filter**
2. Connect IoT Hub source to Filter operator
3. Configure:
   ```
   Condition: CycleOK == false
   ```
   Purpose: Route only quality failures for immediate analysis

#### **Example 2: Calculate Quality Deviations**
1. Click **Operations** → **Manage Fields**
2. Connect previous operator to this one
3. Configure:
   - **Add fields**:
     - `TorqueDeviation = ABS(ActualTorque - TargetTorque) / TargetTorque * 100`
     - `AngleDeviation = ABS(ActualAngle - TargetAngle)`
   - **Remove fields**: `EventProcessedUtcTime`, `PartitionId`, `EventEnqueuedUtcTime`

#### **Example 3: Aggregate Quality Metrics Per Product**
1. Click **Operations** → **Group By**
2. Configure:
   ```
   Group by: ProductID, MachineID
   Window: Tumbling - 5 minutes
   Aggregations:
     - COUNT(*) as TotalCycles
     - COUNTIF(CycleOK == false) as FailedCycles
     - AVG(ActualTorque) as AvgTorque
     - AVG(CycleTime_ms) as AvgCycleTime
   ```

---

### **Phase 4: Add Warehouse Destination (10 minutes)**

You have two options:

#### **Option A: Lakehouse (Recommended for Power BI)**

**Best for:** Historical storage, Power BI reports, long-term analytics

1. Click **Add destination** → **Lakehouse**
2. Connect your last operator/source to Lakehouse
3. Configure:
   ```
   Destination name: quality-control-lakehouse-dest
   Workspace: [Your workspace]
   Lakehouse: [Select or create new]
   Delta table: quality_control_data (NEW - for industrial schema)
   Input data format: JSON
   ```
   
   ⚠️ **Important**: Use a NEW table name to avoid schema conflicts with old data

4. **Advanced settings:**
   ```
   Minimum rows: 10,000 (adjust based on data volume)
   Maximum duration: 60 seconds
   ```
   - Lower values = more frequent writes = more files
   - Your simulator sends ~10 devices × 1 event/minute = ~600 events/hour
   - Suggested: 1,000 rows or 300 seconds (5 minutes)

5. Click **Save** → **Publish**

#### **Option B: Eventhouse (Recommended for Real-Time)**

**Best for:** Real-time KQL queries, flexible schema, time-series analysis

1. Click **Add destination** → **Eventhouse**
2. Choose: **Event processing before ingestion** (if you added transformations) or **Direct ingestion**
3. Configure:
   ```
   Destination name: quality-control-eventhouse-dest
   Workspace: [Your workspace]
   Eventhouse: [Select or create new]
   KQL Database: [Select database]
   Target table: quality_control_data
   Input data format: JSON
   ```

4. Click **Save** → **Publish**

#### **💡 Pro Tip: Use Both!**

Create a **Derived Stream** to send data to both destinations:
1. Add **Derived Stream** from your transformations
2. Add **Eventhouse** for real-time queries (hot data, last 7-30 days)
3. Add **Lakehouse** for historical Power BI reports
4. Enable **OneLake availability** on Eventhouse to unify access

---

### **Phase 5: Verification (5 minutes)**

#### **5.1 Check Eventstream Status**
- All nodes should show **green checkmarks** ✅
- Destination status: **Ingesting** (might take 2-5 minutes initially)

#### **5.2 Verify Data in Lakehouse**
1. Open your Lakehouse
2. Find table: `quality_control_data`
3. Click **View data**
4. You should see rows with quality control data (MachineID, ProductID, CycleOK, etc.)!

#### **5.3 Query Data in Eventhouse (if using)**
```kql
quality_control_data
| where Timestamp > ago(1h)
| summarize 
    TotalCycles = count(),
    FailedCycles = countif(CycleOK == false),
    PassRate = round(100.0 * countif(CycleOK == true) / count(), 2),
    AvgTorque = avg(ActualTorque)
  by MachineID, ProductID
| order by PassRate asc
```

---

## 📊 Power BI Setup

Once data is in Lakehouse:

### **Create Power BI Report**
1. Open your Lakehouse in Fabric
2. Click **New Power BI dataset**
3. Select `quality_control_data` table
4. Click **Create**
5. Build visualizations:
   - **Card**: Pass Rate % (CycleOK = true / total)
   - **Donut Chart**: Error Code distribution
   - **Line chart**: Pass Rate % over `Timestamp` by `MachineID`
   - **Matrix**: ProductID × MachineID with Pass Rate %
   - **Scatter Plot**: ActualTorque vs ActualAngle (colored by CycleOK)
   - **Table**: Recent failures with ErrorCode details

### **Sample DAX Measures**
```dax
Pass Rate % = 
DIVIDE(
    COUNTROWS(FILTER('quality_control_data', 
        'quality_control_data'[CycleOK] = TRUE)),
    COUNTROWS('quality_control_data'),
    0
) * 100

Failed Cycles = 
COUNTROWS(FILTER('quality_control_data', 
    'quality_control_data'[CycleOK] = FALSE))

Avg Torque Deviation % = 
AVERAGEX(
    'quality_control_data',
    ABS('quality_control_data'[ActualTorque] - 'quality_control_data'[TargetTorque]) 
    / 'quality_control_data'[TargetTorque] * 100
)

Error Type = 
SWITCH(
    'quality_control_data'[ErrorCode],
    0, "OK",
    1, "Torque Error",
    2, "Angle Error",
    3, "Timeout",
    4, "Multiple Errors",
    "Unknown"
)

Machines Need Bit Change = 
CALCULATE(
    DISTINCTCOUNT('quality_control_data'[MachineID]),
    'quality_control_data'[BitRotationCounter] > 100000
)
```

---

## 🔍 Monitoring & Troubleshooting

### **Common Issues**

| Problem | Solution |
|---------|----------|
| **No data preview** | Check simulator is running: `python main.py` |
| **Connection failed** | Verify access key hasn't been regenerated |
| **Schema errors** | Ensure data format is JSON (not Avro/CSV) |
| **High latency** | Upgrade Fabric capacity to F4+ SKU |
| **Data not appearing** | Wait 2-5 minutes for initial ingestion setup |

### **Verify Simulator is Sending Data**

```powershell
# Monitor events in real-time
az iot hub monitor-events --hub-name YOUR_IOT_HUB_NAME --consumer-group $Default

# Check specific device
az iot hub monitor-events --hub-name YOUR_IOT_HUB_NAME --device-id screw-robot-001
```

### **Check IoT Hub Metrics** (Azure Portal)
1. Navigate to your IoT Hub (e.g., `YOUR_IOT_HUB_NAME`)
2. Select: **Monitoring** → **Metrics**
3. Add metric: **Telemetry messages sent**
4. Should see ~10 messages per minute from your simulator

---

## 🎯 Expected Data Schema

Your telemetry data structure (industrial quality control format):
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

**Field Descriptions:**
- **CycleOK**: Pass/fail status (±10% torque, ±30° angle, 1-3s time)
- **ErrorCode**: 0=OK, 1=Torque, 2=Angle, 3=Timeout, 4=Multiple
- **ProductID**: 8 variants (PROD-A100, PROD-A200, PROD-B150, PROD-C300, PROD-D250, PROD-E175, PROD-F225, PROD-G190)
- **ScrewPosition**: 1-8 positions on assembly
- **TargetTorque**: 15-25 Nm (based on speed)
- **BitRotationCounter**: Cumulative wear tracking for maintenance

**Quality Control Logic:**
- Torque tolerance: ±10% of target
- Angle tolerance: ±30° of target
- Time range: 1000-3000 ms
- All conditions must pass for `CycleOK=true`

---

## 🎓 Next Steps

1. ✅ **Create consumer group** for Eventstream
2. ✅ **Set up Eventstream** with IoT Hub source
3. ✅ **Add transformations** (filter anomalies, aggregate metrics)
4. ✅ **Configure destination** (Lakehouse for Power BI, Eventhouse for KQL)
5. ✅ **Build Power BI dashboard** for predictive maintenance
6. ✅ **Set up alerts** in Fabric Activator for critical anomalies
7. ✅ **Test hot-reload** by changing `ANOMALY_RATE` in `.env`

---

## 📚 Official Documentation

- [Add Azure IoT Hub Source to Eventstream](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/add-source-azure-iot-hub)
- [Add Lakehouse Destination](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/add-destination-lakehouse)
- [Process Events with Transformations](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/process-events-using-event-processor-editor)
- [Tutorial: Transform and Stream to Lakehouse](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/transform-and-stream-real-time-events-to-lakehouse)

---

## 💡 Tips & Best Practices

1. **Consumer Groups**: Always use dedicated consumer group (not `$Default`) in production
2. **Schema Stability**: Keep your telemetry structure consistent to avoid Lakehouse schema issues
3. **Capacity Planning**: F4 SKU minimum recommended for production workloads
4. **Data Retention**: Eventhouse for hot data (7-30 days), Lakehouse for cold storage
5. **Transformation Strategy**: Filter and aggregate early to reduce storage costs
6. **Monitoring**: Set up Azure Monitor alerts for IoT Hub throttling or errors

---

**Your simulator is already running and sending data! 🚀**  
**Just configure Eventstream to start collecting in Fabric.**
