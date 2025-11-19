# Power BI Predictive Maintenance Training Lab
## Manufacturing Screw Tightening Machine - Maintenance Prediction System

---

## 🎯 Lab Objectives

By the end of this lab, you will be able to:
1. Load historical screwing machine data into Power BI
2. Calculate component lifecycle metrics (bit, spindle wear)
3. Predict maintenance schedules based on usage patterns
4. Create visual alerts for component replacement
5. Build a comprehensive maintenance dashboard

**Duration:** 60-90 minutes  
**Difficulty:** Intermediate  
**Tools Required:** Power BI Desktop, CSV data file

---

## 📁 Lab Prerequisites

### **1. Data File**
You should have generated the historical data CSV file:
```powershell
# Generate 30-day historical data (if not already done)
python generate_historical_data.py --days 30 --output quality_30days.csv
```

**Expected CSV Structure:**
```
Timestamp,MachineID,ProductID,ScrewPosition,TargetTorque,ActualTorque,TargetAngle,ActualAngle,PulseCount,CycleOK,CycleTime_ms,SpindleRotationCounter,BitRotationCounter,ErrorCode
```

### **2. Software**
- Power BI Desktop (latest version)
- Download from: https://powerbi.microsoft.com/desktop/

---

## 📊 STEP 1: Load Data into Power BI

### **1.1 Import CSV File**

1. Open **Power BI Desktop**
2. Click **Home** → **Get Data** → **Text/CSV**
3. Browse to: `quality_30days.csv` (or your generated file)
4. Click **Open**
5. Preview the data and click **Transform Data**

### **1.2 Data Type Configuration**

In Power Query Editor, ensure correct data types:

| Column | Data Type | Action |
|--------|-----------|--------|
| Timestamp | Date/Time | Change type if needed |
| MachineID | Text | Keep as-is |
| ProductID | Text | Keep as-is |
| ScrewPosition | Whole Number | Change if needed |
| TargetTorque | Decimal Number | Change if needed |
| ActualTorque | Decimal Number | Change if needed |
| TargetAngle | Whole Number | Change if needed |
| ActualAngle | Whole Number | Change if needed |
| PulseCount | Whole Number | Change if needed |
| CycleOK | Boolean (True/False) | Change if needed |
| CycleTime_ms | Whole Number | Change if needed |
| SpindleRotationCounter | Whole Number | Change if needed |
| BitRotationCounter | Whole Number | Change if needed |
| ErrorCode | Whole Number | Change if needed |

### **1.3 Add Date/Time Columns**

Add custom columns in Power Query Editor:

**Date Column:**
```m
= Date.From([Timestamp])
```

**Hour Column:**
```m
= Time.Hour([Timestamp])
```

**DayOfWeek Column:**
```m
= Date.DayOfWeek([Timestamp], Day.Monday)
```

Click **Close & Apply** to load the data.

---

## 🔧 STEP 2: Create Component Lifetime Table

### **2.1 Create Component Reference Table**

In Power BI Desktop:
1. Click **Home** → **Enter Data**
2. Create a table named `ComponentLifetime`:

| Component | Lifetime_Cycles | Lifetime_Hours | Cost_USD | Lead_Time_Days |
|-----------|-----------------|----------------|----------|----------------|
| Bit | 100000 | 28 | 150 | 3 |
| Spindle | 500000 | 139 | 800 | 7 |
| Motor | 1000000 | 278 | 1500 | 14 |
| Bearing | 750000 | 208 | 600 | 10 |

3. Click **Load**

### **2.2 Create Relationships**

No direct relationship needed - we'll use LOOKUPVALUE in DAX measures.

---

## 📈 STEP 3: Create DAX Measures for Maintenance Prediction

### **3.1 Basic Metrics**

Create a new measure by clicking **Home** → **New Measure**

**Total Cycles Performed:**
```dax
TotalCycles = COUNTROWS('quality_30days')
```

**Total Failed Cycles:**
```dax
FailedCycles = COUNTROWS(FILTER('quality_30days', 'quality_30days'[CycleOK] = FALSE))
```

**Pass Rate Percentage:**
```dax
PassRate% = 
DIVIDE(
    COUNTROWS(FILTER('quality_30days', 'quality_30days'[CycleOK] = TRUE)),
    COUNTROWS('quality_30days'),
    0
) * 100
```

### **3.2 Bit Wear Calculations**

**Current Bit Rotation Count:**
```dax
CurrentBitRotations = MAX('quality_30days'[BitRotationCounter])
```

