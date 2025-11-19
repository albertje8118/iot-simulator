# Daily Report & Checklist Application - Training Lab

**Power Platform Solution for Press/Molding Team**

Build a complete daily reporting and checklist system using Microsoft Forms, Power Automate, SharePoint Lists, and Power BI for monthly analytics.

---

## 📋 Lab Overview

**Duration**: 2-3 hours  
**Difficulty**: Beginner to Intermediate  
**Prerequisites**: Microsoft 365 E3/Business Premium license

### What You'll Build

A production floor reporting system where Press/Molding operators can:
1. Submit daily production reports via Microsoft Forms
2. Complete daily safety/quality checklists
3. View and manage reports in SharePoint Lists
4. Generate automated monthly reports in Power BI

### Business Value

✅ **Paperless reporting** - Eliminate manual logbooks  
✅ **Real-time visibility** - Managers see data immediately  
✅ **Trend analysis** - Power BI tracks performance over time  
✅ **Accountability** - Timestamped entries with user tracking  
✅ **Compliance** - Automated quality/safety documentation

---

## 🎯 Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Microsoft Forms (2 Forms)                      │
│  ┌──────────────────────┐  ┌──────────────────────────┐   │
│  │  Daily Production    │  │   Daily Checklist        │   │
│  │  Report              │  │   (Safety/Quality)       │   │
│  └──────────┬───────────┘  └───────────┬──────────────┘   │
│             │                           │                   │
└─────────────┼───────────────────────────┼───────────────────┘
              │                           │
              ↓                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Power Automate (2 Flows)                   │
│  ┌─────────────────────────┐  ┌────────────────────────┐   │
│  │ Flow 1: Production      │  │ Flow 2: Checklist      │   │
│  │ - Get form response     │  │ - Get form response    │   │
│  │ - Parse data            │  │ - Parse data           │   │
│  │ - Create SharePoint item│  │ - Create item          │   │
│  │ - Send confirmation     │  │ - Send email if issues │   │
│  └──────────┬──────────────┘  └────────┬───────────────┘   │
└─────────────┼──────────────────────────┼───────────────────┘
              │                          │
              ↓                          ↓
┌─────────────────────────────────────────────────────────────┐
│              SharePoint Lists (2 Lists)                     │
│  ┌──────────────────────────┐  ┌─────────────────────┐     │
│  │ Press_Daily_Reports      │  │ Press_Daily_Checklist│    │
│  │ - Date                   │  │ - Date               │    │
│  │ - Shift (A/B/C)          │  │ - Shift              │    │
│  │ - Machine ID             │  │ - Machine ID         │    │
│  │ - Parts Produced         │  │ - Safety Check       │    │
│  │ - Scrap Count            │  │ - Quality Check      │    │
│  │ - Downtime (minutes)     │  │ - Equipment Status   │    │
│  │ - Issues/Comments        │  │ - Issues Found       │    │
│  └──────────┬───────────────┘  └──────┬──────────────┘     │
└─────────────┼──────────────────────────┼───────────────────┘
              │                          │
              └────────────┬─────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │      Power BI          │
              │  Monthly Dashboard     │
              │  - Production KPIs     │
              │  - Downtime Analysis   │
              │  - Quality Trends      │
              │  - Shift Performance   │
              └────────────────────────┘
```

---

## 📝 Lab 1: Create SharePoint Lists (15 minutes)

### Step 1.1: Create Production Reports List

1. Navigate to your SharePoint site (e.g., `https://yourtenant.sharepoint.com/sites/manufacturing`)
2. Click **+ New** → **List**
3. Select **Blank list**
   - **Name**: `Press_Daily_Reports`
   - **Description**: `Daily production reports from Press/Molding team`
4. Click **Create**

### Step 1.2: Add Columns to Production Reports List

Click **+ Add column** and create these columns:

| Column Name | Column Type | Required | Settings |
|------------|-------------|----------|----------|
| **ReportDate** | Date and time | Yes | Include time: No, Default: Today |
| **Shift** | Choice | Yes | Choices: A, B, C, Default: A |
| **MachineID** | Single line of text | Yes | Max length: 50 |
| **Operator** | Person | Yes | Allow multiple: No |
| **PartsProduced** | Number | Yes | Min: 0, Decimals: 0 |
| **TargetProduction** | Number | Yes | Min: 0, Default: 1000 |
| **ScrapCount** | Number | Yes | Min: 0, Default: 0 |
| **DowntimeMinutes** | Number | Yes | Min: 0, Default: 0 |
| **DowntimeReason** | Choice | No | Choices: Material Shortage, Machine Breakdown, Quality Hold, Changeover, Other |
| **Issues** | Multiple lines of text | No | Type: Plain text |
| **Comments** | Multiple lines of text | No | Type: Plain text |

**Column Configuration Tips:**
- For **ReportDate**: Settings → Default value → Today
- For **Operator**: Will auto-populate with form submitter
- For **PartsProduced**: Use Number with no decimals

### Step 1.3: Create Checklist List

