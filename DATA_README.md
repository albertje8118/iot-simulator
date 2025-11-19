# Sample Data

This directory contains sample datasets for testing the IoT Predictive Maintenance solution.

## 📁 Files

### `sample_screw_machine_data.csv` (Included in Repo)
**Size**: ~100 KB  
**Records**: Small sample dataset for quick testing  
**Usage**: Initial testing of IoT simulator and data pipeline

**Schema**:
```
DeviceId, EventProcessedUtcTime, PartitionId, EventEnqueuedUtcTime,
Temperature, Vibration, MotorSpeed, PowerConsumption, ScrewingDuration,
TorqueApplied, BitRotationCount, MotorHealth, BearingHealth, ErrorCount,
AnomalyScore, OperationalHours, LastMaintenanceDate, ComponentAge
```

---

### `sample_quality_data.csv` (Generate or Download)
**Size**: ~46 MB  
**Records**: ~30 days of telemetry (10 devices × 1,440 records/day)  
**Usage**: ML model training and validation

**Note**: This file is **excluded from Git** due to size (see `.gitignore`).

#### How to Generate:

```bash
python generate_historical_data.py
```

This creates 30 days of synthetic telemetry data with:
- 10 simulated devices
- Realistic bit rotation patterns
- 3-5 replacement cycles per machine
- Configurable anomaly injection
- Component degradation patterns

#### Alternative: Download Pre-Generated

If available, download from:
- [Release Assets](https://github.com/yourusername/iot-predictive-maintenance/releases)
- [Azure Blob Storage](https://yourstorageaccount.blob.core.windows.net/datasets/sample_quality_data.csv)

---

### `historical_telemetry_30days.csv` (Generate or Download)
**Size**: ~60 MB  
**Records**: Full historical dataset with extended metrics  
**Usage**: Advanced ML training and performance benchmarking

**Note**: This file is **excluded from Git** due to size.

#### How to Generate:

Already generated when you run the IoT simulator for 30 days or use:
```bash
python generate_historical_data.py --days 30 --output historical_telemetry_30days.csv
```

---

## 🚀 Quick Start

### Option 1: Use Small Sample (Fastest)
```bash
# Use sample_screw_machine_data.csv (already in repo)
# Good for: Initial testing, understanding schema
```

### Option 2: Generate 30-Day Dataset
```bash
# Generate full 30-day dataset
python generate_historical_data.py

# This creates sample_quality_data.csv (~46 MB)
# Good for: ML training, full pipeline testing
# Time: ~5-10 minutes
```

### Option 3: Run Live Simulator
```bash
# Start IoT simulator and collect real-time data
python main.py

# Let it run for 1-30 days
# Good for: Production-like testing, real-time pipeline
```

---

## 📊 Data Schema

### Core Fields (All Files)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `DeviceId` | String | Unique device identifier | `screw-robot-001` |
| `EventProcessedUtcTime` | DateTime | When event was processed | `2025-11-19T10:30:00Z` |
| `Temperature` | Float | Operating temperature (°C) | `72.5` |
| `Vibration` | Float | Vibration level (g-force) | `0.8` |
| `MotorSpeed` | Int | Motor RPM | `1800` |
| `BitRotationCount` | Int | Cumulative rotations since last replacement | `124567` |
| `TorqueApplied` | Float | Torque in Newton-meters | `4.2` |
| `ScrewingDuration` | Float | Operation duration (seconds) | `2.3` |

### Health Metrics

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `MotorHealth` | Float | 0.0-1.0 | Motor health score (1.0 = perfect) |
| `BearingHealth` | Float | 0.0-1.0 | Bearing condition score |
| `AnomalyScore` | Float | 0.0-1.0 | Anomaly detection score (0 = normal) |
| `ComponentAge` | Int | Days | Days since last component replacement |

### Maintenance Fields

| Field | Type | Description |
|-------|------|-------------|
| `LastMaintenanceDate` | DateTime | Last maintenance timestamp |
| `OperationalHours` | Float | Total operating hours |
| `ErrorCount` | Int | Cumulative error count |

---

## 🎯 Dataset Characteristics

### Replacement Events
- **Frequency**: Every 5-7 days per machine
- **Detection**: `BitRotationCount` resets to ~0
- **Max Rotations**: ~1,200,000 - 1,500,000 before replacement

### Anomalies (5% of records)
- **Temperature spikes**: >85°C
- **Vibration spikes**: >2.0 g-force  
- **Speed drops**: <1530 RPM (15% below normal)
- **Duration outliers**: >4 seconds

### Degradation Patterns (if enabled)
- **Linear degradation**: Health decreases 0.001 per operational hour
- **Accelerated wear**: Near end of bit life (<100,000 rotations remaining)
- **Recovery after maintenance**: Health resets to 1.0 after replacement

---

## 🔍 Data Quality Checks

Before using data for ML training:

```python
import pandas as pd

df = pd.read_csv('sample_quality_data.csv')

# Check for missing values
print(df.isnull().sum())

# Check data types
print(df.dtypes)

# Verify replacement cycles
resets = df[df['BitRotationCount'] < 1000].groupby('DeviceId').size()
print(f"Replacement cycles detected:\n{resets}")

# Expected: 3-5 cycles per device for 30-day dataset
assert resets.min() >= 3, "Not enough replacement cycles for ML training"

# Check date range
df['EventProcessedUtcTime'] = pd.to_datetime(df['EventProcessedUtcTime'])
print(f"Date range: {df['EventProcessedUtcTime'].min()} to {df['EventProcessedUtcTime'].max()}")
print(f"Days covered: {(df['EventProcessedUtcTime'].max() - df['EventProcessedUtcTime'].min()).days}")
```

---

## 📝 Usage in Labs

### Lab 3: ML Pipeline
```python
# Load data in Fabric notebook (Part 1)
csv_path = "Files/sample_quality_data.csv"
df_spark = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(csv_path)
```

### Power BI Dashboard
```
Data Source: Fabric Lakehouse
Table: MaintenanceML.replacement_predictions
Refresh: Daily (after ML scoring pipeline)
```

---

## ⚠️ Important Notes

1. **Privacy**: Sample data is synthetic - no real device data included
2. **Size Limits**: Files >50 MB are excluded from Git (see `.gitignore`)
3. **Generation Time**: ~5-10 minutes for 30-day dataset
4. **Storage**: Requires ~100 MB free disk space
5. **Randomness**: Each generation creates slightly different patterns (set seed for reproducibility)

---

## 🛠️ Troubleshooting

**Q: `generate_historical_data.py` not found**
```bash
# Ensure you're in the iot-simulator directory
cd iot-simulator
python generate_historical_data.py
```

**Q: Generated file is too small**
- Check `--days` parameter (default: 30)
- Verify `NUM_DEVICES` in script (default: 10)
- Check disk space

**Q: ML model performs poorly**
- Ensure at least 3 replacement cycles per machine
- Verify `BitRotationCount` resets are present
- Check for sufficient data variance (not all identical values)

**Q: Cannot load CSV in Fabric**
- Upload to Lakehouse **Files** section (not Tables)
- Verify file path: `Files/sample_quality_data.csv`
- Check file size limit (Fabric supports up to 100 MB per file)

---

**Need help?** See [main README](../README.md) or [create an issue](https://github.com/yourusername/iot-predictive-maintenance/issues).