**Bit Lifetime (from reference table):**
```dax
BitLifetime = 
LOOKUPVALUE(
    ComponentLifetime[Lifetime_Cycles],
    ComponentLifetime[Component], "Bit"
)
```

**Remaining Bit Life (cycles):**
```dax
RemainingBitLife = [BitLifetime] - [CurrentBitRotations]
```

**Bit Wear Percentage:**
```dax
BitWear% = 
DIVIDE(
    [CurrentBitRotations],
    [BitLifetime],
    0
) * 100
```

### **3.3 Time-Based Predictions**

**Average Cycles Per Hour:**
```dax
CyclesPerHour = 
VAR LastTimestamp = MAX('quality_30days'[Timestamp])
VAR FirstTimestamp = MIN('quality_30days'[Timestamp])
VAR TotalHours = DATEDIFF(FirstTimestamp, LastTimestamp, HOUR)
RETURN
DIVIDE([TotalCycles], TotalHours, 0)
```

**Hours Until Bit Replacement:**
```dax
HoursUntilBitReplacement = 
DIVIDE(
    [RemainingBitLife],
    [CyclesPerHour],
    0
)
```

**Days Until Bit Replacement:**
```dax
DaysUntilBitReplacement = 
DIVIDE(
    [HoursUntilBitReplacement],
    24,
    0
)
```

**Estimated Replacement Date:**
```dax
BitReplacementDate = 
VAR DaysRemaining = [DaysUntilBitReplacement]
VAR LastDate = MAX('quality_30days'[Timestamp])
RETURN
IF(
    DaysRemaining > 0,
    LastDate + DaysRemaining,
    BLANK()
)
```

### **3.4 Component Health Status**

**Bit Health Status:**
```dax
BitHealthStatus = 
VAR WearPercent = [BitWear%]
RETURN
SWITCH(
    TRUE(),
    WearPercent >= 95, "CRITICAL - Replace Now",
    WearPercent >= 80, "WARNING - Schedule Replacement",
    WearPercent >= 60, "CAUTION - Monitor Closely",
    "GOOD"
)
```

**Bit Health Color (for conditional formatting):**
```dax
BitHealthColor = 
VAR WearPercent = [BitWear%]
RETURN
SWITCH(
    TRUE(),
    WearPercent >= 95, "#DC3545",  // Red
    WearPercent >= 80, "#FFC107",  // Yellow
    WearPercent >= 60, "#FD7E14",  // Orange
    "#28A745"                       // Green
)
```

### **3.5 Spindle Wear Calculations**

**Average Spindle Rotations Per Cycle:**
```dax
AvgSpindleRotations = AVERAGE('quality_30days'[SpindleRotationCounter])
```

**Estimated Total Spindle Rotations:**
```dax
EstimatedSpindleRotations = [TotalCycles] * [AvgSpindleRotations]
```

**Spindle Lifetime:**
```dax
SpindleLifetime = 
LOOKUPVALUE(
    ComponentLifetime[Lifetime_Cycles],
    ComponentLifetime[Component], "Spindle"
)
```

**Remaining Spindle Life:**
```dax
RemainingSpindleLife = [SpindleLifetime] - [EstimatedSpindleRotations]
```

**Spindle Wear Percentage:**
```dax
SpindleWear% = 
DIVIDE(
    [EstimatedSpindleRotations],
    [SpindleLifetime],
    0
) * 100
```

**Days Until Spindle Replacement:**
```dax
DaysUntilSpindleReplacement = 
DIVIDE(
    [RemainingSpindleLife],
    ([CyclesPerHour] * [AvgSpindleRotations]),
    0
) / 24
```

### **3.6 Cost Predictions**

**Estimated Maintenance Cost (Next 30 Days):**
```dax
EstimatedMaintenanceCost30Days = 
VAR BitDaysRemaining = [DaysUntilBitReplacement]
VAR SpindleDaysRemaining = [DaysUntilSpindleReplacement]
VAR BitCost = LOOKUPVALUE(ComponentLifetime[Cost_USD], ComponentLifetime[Component], "Bit")
VAR SpindleCost = LOOKUPVALUE(ComponentLifetime[Cost_USD], ComponentLifetime[Component], "Spindle")
RETURN
(IF(BitDaysRemaining <= 30, BitCost, 0)) +
(IF(SpindleDaysRemaining <= 30, SpindleCost, 0))
```

---

## 🎨 STEP 4: Build the Maintenance Dashboard

### **4.1 PAGE 1 — Maintenance Health (Main Dashboard)**

This is your primary operational dashboard focusing on rotation-based maintenance metrics.

#### **A. Top Row — KPI Cards**