1. On the same SharePoint site, click **+ New** → **List**
2. Select **Blank list**
   - **Name**: `Press_Daily_Checklist`
   - **Description**: `Daily safety and quality checklists`
3. Click **Create**

### Step 1.4: Add Columns to Checklist List

| Column Name | Column Type | Required | Settings |
|------------|-------------|----------|----------|
| **ChecklistDate** | Date and time | Yes | Include time: No, Default: Today |
| **Shift** | Choice | Yes | Choices: A, B, C |
| **MachineID** | Single line of text | Yes | Max length: 50 |
| **Inspector** | Person | Yes | Allow multiple: No |
| **SafetyCheck_GuardsInPlace** | Yes/No | Yes | Default: Yes |
| **SafetyCheck_EmergencyStop** | Yes/No | Yes | Default: Yes |
| **SafetyCheck_PPEWorn** | Yes/No | Yes | Default: Yes |
| **QualityCheck_FirstPart** | Yes/No | Yes | Default: Yes |
| **QualityCheck_Dimensions** | Yes/No | Yes | Default: Yes |
| **QualityCheck_VisualInspection** | Yes/No | Yes | Default: Yes |
| **EquipmentStatus** | Choice | Yes | Choices: Operational, Needs Maintenance, Down, Default: Operational |
| **IssuesFound** | Multiple lines of text | No | Type: Plain text |
| **CorrectiveAction** | Multiple lines of text | No | Type: Plain text |

---

## 📋 Lab 2: Create Microsoft Forms (30 minutes)

### Step 2.1: Create Daily Production Report Form