1. **Card: Total Rotations**
   - Field: `[CurrentBitRotations]`
   - Format: Whole number with commas
   - Title: "Total Bit Rotations"
   - Subtitle: "Cumulative wear tracking"

2. **Card: Rotations Per Hour**
   - Field: `[CyclesPerHour] * [AvgSpindleRotations]`
   - Create new measure:
   ```dax
   RotationsPerHour = [CyclesPerHour] * [AvgSpindleRotations]
   ```
   - Format: Decimal number (1 decimal place)
   - Title: "Rotations/Hour"

3. **Card: Bit Remaining (Rotations)**
   - Field: `[RemainingBitLife]`
   - Format: Whole number with commas
   - Conditional formatting: Red if <5,000, Yellow if <10,000, Green if >=10,000
   - Title: "Bit Life Remaining"

4. **Card: Spindle Remaining (Rotations)**
   - Field: `[RemainingSpindleLife]`
   - Format: Whole number with commas
   - Conditional formatting: Red if <50,000, Yellow if <100,000, Green if >=100,000
   - Title: "Spindle Life Remaining"

5. **Card: Days Left Until Replacement**
   - Field: Create new measure:
   ```dax
   MinDaysUntilReplacement = 
   VAR BitDays = [DaysUntilBitReplacement]
   VAR SpindleDays = [DaysUntilSpindleReplacement]
   RETURN
   MIN(BitDays, SpindleDays)
   ```
   - Format: Whole number with "days" suffix
   - Background color: Red if <7, Yellow if <14, Green if >=14
   - Title: "Next Maintenance"

#### **B. Middle Section — Status Gauges**