1. Go to [Microsoft Forms](https://forms.microsoft.com)
2. Click **+ New Form**
3. **Title**: `Press/Molding - Daily Production Report`
4. **Description**:
   ```
   Daily production report for Press/Molding operations.
   Submit this form at the end of each shift.
   ```

### Step 2.2: Add Questions to Production Form

**Question 1: Report Date**
- Type: **Date**
- Question: `Report Date`
- Required: ✅ Yes

**Question 2: Shift**
- Type: **Choice**
- Question: `Which shift are you reporting for?`
- Options:
  - A - Day Shift (6:00 AM - 2:00 PM)
  - B - Afternoon Shift (2:00 PM - 10:00 PM)
  - C - Night Shift (10:00 PM - 6:00 AM)
- Required: ✅ Yes

**Question 3: Machine ID**
- Type: **Text**
- Question: `Machine/Press Number`
- Long answer: ❌ No
- Required: ✅ Yes

**Question 4: Parts Produced**
- Type: **Text** (with Number restriction)
- Question: `Total Parts Produced This Shift`
- Long answer: ❌ No
- Restrictions: Number between 0 and 10000
- Required: ✅ Yes

**Question 5: Target Production**
- Type: **Text**
- Question: `Target Production for This Shift`
- Default: 1000
- Required: ✅ Yes

**Question 6: Scrap Count**
- Type: **Text**
- Question: `Total Scrap/Reject Parts`
- Default: 0
- Required: ✅ Yes

**Question 7: Downtime**
- Type: **Text**
- Question: `Total Downtime (minutes)`
- Default: 0
- Required: ✅ Yes

**Question 8: Downtime Reason**
- Type: **Choice**
- Question: `Primary Downtime Reason (if any)`
- Options:
  - Material Shortage
  - Machine Breakdown
  - Quality Hold
  - Changeover
  - Scheduled Maintenance
  - Other
- Required: ❌ No

**Question 9: Issues**
- Type: **Text**
- Question: `Any issues or problems encountered?`
- Long answer: ✅ Yes
- Required: ❌ No

**Question 10: Additional Comments**
- Type: **Text**
- Question: `Additional Comments`
- Long answer: ✅ Yes
- Required: ❌ No

### Step 2.3: Configure Form Settings

1. Click **...** (More options) → **Settings**
2. **Who can fill out this form**: Only people in my organization
3. **One response per person**: ❌ No (allow multiple submissions per shift)
4. **Record name**: ✅ Yes (track who submitted)
5. **Collect email**: ✅ Yes
6. Click **Save**

### Step 2.4: Create Daily Checklist Form

1. Click **+ New Form**
2. **Title**: `Press/Molding - Daily Safety & Quality Checklist`
3. **Description**:
   ```
   Daily safety and quality checklist to be completed at start of shift.
   All checks must pass before starting production.
   ```

### Step 2.5: Add Questions to Checklist Form

**Question 1: Checklist Date**
- Type: **Date**
- Question: `Inspection Date`
- Required: ✅ Yes

**Question 2: Shift**
- Type: **Choice**
- Question: `Shift`
- Options: A, B, C
- Required: ✅ Yes

**Question 3: Machine ID**
- Type: **Text**
- Question: `Machine/Press Number`
- Required: ✅ Yes

**Section: Safety Checks**

**Question 4: Guards in Place**
- Type: **Choice**
- Question: `All safety guards properly installed and secured?`
- Options: ✅ Pass, ❌ Fail
- Required: ✅ Yes

**Question 5: Emergency Stop**
- Type: **Choice**
- Question: `Emergency stop button tested and functional?`
- Options: ✅ Pass, ❌ Fail
- Required: ✅ Yes

**Question 6: PPE**
- Type: **Choice**
- Question: `All operators wearing required PPE?`
- Options: ✅ Pass, ❌ Fail
- Required: ✅ Yes

**Section: Quality Checks**

**Question 7: First Part Inspection**
- Type: **Choice**
- Question: `First part inspection completed and passed?`
- Options: ✅ Pass, ❌ Fail
- Required: ✅ Yes

**Question 8: Dimension Check**
- Type: **Choice**
- Question: `Critical dimensions within specification?`
- Options: ✅ Pass, ❌ Fail
- Required: ✅ Yes

**Question 9: Visual Inspection**
- Type: **Choice**
- Question: `Visual inspection for defects completed?`
- Options: ✅ Pass, ❌ Fail
- Required: ✅ Yes

**Question 10: Equipment Status**
- Type: **Choice**
- Question: `Overall Equipment Status`
- Options:
  - ✅ Operational - Ready for production
  - ⚠️ Needs Maintenance - Can operate but schedule service
  - ❌ Down - Cannot operate
- Required: ✅ Yes

**Question 11: Issues Found**
- Type: **Text**
- Question: `Describe any issues or failures found during inspection`
- Long answer: ✅ Yes
- Required: ❌ No

**Question 12: Corrective Action**
- Type: **Text**
- Question: `Corrective action taken (if any)`
- Long answer: ✅ Yes
- Required: ❌ No

### Step 2.6: Get Form IDs

1. For each form, click **Share**
2. Copy the form link - it looks like:
   ```
   https://forms.office.com/Pages/ResponsePage.aspx?id=XXXXXXXXXX
   ```
3. Save the form ID (the part after `id=`) - you'll need this for Power Automate

---

## ⚡ Lab 3: Create Power Automate Flows (45 minutes)

### Step 3.1: Create Production Report Flow

1. Go to [Power Automate](https://make.powerautomate.com)
2. Click **+ Create** → **Automated cloud flow**
3. **Flow name**: `Press Production Report to SharePoint`
4. **Choose your flow's trigger**: Search for "Microsoft Forms"
5. Select **When a new response is submitted (Microsoft Forms)**
6. Click **Create**

### Step 3.2: Configure Production Report Flow

**Step 1: Trigger Configuration**
- **Form Id**: Select `Press/Molding - Daily Production Report`

**Step 2: Get Response Details**
1. Click **+ New step**
2. Search for **Microsoft Forms**
3. Select **Get response details**
4. **Form Id**: Select `Press/Molding - Daily Production Report`
5. **Response Id**: From dynamic content, select `Response Id`

**Step 3: Create SharePoint Item**
1. Click **+ New step**
2. Search for **SharePoint**
3. Select **Create item**
4. **Site Address**: Select your SharePoint site
5. **List Name**: Select `Press_Daily_Reports`

**Map Form Fields to SharePoint Columns:**

| SharePoint Column | Dynamic Content from Form |
|-------------------|---------------------------|
| Title | Enter: `Production Report - [Machine ID] - [Report Date]` |
| ReportDate | Report Date |
| Shift | Which shift are you reporting for? |
| MachineID | Machine/Press Number |
| Operator | Responders' Email |
| PartsProduced | Total Parts Produced This Shift |
| TargetProduction | Target Production for This Shift |
| ScrapCount | Total Scrap/Reject Parts |
| DowntimeMinutes | Total Downtime (minutes) |
| DowntimeReason | Primary Downtime Reason (if any) |
| Issues | Any issues or problems encountered? |
| Comments | Additional Comments |

**Dynamic Title Expression:**
```
concat('Production Report - ', outputs('Get_response_details')?['body/r3c6f8e0b5d4e4c8f9a1b2c3d4e5f6a7'], ' - ', outputs('Get_response_details')?['body/r1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6'])
```

**Step 4: Send Confirmation Email (Optional)**
1. Click **+ New step**
2. Search for **Office 365 Outlook**
3. Select **Send an email (V2)**
4. **To**: Responders' Email
5. **Subject**: `Production Report Submitted - [Machine ID]`
6. **Body**:
```html
<p>Hi,</p>

<p>Your daily production report has been successfully submitted:</p>

<ul>
  <li><strong>Date:</strong> [Report Date]</li>
  <li><strong>Shift:</strong> [Shift]</li>
  <li><strong>Machine:</strong> [Machine ID]</li>
  <li><strong>Parts Produced:</strong> [Parts Produced]</li>
  <li><strong>Target:</strong> [Target Production]</li>
  <li><strong>Achievement:</strong> [Calculate Percentage]%</li>
  <li><strong>Scrap:</strong> [Scrap Count]</li>
  <li><strong>Downtime:</strong> [Downtime] minutes</li>
</ul>

<p>Thank you for your report.</p>
```

**Calculate Achievement Percentage Expression:**
```
mul(div(float(outputs('Get_response_details')?['body/r3']), float(outputs('Get_response_details')?['body/r4'])), 100)
```

### Step 3.3: Test Production Report Flow

1. Click **Save** (top right)
2. Click **Test** → **Manually** → **Test**
3. Go to your Microsoft Form and submit a test entry
4. Return to Power Automate and verify:
   - ✅ All steps succeeded (green checkmarks)
   - ✅ New item created in SharePoint list
   - ✅ Confirmation email received (if configured)

### Step 3.4: Create Checklist Flow

1. Click **+ Create** → **Automated cloud flow**
2. **Flow name**: `Press Daily Checklist to SharePoint`
3. **Trigger**: **When a new response is submitted (Microsoft Forms)**
4. Select checklist form

**Configure Checklist Flow:**

**Step 1: Get Response Details**
- Same as production flow, but select checklist form

**Step 2: Create SharePoint Item**
- **List Name**: `Press_Daily_Checklist`

**Map Fields:**

| SharePoint Column | Form Response |
|-------------------|---------------|
| Title | `Checklist - [Machine ID] - [Date]` |
| ChecklistDate | Inspection Date |
| Shift | Shift |
| MachineID | Machine/Press Number |
| Inspector | Responders' Email |
| SafetyCheck_GuardsInPlace | Convert "Pass" to Yes, "Fail" to No |
| SafetyCheck_EmergencyStop | Convert Pass/Fail to Yes/No |
| SafetyCheck_PPEWorn | Convert Pass/Fail to Yes/No |
| QualityCheck_FirstPart | Convert Pass/Fail to Yes/No |
| QualityCheck_Dimensions | Convert Pass/Fail to Yes/No |
| QualityCheck_VisualInspection | Convert Pass/Fail to Yes/No |
| EquipmentStatus | Overall Equipment Status |
| IssuesFound | Describe any issues |
| CorrectiveAction | Corrective action taken |

**Converting Pass/Fail to Yes/No:**

For each Yes/No field, use this expression:
```
if(equals(outputs('Get_response_details')?['body/r4'], 'Pass'), true, false)
```

**Step 3: Condition - Check for Failures**

1. Click **+ New step** → **Condition**
2. **Condition**: Check if ANY safety or quality check failed
3. Expression:
```
or(
  equals(outputs('Get_response_details')?['body/r4'], 'Fail'),
  equals(outputs('Get_response_details')?['body/r5'], 'Fail'),
  equals(outputs('Get_response_details')?['body/r6'], 'Fail'),
  equals(outputs('Get_response_details')?['body/r7'], 'Fail'),
  equals(outputs('Get_response_details')?['body/r8'], 'Fail'),
  equals(outputs('Get_response_details')?['body/r9'], 'Fail')
)
```

**If Yes (Failure Detected):**

1. **Send an email (V2)** to Supervisor
   - **To**: `supervisor@yourcompany.com`
   - **Subject**: `🚨 URGENT: Checklist Failure - Machine [Machine ID]`
   - **Importance**: High
   - **Body**:
   ```html
   <p style="color: red;"><strong>⚠️ CRITICAL ALERT</strong></p>
   
   <p>A checklist failure has been reported. Immediate attention required.</p>
   
   <p><strong>Details:</strong></p>
   <ul>
     <li><strong>Date:</strong> [Checklist Date]</li>
     <li><strong>Shift:</strong> [Shift]</li>
     <li><strong>Machine:</strong> [Machine ID]</li>
     <li><strong>Inspector:</strong> [Inspector Name]</li>
     <li><strong>Equipment Status:</strong> [Status]</li>
   </ul>
   
   <p><strong>Failed Checks:</strong></p>
   [List of failed items]
   
   <p><strong>Issues Found:</strong><br/>
   [Issues description]</p>
   
   <p><strong>Corrective Action:</strong><br/>
   [Corrective action]</p>
   
   <p>View full details in SharePoint: <a href="[SharePoint List URL]">Press Daily Checklist</a></p>
   ```

2. **Create a planner task** (Optional)
   - **Task title**: `Resolve Checklist Failure - [Machine ID]`
   - **Assigned to**: Maintenance team
   - **Priority**: Urgent

**If No (All Checks Passed):**

1. **Send an email (V2)** to Inspector
   - **To**: Responders' Email
   - **Subject**: `✅ Checklist Approved - Machine [Machine ID]`
   - **Body**:
   ```html
   <p>All safety and quality checks passed. Machine approved for production.</p>
   
   <p><strong>Checklist Summary:</strong></p>
   <ul>
     <li>Date: [Date]</li>
     <li>Machine: [Machine ID]</li>
     <li>Status: ✅ All checks passed</li>
   </ul>
   
   <p>Safe operations!</p>
   ```

### Step 3.5: Test Checklist Flow

1. Save and test with both scenarios:
   - ✅ All checks pass
   - ❌ At least one check fails
2. Verify correct email routing and urgency

---

## 📊 Lab 4: Create Power BI Monthly Report (45 minutes)

### Step 4.1: Connect Power BI to SharePoint

1. Open **Power BI Desktop**
2. Click **Get Data** → **More...**
3. Search for **SharePoint Online List**
4. Click **Connect**
5. **Enter SharePoint Site URL**: `https://yourtenant.sharepoint.com/sites/manufacturing`
6. Click **OK**
7. Sign in with your Microsoft 365 account
8. **Navigator**: Select both lists:
   - ✅ Press_Daily_Reports
   - ✅ Press_Daily_Checklist
9. Click **Transform Data**

### Step 4.2: Transform Production Reports Data

**In Power Query Editor:**

1. **Select Press_Daily_Reports table**

2. **Remove unnecessary columns:**
   - Right-click column headers → Remove columns:
     - ID, ContentType, Modified, Created (keep Created By for tracking)
     - OData__ columns
     - Attachments, Edit, ItemChildCount, FolderChildCount

3. **Rename columns** for clarity:
   - `Title` → `ReportID`
   - `ReportDate` → `Date`
   - `PartsProduced` → `Produced`
   - `TargetProduction` → `Target`
   - `ScrapCount` → `Scrap`
   - `DowntimeMinutes` → `Downtime`

4. **Change data types:**
   - `Date`: Date
   - `Produced`: Whole Number
   - `Target`: Whole Number
   - `Scrap`: Whole Number
   - `Downtime`: Whole Number

5. **Add calculated columns:**

   **Achievement Percentage:**
   - Add Column → Custom Column
   - Name: `AchievementPct`
   - Formula: `= [Produced] / [Target] * 100`

   **Scrap Rate:**
   - Add Column → Custom Column
   - Name: `ScrapRate`
   - Formula: `= [Scrap] / [Produced] * 100`

   **Good Parts:**
   - Add Column → Custom Column
   - Name: `GoodParts`
   - Formula: `= [Produced] - [Scrap]`

   **Month Name:**
   - Add Column → Custom Column
   - Name: `MonthYear`
   - Formula: `= Date.ToText([Date], "MMM yyyy")`

   **Week Number:**
   - Add Column → Custom Column
   - Name: `WeekNumber`
   - Formula: `= Date.WeekOfYear([Date])`

6. Click **Close & Apply**

### Step 4.3: Transform Checklist Data

1. **Select Press_Daily_Checklist table**

2. **Remove unnecessary columns** (same as reports)

3. **Add calculated column:**

   **Pass Rate:**
   - Add Column → Custom Column
   - Name: `PassRate`
   - Formula:
   ```
   = (
       if [SafetyCheck_GuardsInPlace] then 1 else 0 +
       if [SafetyCheck_EmergencyStop] then 1 else 0 +
       if [SafetyCheck_PPEWorn] then 1 else 0 +
       if [QualityCheck_FirstPart] then 1 else 0 +
       if [QualityCheck_Dimensions] then 1 else 0 +
       if [QualityCheck_VisualInspection] then 1 else 0
     ) / 6 * 100
   ```

   **Any Failures:**
   - Add Column → Custom Column
   - Name: `HasFailures`
   - Formula:
   ```
   = not (
       [SafetyCheck_GuardsInPlace] and
       [SafetyCheck_EmergencyStop] and
       [SafetyCheck_PPEWorn] and
       [QualityCheck_FirstPart] and
       [QualityCheck_Dimensions] and
       [QualityCheck_VisualInspection]
     )
   ```

4. Click **Close & Apply**

### Step 4.4: Create Relationships

1. Click **Model** view (left sidebar)
2. **Create relationship**:
   - Drag `Date` from `Press_Daily_Reports` to `ChecklistDate` in `Press_Daily_Checklist`
   - Relationship: Many-to-One
   - Cross filter direction: Both

### Step 4.5: Create DAX Measures

Click **Data** view, select `Press_Daily_Reports` table, click **New Measure**:

**Production Measures:**

```dax
Total Parts Produced = SUM(Press_Daily_Reports[Produced])
```

```dax
Total Target = SUM(Press_Daily_Reports[Target])
```

```dax
Overall Achievement = 
DIVIDE([Total Parts Produced], [Total Target], 0) * 100
```

```dax
Total Scrap = SUM(Press_Daily_Reports[Scrap])
```

```dax
Scrap Rate = 
DIVIDE([Total Scrap], [Total Parts Produced], 0) * 100
```

```dax
Total Downtime Hours = 
SUM(Press_Daily_Reports[Downtime]) / 60
```

```dax
Average Downtime Per Shift = 
AVERAGE(Press_Daily_Reports[Downtime])
```

```dax
Total Good Parts = 
SUM(Press_Daily_Reports[GoodParts])
```

**Checklist Measures:**

```dax
Total Checklists = COUNTROWS(Press_Daily_Checklist)
```

```dax
Checklists with Failures = 
CALCULATE(
    COUNTROWS(Press_Daily_Checklist),
    Press_Daily_Checklist[HasFailures] = TRUE
)
```

```dax
Checklist Compliance Rate = 
DIVIDE(
    [Total Checklists] - [Checklists with Failures],
    [Total Checklists],
    0
) * 100
```

**Time Intelligence:**

```dax
Previous Month Production = 
CALCULATE(
    [Total Parts Produced],
    DATEADD(Press_Daily_Reports[Date], -1, MONTH)
)
```

```dax
MoM Production Change = 
[Total Parts Produced] - [Previous Month Production]
```

```dax
MoM Production Change % = 
DIVIDE([MoM Production Change], [Previous Month Production], 0) * 100
```

### Step 4.6: Build Dashboard - Page 1: Production Overview

**Page Name**: `Monthly Production Overview`

**Visual 1: KPI Cards (Top Row)**

1. **Card 1 - Total Production**
   - Value: `Total Parts Produced`
   - Callout value color: Blue
   - Data label: `{value:,} parts`

2. **Card 2 - Achievement**
   - Value: `Overall Achievement`
   - Data label: `{value:.1f}%`
   - Callout value color: Green if >95%, Orange if 90-95%, Red if <90%

3. **Card 3 - Scrap Rate**
   - Value: `Scrap Rate`
   - Data label: `{value:.2f}%`
   - Callout value color: Green if <2%, Orange if 2-5%, Red if >5%

4. **Card 4 - Downtime**
   - Value: `Total Downtime Hours`
   - Data label: `{value:.1f} hours`

**Visual 2: Production Trend (Line Chart)**
- **X-axis**: Date (by day)
- **Y-axis**: Total Parts Produced
- **Legend**: Shift
- **Add Target Line**: Add constant line at daily target
- **Title**: `Daily Production Trend`

**Visual 3: Shift Performance (Clustered Column Chart)**
- **X-axis**: Shift
- **Y-axis**: Total Parts Produced, Total Target
- **Title**: `Production by Shift`

**Visual 4: Machine Performance (Table)**
- **Columns**:
  - MachineID
  - Total Parts Produced
  - Overall Achievement
  - Total Scrap
  - Scrap Rate
  - Average Downtime Per Shift
- **Conditional formatting**:
  - Achievement: Green >95%, Red <90%
  - Scrap Rate: Green <2%, Red >5%

**Visual 5: Downtime Analysis (Pie Chart)**
- **Legend**: DowntimeReason
- **Values**: Total Downtime Hours
- **Title**: `Downtime by Reason`

**Visual 6: Month-over-Month Comparison (Card)**
- **Value**: MoM Production Change %
- **Show trend indicator**: Up arrow (green) or down arrow (red)

### Step 4.7: Build Dashboard - Page 2: Quality & Compliance

**Page Name**: `Quality & Safety Compliance`

**Visual 1: Compliance KPIs**

1. **Card - Compliance Rate**
   - Value: `Checklist Compliance Rate`
   - Target: 100%
   - Callout color: Green if 100%, Red if <100%

2. **Card - Total Inspections**
   - Value: `Total Checklists`

3. **Card - Failures**
   - Value: `Checklists with Failures`
   - Callout color: Red

**Visual 2: Checklist Pass Rate Trend (Line Chart)**
- **X-axis**: ChecklistDate
- **Y-axis**: Average PassRate
- **Title**: `Daily Checklist Pass Rate`
- **Target line**: 100%

**Visual 3: Equipment Status Distribution (Donut Chart)**
- **Legend**: EquipmentStatus
- **Values**: Count of checklists
- **Title**: `Equipment Status Summary`

**Visual 4: Safety Checks Matrix (Matrix Visual)**
- **Rows**: MachineID
- **Columns**: 
  - SafetyCheck_GuardsInPlace
  - SafetyCheck_EmergencyStop
  - SafetyCheck_PPEWorn
- **Values**: Count (show green ✓ for TRUE, red ✗ for FALSE)
- **Title**: `Safety Checks by Machine`

**Visual 5: Quality Checks Matrix**
- **Rows**: MachineID
- **Columns**:
  - QualityCheck_FirstPart
  - QualityCheck_Dimensions
  - QualityCheck_VisualInspection
- **Values**: Pass rate %

**Visual 6: Issues Log (Table)**
- **Columns**:
  - ChecklistDate
  - Shift
  - MachineID
  - IssuesFound
  - CorrectiveAction
- **Filter**: Only show rows where HasFailures = TRUE
- **Title**: `Recent Issues Requiring Attention`

### Step 4.8: Add Slicers and Filters

Add these slicers to both pages:

1. **Date Range Slicer**
   - Field: Date or ChecklistDate
   - Type: Between
   - Default: Last 30 days

2. **Month Slicer**
   - Field: MonthYear
   - Type: Dropdown
   - Allow multiple selections

3. **Shift Slicer**
   - Field: Shift
   - Type: Buttons (A, B, C, All)

4. **Machine Slicer**
   - Field: MachineID
   - Type: Dropdown

### Step 4.9: Publish to Power BI Service

1. Click **Publish** (top ribbon)
2. **Select destination**: Choose your workspace
3. Click **Select**
4. Once published, click **Open '[Report Name]' in Power BI**

### Step 4.10: Schedule Data Refresh

1. In Power BI Service, go to **Workspaces** → Your workspace
2. Find the dataset → Click **...** → **Settings**
3. **Data source credentials**: Click **Edit credentials**
4. **Authentication method**: OAuth2
5. Click **Sign in**
6. **Scheduled refresh**:
   - Toggle **Keep your data up to date**: ✅ On
   - **Refresh frequency**: Daily
   - **Time**: 6:00 AM (or after shift ends)
   - Click **Apply**

---

## 📱 Lab 5: Mobile Access & QR Codes (15 minutes)

### Step 5.1: Create QR Codes for Forms

1. For each Microsoft Form, click **Share**
2. Copy the short link (e.g., `https://forms.office.com/r/XXXXX`)
3. Generate QR code using [QR Code Generator](https://www.qr-code-generator.com/)
4. **Customize QR Code**:
   - Add logo (company logo)
   - Add label: "Daily Production Report" or "Daily Checklist"
   - Colors: Match company branding
5. Download as PNG (high resolution)

### Step 5.2: Print and Display QR Codes

**Recommended Locations:**
- At each Press/Molding machine station
- Break room bulletin board
- Entrance to production floor
- Supervisor desk

**Printed Materials:**
- 8.5" x 11" laminated poster
- 4" x 6" desk cards
- Label on each machine control panel

**Instructions on Poster:**
```
📱 SCAN TO SUBMIT DAILY REPORT

1. Scan QR code with phone camera
2. Complete form (takes 2-3 minutes)
3. Submit before end of shift

✅ Required for all shifts
```

### Step 5.3: Mobile Access Instructions

**For Operators:**
1. Install **Microsoft 365** mobile app (iOS/Android)
2. Sign in with work account
3. Access forms from app or scan QR code
4. Forms auto-save progress
5. Works offline (submits when online)

---

## 🔍 Lab 6: Testing & Validation (20 minutes)

### Test Scenario 1: End-to-End Production Report

1. **Submit Form**:
   - Fill out production report form
   - Use realistic data:
     - Machine: PRESS-01
     - Shift: A
     - Parts: 950
     - Target: 1000
     - Scrap: 15
     - Downtime: 30 minutes
   - Submit

2. **Verify Power Automate**:
   - Go to Power Automate → My flows
   - Check run history (should show success)
   - Verify all actions completed

3. **Verify SharePoint**:
   - Open `Press_Daily_Reports` list
   - New item should appear
   - All fields populated correctly
   - Operator name recorded

4. **Verify Email**:
   - Check inbox for confirmation email
   - Verify data matches submission

5. **Verify Power BI**:
   - Refresh dataset (if not auto-refreshed)
   - Check dashboard shows new data
   - Verify KPIs updated

### Test Scenario 2: Checklist with Failures

1. **Submit Checklist** with at least one failure:
   - Guards in Place: ❌ Fail
   - Issues: "Safety guard damaged on left side"
   - Corrective Action: "Maintenance notified, guard replaced"

2. **Verify Alert Email**:
   - Supervisor should receive urgent email
   - Email should highlight failure
   - Contains all relevant details

3. **Verify SharePoint**:
   - Item created in checklist list
   - Yes/No fields correctly mapped

4. **Verify Power BI**:
   - Compliance rate decreases
   - Failure appears in issues log table

### Test Scenario 3: Multiple Shifts

1. Submit reports for all three shifts (A, B, C)
2. Verify data segregation by shift in Power BI
3. Compare shift performance metrics

---

## 📈 Lab 7: Usage Guidelines & Best Practices (10 minutes)

### For Operators

**Daily Production Report:**
- ✅ Submit at **end of each shift**
- ✅ Be accurate with counts (verify before submitting)
- ✅ Document all downtime and reasons
- ✅ Report any quality issues immediately
- ⏱️ Takes 2-3 minutes to complete

**Daily Checklist:**
- ✅ Complete at **start of shift** before production
- ✅ Do not skip safety checks
- ✅ Report all failures immediately to supervisor
- ✅ Document corrective actions taken
- ⚠️ Do NOT start production if any check fails

### For Supervisors

**Daily Tasks:**
- Review all submitted reports by end of day
- Follow up on any downtime >30 minutes
- Address checklist failures immediately
- Verify scrap rates are within limits

**Weekly Tasks:**
- Review Power BI dashboard trends
- Identify machines with recurring issues
- Plan maintenance based on downtime patterns
- Recognize high-performing shifts

**Monthly Tasks:**
- Generate and review monthly report
- Share performance summary with management
- Set targets for next month
- Schedule training if needed

### Data Quality Tips

**Ensure Accurate Data:**
1. Verify part counts before submitting
2. Record downtime immediately (don't estimate later)
3. Be specific in issue descriptions
4. Update target production if changed
5. Double-check machine ID

**Common Mistakes to Avoid:**
- ❌ Estimating production counts
- ❌ Forgetting to submit report
- ❌ Submitting duplicate reports
- ❌ Leaving issues blank when problems occurred
- ❌ Skipping checklist steps

---

## 🔧 Lab 8: Troubleshooting (Reference)

### Issue: Form Not Submitting

**Symptoms**: "An error occurred" message  
**Solutions**:
1. Check internet connection
2. Verify you're signed in with work account
3. Try refreshing the page
4. Clear browser cache
5. Try different browser

### Issue: Flow Failed

**Symptoms**: Email not received, data not in SharePoint  
**Solutions**:
1. Go to Power Automate → My flows
2. Click on failed flow → View run history
3. Click on failed run to see error details
4. Common fixes:
   - **Permission denied**: Re-authenticate SharePoint connection
   - **Column not found**: Verify SharePoint column names match exactly
   - **Type mismatch**: Check data type conversions

### Issue: Power BI Not Updating

**Symptoms**: Dashboard shows old data  
**Solutions**:
1. Check scheduled refresh status
2. Manually refresh: Dataset → ... → Refresh now
3. Verify connection credentials
4. Check refresh history for errors
5. Re-publish report if needed

### Issue: QR Code Not Working

**Symptoms**: Scans but doesn't open form  
**Solutions**:
1. Verify QR code contains correct URL
2. Check form sharing settings (should be "People in organization")
3. Regenerate QR code if corrupted
4. Test with different QR code reader app

---

## 📊 Sample Data for Testing

Use this data to populate your forms for realistic testing:

### Production Report Samples

**Shift A - Good Performance:**
- Machine: PRESS-01
- Parts: 1050
- Target: 1000
- Scrap: 8
- Downtime: 10 min (Scheduled Break)

**Shift B - Below Target:**
- Machine: PRESS-02
- Parts: 875
- Target: 1000
- Scrap: 25
- Downtime: 90 min (Material Shortage)

**Shift C - Excellent:**
- Machine: PRESS-03
- Parts: 1200
- Target: 1000
- Scrap: 5
- Downtime: 0 min

### Checklist Samples

**Normal Operations:**
- All safety checks: ✅ Pass
- All quality checks: ✅ Pass
- Equipment: Operational

**Maintenance Needed:**
- Guards: ✅ Pass
- Emergency Stop: ✅ Pass
- PPE: ✅ Pass
- First Part: ❌ Fail (dimensions off)
- Equipment: Needs Maintenance
- Issues: "Part dimensions 0.5mm over spec"
- Action: "Adjusted tooling, re-ran first part inspection - PASS"

---

## 🎓 Lab Summary

### What You Built

✅ **Microsoft Forms**: 2 forms for data collection  
✅ **Power Automate**: 2 automated flows for data processing  
✅ **SharePoint Lists**: 2 structured data backends  
✅ **Power BI Dashboard**: 2-page monthly report with KPIs  
✅ **Mobile Access**: QR codes for easy form access  
✅ **Alerting System**: Automated notifications for failures

### Skills Learned

- SharePoint list design and column types
- Microsoft Forms best practices
- Power Automate flow creation and testing
- SharePoint connector configuration
- DAX measures and calculated columns
- Power BI visualization techniques
- Mobile-friendly solutions
- Production data analysis

### Business Impact

- **Time Saved**: 15-20 minutes per shift (no paper forms)
- **Data Accuracy**: Real-time validation, no transcription errors
- **Visibility**: Instant access to production metrics
- **Compliance**: Automated safety/quality tracking
- **Decision Making**: Data-driven insights from Power BI

### Next Steps

1. **Customize**: Adapt forms to your specific needs
2. **Expand**: Add more machines, shifts, or metrics
3. **Integrate**: Connect to ERP or MES systems
4. **Automate**: Add more Power Automate actions (e.g., Teams notifications)
5. **Train**: Roll out to all operators with training sessions

---

## 📚 Additional Resources

**Microsoft Learn:**
- [Microsoft Forms Documentation](https://support.microsoft.com/forms)
- [Power Automate for SharePoint](https://learn.microsoft.com/power-automate/sharepoint-overview)
- [Power BI with SharePoint](https://learn.microsoft.com/power-bi/connect-data/service-sharepoint-online-list)

**Community:**
- [Power Platform Community](https://powerusers.microsoft.com/)
- [Power BI Community](https://community.powerbi.com/)

**Templates:**
- Download pre-built templates from Microsoft template gallery
- Customize and deploy faster

---

## ✅ Completion Checklist

- [ ] SharePoint lists created with all columns
- [ ] Production report form configured
- [ ] Checklist form configured
- [ ] Production report flow tested
- [ ] Checklist flow tested with failures
- [ ] Power BI connected to SharePoint
- [ ] DAX measures created
- [ ] Dashboard visuals completed
- [ ] Data refresh scheduled
- [ ] QR codes generated and printed
- [ ] End-to-end testing completed
- [ ] Operators trained
- [ ] Supervisors trained
- [ ] Documentation distributed

---

**🎉 Congratulations!** You've built a complete daily reporting and checklist system for manufacturing operations!

**Total Lab Time**: ~2-3 hours  
**Maintenance**: Minimal (mostly automatic)  
**ROI**: High (time savings, data quality, compliance)

---

**Need Help?** Contact your Microsoft 365 administrator or Power Platform Center of Excellence.