6. **Gauge: Bit Health**
   - Value: `[CurrentBitRotations]`
   - Minimum: 0
   - Maximum: `[BitLifetime]` (100,000)
   - Target: `[BitLifetime] * 0.8` (80,000 rotations = warning threshold)
   - Color ranges:
     - 0-60,000 (0-60%): Green (#28A745)
     - 60,000-80,000 (60-80%): Yellow (#FFC107)
     - 80,000-100,000 (80-100%): Red (#DC3545)
   - Title: "Bit Health (Rotation-Based)"
   - Data labels: On

7. **Gauge: Spindle Health**
   - Value: `[EstimatedSpindleRotations]`
   - Minimum: 0
   - Maximum: `[SpindleLifetime]` (500,000)
   - Target: `[SpindleLifetime] * 0.8` (400,000)
   - Color ranges:
     - 0-300,000 (0-60%): Green
     - 300,000-400,000 (60-80%): Yellow
     - 400,000-500,000 (80-100%): Red
   - Title: "Spindle Health (Rotation-Based)"

8. **Gauge: Gearbox Health (Estimated)**
   - Create new measure:
   ```dax
   GearboxRotations = [EstimatedSpindleRotations] * 3  // Gear ratio 3:1
   GearboxLifetime = 1000000  // 1 million rotations
   GearboxWear% = DIVIDE([GearboxRotations], [GearboxLifetime], 0) * 100
   ```
   - Value: `[GearboxRotations]`
   - Maximum: 1,000,000
   - Target: 800,000
   - Color ranges: Same as above (Green/Yellow/Red)
   - Title: "Gearbox Health (Estimated)"

#### **C. Bottom Section — Trend Charts**

9. **Line Chart: Rotation Count per Hour**
   - X-axis: `Timestamp` (Date hierarchy, drill to Hour)
   - Y-axis: `SUM('quality_30days'[SpindleRotationCounter])`
   - Legend: `MachineID`
   - Show data labels: Off
   - Line style: Smooth
   - Title: "Hourly Rotation Count by Machine"
   - Subtitle: "Monitor production intensity"

10. **Line Chart: Cycle Time Trend (Detect Slow Cycles)**
    - X-axis: `Timestamp` (by Hour)
    - Y-axis: `AVERAGE('quality_30days'[CycleTime_ms])`
    - Reference line: Add at 2000ms (2 seconds = normal threshold)
    - Color: Single color, highlight anomalies
    - Title: "Average Cycle Time (ms)"
    - Subtitle: "Slow cycles may indicate wear"

11. **Line Chart: Torque Trend**
    - X-axis: `Timestamp` (by Hour)
    - Y-axis: 
      - `AVERAGE('quality_30days'[ActualTorque])` (main line)
      - `AVERAGE('quality_30days'[TargetTorque])` (reference line, dashed)
    - Show both as separate series
    - Title: "Torque Trend: Actual vs Target"
    - Subtitle: "Deviation may indicate bit wear"

#### **D. Side Panel — Filters**

12. **Slicer: MachineID**
    - Field: `MachineID`
    - Style: Dropdown or Tile
    - Multi-select: Enabled
    - Select all by default

13. **Slicer: ScrewPosition**
    - Field: `ScrewPosition`
    - Style: Dropdown
    - Multi-select: Enabled

14. **Slicer: Date Range Filter**
    - Field: `Timestamp`
    - Style: Between (range slider)
    - Default: Last 7 days
    - Enable relative date filtering

### **4.2 PAGE 2 — Quality Analysis**

This page focuses on quality metrics and process capability analysis.

#### **A. Top Metrics Cards**

15. **Card: NG Rate %**
    - Create measure:
    ```dax
    NGRate% = 
    DIVIDE(
        COUNTROWS(FILTER('quality_30days', 'quality_30days'[CycleOK] = FALSE)),
        COUNTROWS('quality_30days'),
        0
    ) * 100
    ```
    - Format: Percentage with 2 decimals
    - Conditional formatting: Red if >10%, Yellow if >5%, Green if <=5%
    - Title: "NG Rate %"

16. **Card: Total NG Cycles**
    - Field: `[FailedCycles]`
    - Format: Whole number
    - Title: "Total NG Cycles"

17. **Card: Pass Rate %**
    - Field: `[PassRate%]`
    - Format: Percentage
    - Title: "Pass Rate %"

#### **B. Scatter Plots — Process Capability**

18. **Scatter Plot: Torque vs Target**
    - **X-axis**: `ActualTorque`
    - **Y-axis**: `TargetTorque`
    - **Legend**: `CycleOK`
      - True = Green dots
      - False = Red dots
    - **Size**: Optional, use uniform size
    - **Tooltips**: Add `MachineID`, `ProductID`, `Timestamp`
    - **Reference Lines**:
      - Add Y=X diagonal line (perfect match line)
      - Add ±10% tolerance bands:
        - Upper: Y = X * 1.1
        - Lower: Y = X * 0.9
    - **Title**: "Torque Accuracy: Actual vs Target"
    - **Subtitle**: "Green = OK, Red = NG (±10% tolerance)"

**How to add tolerance bands:**
   - Click on chart → Analytics pane
   - Add "Constant Line" at Y-axis
   - Create calculated measures:
   ```dax
   TargetTorqueUpper = AVERAGE('quality_30days'[TargetTorque]) * 1.1
   TargetTorqueLower = AVERAGE('quality_30days'[TargetTorque]) * 0.9
   ```

19. **Scatter Plot: Angle vs Target**
    - **X-axis**: `ActualAngle`
    - **Y-axis**: `TargetAngle`
    - **Legend**: `CycleOK`
      - True = Green
      - False = Red
    - **Tooltips**: Add `ScrewPosition`, `MachineID`, `ProductID`
    - **Reference Lines**:
      - Y=X diagonal (perfect match)
      - ±30° tolerance bands:
        ```dax
        TargetAngleUpper = AVERAGE('quality_30days'[TargetAngle]) + 30
        TargetAngleLower = AVERAGE('quality_30days'[TargetAngle]) - 30
        ```
    - **Title**: "Angle Accuracy: Actual vs Target"
    - **Subtitle**: "Tolerance: ±30°"

#### **C. Distribution Analysis**

20. **Histogram: Torque Distribution**
    - Visual: Column chart with binned data
    - **X-axis**: `ActualTorque` (create bins)
    - **Y-axis**: Count of records
    - **Bin configuration**:
      - Bin size: 0.5 Nm
      - Range: 10-30 Nm
    - **Overlay**: Normal distribution curve (if available)
    - **Color**: Single color or by `CycleOK`
    - **Title**: "Torque Distribution (Histogram)"
    - **Add mean line** (Analytics pane):
      ```dax
      AvgActualTorque = AVERAGE('quality_30days'[ActualTorque])
      ```

**How to create histogram:**
   1. Insert Column Chart
   2. X-axis: Right-click `ActualTorque` → "Group" → "New Group"
   3. Set bin size: 0.5
   4. Y-axis: Count of `ActualTorque`

21. **Histogram: Angle Distribution**
    - Same configuration as torque
    - **X-axis**: `ActualAngle` (bins of 10°)
    - **Y-axis**: Count
    - **Title**: "Angle Distribution (Histogram)"

#### **D. NG Rate Trend**

22. **Line Chart: NG Rate % per Day**
    - **X-axis**: `Date`
    - **Y-axis**: `[NGRate%]`
    - **Reference line**: 5% (warning threshold)
    - **Color**: Red if above threshold, Green if below
    - **Title**: "Daily NG Rate Trend"
    - **Subtitle**: "Target: <5%"

23. **Stacked Bar Chart: NG by Error Code**
    - **Y-axis**: `ErrorCode`
      - 0 = OK (should not appear in filter)
      - 1 = Torque NG
      - 2 = Angle NG
      - 3 = Timeout NG
      - 4 = Multiple NG
    - **X-axis**: Count of records
    - **Legend**: Optional, use single color
    - **Data labels**: On (show count)
    - **Filter**: `ErrorCode > 0` (exclude OK cycles)
    - **Title**: "NG Distribution by Error Code"

#### **E. Side Panel — Quality Filters**

24. **Slicer: CycleOK**
    - Field: `CycleOK`
    - Style: Dropdown
    - Options: True, False, All

25. **Slicer: ErrorCode**
    - Field: `ErrorCode`
    - Style: List
    - Multi-select: Enabled

### **4.3 PAGE 3 — Maintenance Log & Prediction Table**

This is your maintenance planning page with component lifecycle tracking.

#### **A. Main Component Prediction Table**

26. **Table: Component Maintenance Status**

Create a **calculated table** (not visual table):

```dax
MaintenanceStatus = 
VAR BitRotations = [CurrentBitRotations]
VAR BitLife = [BitLifetime]
VAR BitRemaining = [RemainingBitLife]
VAR BitDaysLeft = [DaysUntilBitReplacement]
VAR BitStatus = 
    SWITCH(
        TRUE(),
        BitDaysLeft < 2, "🔴 CRITICAL",
        BitDaysLeft < 7, "🟠 URGENT",
        BitDaysLeft < 14, "🟡 WARNING",
        "🟢 GOOD"
    )

VAR SpindleRotations = [EstimatedSpindleRotations]
VAR SpindleLife = [SpindleLifetime]
VAR SpindleRemaining = [RemainingSpindleLife]
VAR SpindleDaysLeft = [DaysUntilSpindleReplacement]
VAR SpindleStatus = 
    SWITCH(
        TRUE(),
        SpindleDaysLeft < 3, "🔴 CRITICAL",
        SpindleDaysLeft < 14, "🟠 URGENT",
        SpindleDaysLeft < 30, "🟡 WARNING",
        "🟢 GOOD"
    )

VAR GearboxRotations = SpindleRotations * 3
VAR GearboxLife = 1000000
VAR GearboxRemaining = GearboxLife - GearboxRotations
VAR GearboxDaysLeft = DIVIDE(GearboxRemaining, ([RotationsPerHour] * 3), 0) / 24
VAR GearboxStatus = 
    SWITCH(
        TRUE(),
        GearboxDaysLeft < 7, "🟠 URGENT",
        GearboxDaysLeft < 30, "🟡 WARNING",
        "🟢 GOOD"
    )

VAR BearingRotations = SpindleRotations * 2
VAR BearingLife = 750000
VAR BearingRemaining = BearingLife - BearingRotations
VAR BearingDaysLeft = DIVIDE(BearingRemaining, ([RotationsPerHour] * 2), 0) / 24
VAR BearingStatus = 
    SWITCH(
        TRUE(),
        BearingDaysLeft < 7, "🟠 URGENT",
        BearingDaysLeft < 30, "🟡 WARNING",
        "🟢 GOOD"
    )

RETURN
UNION(
    ROW(
        "Component", "Bit",
        "Total Rotations", BitRotations,
        "Lifetime", BitLife,
        "Remaining", BitRemaining,
        "Days Left", BitDaysLeft,
        "Status", BitStatus
    ),
    ROW(
        "Component", "Spindle",
        "Total Rotations", SpindleRotations,
        "Lifetime", SpindleLife,
        "Remaining", SpindleRemaining,
        "Days Left", SpindleDaysLeft,
        "Status", SpindleStatus
    ),
    ROW(
        "Component", "Gearbox",
        "Total Rotations", GearboxRotations,
        "Lifetime", GearboxLife,
        "Remaining", GearboxRemaining,
        "Days Left", GearboxDaysLeft,
        "Status", GearboxStatus
    ),
    ROW(
        "Component", "Bearing",
        "Total Rotations", BearingRotations,
        "Lifetime", BearingLife,
        "Remaining", BearingRemaining,
        "Days Left", BearingDaysLeft,
        "Status", BearingStatus
    )
)
```

**Display as Table Visual:**
- Columns: All columns from calculated table
- Format:
  - "Total Rotations": Whole number with commas
  - "Lifetime": Whole number with commas
  - "Remaining": Whole number with commas
  - "Days Left": Decimal (1 place) with " days" suffix
  - "Status": Text with emoji

**Conditional Formatting:**
- **Days Left** column:
  - Background color rules:
    - Red: < 7 days
    - Orange: 7-14 days
    - Yellow: 14-30 days
    - Green: > 30 days
  - Font color: White for dark backgrounds

- **Status** column:
  - Font size: 14pt
  - Bold

**Alternative Simpler Approach** (if calculated table is complex):

Create a static table manually:
1. **Home** → **Enter Data**
2. Table name: `ComponentReference`

| Component | Lifetime | Ratio |
|-----------|----------|-------|
| Bit | 100000 | 1 |
| Spindle | 500000 | 1 |
| Gearbox | 1000000 | 3 |
| Bearing | 750000 | 2 |

3. Create measures for each component:

```dax
// Bit Metrics
BitRotations = [CurrentBitRotations]
BitRemaining = [RemainingBitLife]
BitDaysLeft = [DaysUntilBitReplacement]
BitStatus = 
SWITCH(
    TRUE(),
    [BitDaysLeft] < 2, "🔴 CRITICAL",
    [BitDaysLeft] < 7, "🟠 URGENT",
    [BitDaysLeft] < 14, "🟡 WARNING",
    "🟢 GOOD"
)

// Spindle Metrics
SpindleRotations = [EstimatedSpindleRotations]
SpindleRemaining = [RemainingSpindleLife]
SpindleDaysLeft = [DaysUntilSpindleReplacement]
SpindleStatus = 
SWITCH(
    TRUE(),
    [SpindleDaysLeft] < 3, "🔴 CRITICAL",
    [SpindleDaysLeft] < 14, "🟠 URGENT",
    [SpindleDaysLeft] < 30, "🟡 WARNING",
    "🟢 GOOD"
)

// Gearbox Metrics (Estimated)
GearboxRotations = [EstimatedSpindleRotations] * 3
GearboxLifetime = 1000000
GearboxRemaining = [GearboxLifetime] - [GearboxRotations]
GearboxDaysLeft = DIVIDE([GearboxRemaining], ([RotationsPerHour] * 3), 0) / 24
GearboxStatus = 
SWITCH(
    TRUE(),
    [GearboxDaysLeft] < 7, "🟠 URGENT",
    [GearboxDaysLeft] < 30, "🟡 WARNING",
    "🟢 GOOD"
)

// Bearing Metrics (Estimated)
BearingRotations = [EstimatedSpindleRotations] * 2
BearingLifetime = 750000
BearingRemaining = [BearingLifetime] - [BearingRotations]
BearingDaysLeft = DIVIDE([BearingRemaining], ([RotationsPerHour] * 2), 0) / 24
BearingStatus = 
SWITCH(
    TRUE(),
    [BearingDaysLeft] < 7, "🟠 URGENT",
    [BearingDaysLeft] < 30, "🟡 WARNING",
    "🟢 GOOD"
)
```

4. Create **Matrix Visual**:
   - Rows: `ComponentReference[Component]`
   - Values:
     - For "Bit" row: `[BitRotations]`, `[BitRemaining]`, `[BitDaysLeft]`, `[BitStatus]`
     - For "Spindle" row: Use corresponding measures
   - Use conditional formatting on "Days Left" column

#### **B. Maintenance Cost Summary**

27. **Card: Total Maintenance Cost (Next 30 Days)**
    - Field: `[EstimatedMaintenanceCost30Days]`
    - Format: Currency USD
    - Title: "Estimated Cost (30 Days)"

28. **Card: Next Maintenance Date**
    - Create measure:
    ```dax
    NextMaintenanceDate = 
    VAR MinDays = [MinDaysUntilReplacement]
    VAR NextComponent = 
        SWITCH(
            TRUE(),
            [DaysUntilBitReplacement] = MinDays, "Bit",
            [DaysUntilSpindleReplacement] = MinDays, "Spindle",
            "Unknown"
        )
    RETURN
    FORMAT(TODAY() + MinDays, "YYYY-MM-DD") & " (" & NextComponent & ")"
    ```
    - Display as Card
    - Title: "Next Scheduled Maintenance"

#### **C. Recent Failed Cycles Log**

29. **Table: Recent NG Cycles**

**Configuration:**
- **Filter**: `CycleOK = FALSE`
- **Top N**: Show top 50 by `Timestamp` (descending)
- **Columns**:
  - Timestamp (format: YYYY-MM-DD HH:MM:SS)
  - MachineID
  - ProductID
  - ScrewPosition
  - ActualTorque (format: 0.00 Nm)
  - ActualAngle (format: 0°)
  - ErrorCode
  - CycleTime_ms (format: 0 ms)
- **Conditional formatting**:
  - ErrorCode:
    - 1 (Torque): Orange background
    - 2 (Angle): Red background
    - 3 (Timeout): Yellow background
    - 4 (Multiple): Dark red background

**How to configure:**
1. Insert Table visual
2. Add columns from `quality_30days` table
3. Click on visual → Filters pane → Add filter:
   - CycleOK = FALSE
4. Visual level filters → Top N:
   - Show: Top 50
   - By: Timestamp
   - Sort: Descending

#### **D. Maintenance Action Plan**

30. **Text Box: Maintenance Guidelines**

Insert a text box with this content:

```
🔴 CRITICAL (< 2 days):
   → STOP PRODUCTION
   → Replace component immediately
   → Notify maintenance team

🟠 URGENT (< 7 days):
   → Order replacement parts
   → Schedule maintenance window
   → Prepare backup machine

🟡 WARNING (7-30 days):
   → Monitor daily
   → Check inventory
   → Plan preventive maintenance

🟢 GOOD (> 30 days):
   → Normal operation
   → Continue monitoring
```

#### **E. Side Panel — Maintenance Filters**

31. **Slicer: MachineID**
    - Multi-select dropdown
    - Affects all visuals on page

32. **Slicer: Date Range**
    - Between slider
    - Default: Last 30 days

---

## 🎯 STEP 5: Advanced Analytics - Predictive Alerts

### **5.1 Create Alert Measures**

**Critical Maintenance Alert:**
```dax
MaintenanceAlert = 
VAR BitAlert = IF([BitWear%] >= 80, "Bit replacement needed in " & FORMAT([DaysUntilBitReplacement], "0") & " days", BLANK())
VAR SpindleAlert = IF([SpindleWear%] >= 80, "Spindle replacement needed in " & FORMAT([DaysUntilSpindleReplacement], "0") & " days", BLANK())
VAR QualityAlert = IF([PassRate%] < 90, "Quality below 90% - investigate immediately", BLANK())
RETURN
CONCATENATEX(
    FILTER(
        {BitAlert, SpindleAlert, QualityAlert},
        NOT(ISBLANK([Value]))
    ),
    [Value],
    UNICHAR(10)
)
```

**Alert Count:**
```dax
AlertCount = 
VAR BitAlert = IF([BitWear%] >= 80, 1, 0)
VAR SpindleAlert = IF([SpindleWear%] >= 80, 1, 0)
VAR QualityAlert = IF([PassRate%] < 90, 1, 0)
RETURN
BitAlert + SpindleAlert + QualityAlert
```

### **5.2 Add Alert Card to Dashboard**

19. **Card: Active Alerts**
    - Field: `[AlertCount]`
    - Background: Red if > 0
    - Font size: Large
    - Add drill-through to show `[MaintenanceAlert]` text

---

## 📊 STEP 6: Production Efficiency Metrics

### **6.1 Efficiency Measures**

**Average Cycle Time:**
```dax
AvgCycleTime_ms = AVERAGE('quality_30days'[CycleTime_ms])
```

**Cycle Time Variance:**
```dax
CycleTimeVariance = 
VAR AvgTime = [AvgCycleTime_ms]
RETURN
AVERAGEX(
    'quality_30days',
    POWER('quality_30days'[CycleTime_ms] - AvgTime, 2)
)
```

**Hourly Production Rate:**
```dax
HourlyProductionRate = 
DIVIDE(
    3600000,  // milliseconds in an hour
    [AvgCycleTime_ms],
    0
)
```

**Production Efficiency %:**
```dax
ProductionEfficiency% = 
VAR ActualRate = [CyclesPerHour]
VAR TheoreticalRate = [HourlyProductionRate]
RETURN
DIVIDE(ActualRate, TheoreticalRate, 0) * 100
```

### **6.2 Product-Specific Analysis**

**Product Quality Matrix:**
```dax
ProductQualityScore = 
CALCULATE(
    [PassRate%],
    ALLEXCEPT('quality_30days', 'quality_30days'[ProductID])
)
```

20. **Matrix Visual: Product × Machine Quality**
    - Rows: `ProductID`
    - Columns: `MachineID`
    - Values: `[ProductQualityScore]`
    - Conditional formatting: Heatmap (Red <90%, Green >95%)

---

## 🔄 STEP 7: Refresh Configuration

### **7.1 Automatic Refresh Setup**

If connecting to live data:

1. Click **Home** → **Transform Data** → **Data Source Settings**
2. Update file path to point to auto-updated CSV location
3. Set up scheduled refresh:
   - **File** → **Options and Settings** → **Options**
   - **Data Load** → Enable "Background data"

### **7.2 Power BI Service Refresh**

After publishing to Power BI Service:

1. Go to workspace → Dataset settings
2. Configure **Scheduled refresh**:
   - Frequency: Every 15 minutes (if Gateway configured)
   - Or: Daily at specific time
3. Set up **Data Gateway** for automatic CSV folder monitoring

---

## 🎓 STEP 8: Key Insights and Actions

### **Maintenance Triggers**

| Condition | Action | Lead Time |
|-----------|--------|-----------|
| Bit Wear > 95% | **IMMEDIATE** - Stop production, replace bit | 0 days |
| Bit Wear > 80% | **SCHEDULE** - Order replacement, plan downtime | 3-7 days |
| Spindle Wear > 90% | **URGENT** - Schedule spindle maintenance | 7-14 days |
| Pass Rate < 90% | **INVESTIGATE** - Check calibration, tooling | Immediate |
| Pass Rate < 95% | **MONITOR** - Increase inspection frequency | Ongoing |

### **Cost Optimization**

**Calculate Total Cost of Ownership:**
```dax
AnnualMaintenanceCost = 
VAR CyclesPerYear = [CyclesPerHour] * 24 * 365
VAR BitReplacementsPerYear = DIVIDE(CyclesPerYear, [BitLifetime], 0)
VAR SpindleReplacementsPerYear = DIVIDE(CyclesPerYear, [SpindleLifetime], 0)
VAR BitCost = LOOKUPVALUE(ComponentLifetime[Cost_USD], ComponentLifetime[Component], "Bit")
VAR SpindleCost = LOOKUPVALUE(ComponentLifetime[Cost_USD], ComponentLifetime[Component], "Spindle")
RETURN
(BitReplacementsPerYear * BitCost) + (SpindleReplacementsPerYear * SpindleCost)
```

---

## ✅ Lab Completion Checklist

- [ ] CSV data loaded into Power BI
- [ ] Component lifetime table created
- [ ] All DAX measures created (30+ measures)
- [ ] Page 1: Executive dashboard built
- [ ] Page 2: Component health details completed
- [ ] Page 3: Operations log configured
- [ ] Conditional formatting applied
- [ ] Alert system configured
- [ ] Published to Power BI Service (optional)

---

## 📚 Additional Resources

### **Sample DAX Snippets**

**Filter Last 7 Days:**
```dax
Last7DaysCycles = 
CALCULATE(
    [TotalCycles],
    DATESINPERIOD('quality_30days'[Date], MAX('quality_30days'[Date]), -7, DAY)
)
```

**Shift Analysis (Assuming 8-hour shifts):**
```dax
ShiftName = 
VAR HourOfDay = HOUR('quality_30days'[Timestamp])
RETURN
SWITCH(
    TRUE(),
    HourOfDay >= 6 && HourOfDay < 14, "Morning Shift",
    HourOfDay >= 14 && HourOfDay < 22, "Afternoon Shift",
    "Night Shift"
)
```

**Week-over-Week Comparison:**
```dax
WoWCycleChange% = 
VAR CurrentWeek = [TotalCycles]
VAR LastWeek = CALCULATE([TotalCycles], DATEADD('quality_30days'[Date], -7, DAY))
RETURN
DIVIDE(CurrentWeek - LastWeek, LastWeek, 0) * 100
```

---

## 🎯 Expected Outcomes

By completing this lab, you should have:

1. ✅ **Real-time maintenance visibility** - Know exactly when components need replacement
2. ✅ **Cost prediction** - Budget for upcoming maintenance activities
3. ✅ **Quality monitoring** - Immediate alerts when quality degrades
4. ✅ **Production optimization** - Identify efficiency improvement opportunities
5. ✅ **Data-driven decisions** - Replace reactive maintenance with predictive scheduling

---

## 🚀 Next Steps

1. **Extend to Multiple Machines** - Add data from all production lines
2. **Add Supplier Integration** - Auto-order parts when thresholds hit
3. **Mobile Dashboard** - Enable Power BI mobile app for on-floor access
4. **Machine Learning** - Use Azure ML for advanced failure prediction
5. **Real-Time Alerts** - Configure Power Automate to send email/SMS alerts

---

**Congratulations! You've built a complete predictive maintenance system for manufacturing! 🏭📊**
