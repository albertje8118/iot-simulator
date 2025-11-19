# Microsoft Fabric ML Predictive Maintenance Lab
## 30-Minute Quick Start: Predict Component Replacement Using Machine Learning

---

## 🎯 Lab Objectives

In 30 minutes, you will:
1. Upload historical CSV data to Microsoft Fabric Lakehouse
2. Create features for machine learning in a Fabric Notebook
3. Train a predictive model using AutoML
4. Generate predictions and save to Lakehouse table
5. Visualize ML predictions in Power BI

**Duration:** 30 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** 
- Microsoft Fabric workspace access
- Power BI Desktop (latest version)
- CSV file: `quality_30days.csv` (generated from previous lab)

---

## 📋 What You'll Build

**ML Model Output:**
- Predict **days until component replacement** based on rotation patterns
- Identify **high-risk machines** needing immediate maintenance
- Generate **confidence scores** for each prediction

**Power BI Dashboard:**
- ML-predicted maintenance dates vs rule-based dates
- Risk heatmap by machine and component
- Feature importance visualization

---

## ⏱️ PART 1: Upload Data to Fabric Lakehouse (5 minutes)

### **Step 1.1: Create Lakehouse**

1. Go to **Microsoft Fabric** portal: https://app.fabric.microsoft.com
2. Navigate to your workspace (or create new: **Workspaces** → **+ New workspace**)
3. Click **+ New** → **Lakehouse**
4. Name: `MaintenanceML`
5. Click **Create**

### **Step 1.2: Upload CSV File**

1. In the Lakehouse, click **Get data** → **Upload files**
2. Select your `quality_30days.csv` file
3. Wait for upload to complete (progress bar in notification)
4. Click **Files** in left navigation to verify upload

### **Step 1.3: Load to Table**

1. Right-click on `quality_30days.csv` in Files section
2. Select **Load to Tables**
3. Table name: `machine_data_raw`
4. Click **Load**
5. Wait ~30 seconds for table creation
6. Verify: Click **Tables** → you should see `machine_data_raw`

---

## 🔧 PART 2: Feature Engineering Notebook (8 minutes)

### **Step 2.1: Create Notebook**

1. In Fabric workspace, click **+ New** → **Notebook**
2. Name: `ML_Feature_Engineering`
3. Attach to Lakehouse: Click **Add** → select `MaintenanceML`

### **Step 2.2: Load and Prepare Data**

**Cell 1: Load Data**
```python
# Load raw data from Lakehouse table
df = spark.read.table("MaintenanceML.machine_data_raw").toPandas()

# Convert timestamp to datetime
import pandas as pd
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values(['MachineID', 'Timestamp']).reset_index(drop=True)

print(f"Loaded {len(df):,} records")
print(f"Date range: {df['Timestamp'].min()} to {df['Timestamp'].max()}")
print(f"Machines: {df['MachineID'].nunique()}")
```

**Cell 2: Calculate Rotation Features**
```python
# Calculate rotation count per cycle
df['RotationCount'] = df['ActualAngle'] / 360.0

# Cumulative rotations per machine (key wear indicator)
df['CumulativeRotation'] = df.groupby('MachineID')['RotationCount'].cumsum()

# Cumulative bit rotations (use BitRotationCounter if available)
if 'BitRotationCounter' in df.columns:
    df['CumulativeBitRotation'] = df['BitRotationCounter']
else:
    df['CumulativeBitRotation'] = df['CumulativeRotation']

print("✅ Rotation features created")
df[['Timestamp', 'MachineID', 'RotationCount', 'CumulativeBitRotation']].head()
```

**Cell 3: Rolling Window Features**
```python
# Set timestamp as index for rolling calculations
df_indexed = df.set_index('Timestamp')

# Create rolling features (1 hour window)
rolling_features = df_indexed.groupby('MachineID').rolling('1H').agg({
    'RotationCount': ['sum', 'mean'],
    'ActualTorque': ['mean', 'std'],
    'CycleTime_ms': ['mean', 'max'],
    'CycleOK': 'mean'  # Pass rate in last hour
}).reset_index()

# Flatten column names
rolling_features.columns = ['MachineID', 'Timestamp', 
                             'Rot_LastHour_Sum', 'Rot_LastHour_Avg',
                             'Torque_LastHour_Avg', 'Torque_LastHour_Std',
                             'CycleTime_LastHour_Avg', 'CycleTime_LastHour_Max',
                             'PassRate_LastHour']

# Merge back to main dataframe
df = df.merge(rolling_features, on=['MachineID', 'Timestamp'], how='left')

# Fill NaN with 0 for first hour
df = df.fillna(0)

print("✅ Rolling window features created")
df[['MachineID', 'Rot_LastHour_Sum', 'Torque_LastHour_Avg', 'PassRate_LastHour']].head()
```

**Cell 4: Create Target Variable (Remaining Rotations)**
```python
# Define component lifetime (from reference data)
BIT_LIFETIME = 100000  # rotations

# Calculate remaining rotations until replacement
df['RemainingRotations'] = BIT_LIFETIME - df['CumulativeBitRotation']

# Calculate days until replacement (assuming current rotation rate)
df['RotationsPerHour'] = df['Rot_LastHour_Sum']
df['HoursUntilReplacement'] = df['RemainingRotations'] / (df['RotationsPerHour'] + 0.1)  # avoid divide by zero
df['DaysUntilReplacement'] = df['HoursUntilReplacement'] / 24

# Clip predictions to reasonable range (0-365 days)
df['DaysUntilReplacement'] = df['DaysUntilReplacement'].clip(0, 365)

print("✅ Target variable created")
print(f"Average days until replacement: {df['DaysUntilReplacement'].mean():.1f}")
df[['MachineID', 'CumulativeBitRotation', 'RemainingRotations', 'DaysUntilReplacement']].tail(10)
```

**Cell 5: Save Feature Table**
```python
# Select features for ML model
feature_columns = [
    'Timestamp', 'MachineID', 'ProductID', 'ScrewPosition',
    'CumulativeBitRotation', 'RotationCount',
    'Rot_LastHour_Sum', 'Rot_LastHour_Avg',
    'Torque_LastHour_Avg', 'Torque_LastHour_Std',
    'CycleTime_LastHour_Avg', 'CycleTime_LastHour_Max',
    'PassRate_LastHour',
    'ActualTorque', 'ActualAngle', 'CycleTime_ms',
    'DaysUntilReplacement'  # Target variable
]

df_features = df[feature_columns].copy()

# Convert back to Spark DataFrame and save to Lakehouse
spark_df = spark.createDataFrame(df_features)
spark_df.write.mode("overwrite").saveAsTable("MaintenanceML.ml_features")

print("✅ Feature table saved to Lakehouse: ml_features")
print(f"Total rows: {len(df_features):,}")
print(f"Feature columns: {len(feature_columns)}")
```

---

## 🤖 PART 3: Train ML Model with AutoML (7 minutes)

### **Step 3.1: Create ML Experiment**

1. In Fabric workspace, click **+ New** → **Experiment** (ML)
2. Name: `Predictive_Maintenance_Experiment`

### **Step 3.2: Configure AutoML**

1. Click **+ New AutoML run**
2. **Select data source:**
   - Type: **Lakehouse table**
   - Lakehouse: `MaintenanceML`
   - Table: `ml_features`
3. **Configure run:**
   - **Task type**: Regression
   - **Target column**: `DaysUntilReplacement`
   - **Primary metric**: R-squared (R²)
4. **Select features** (deselect non-predictive columns):
   - ✅ Keep: All numeric features (`CumulativeBitRotation`, `Rot_LastHour_*`, `Torque_*`, etc.)
   - ❌ Remove: `Timestamp`, `MachineID`, `ProductID` (identity columns)
5. **Training configuration:**
   - Training time: **5 minutes** (for speed)
   - Max iterations: **10**
   - Concurrency: **4**
6. Click **Start training**

### **Step 3.3: Monitor Training**

- Watch the **Leaderboard** panel update with model results
- Best models will show R² > 0.85 typically
- Wait ~5 minutes for completion

### **Step 3.4: Review Best Model**

1. Once complete, click on **Best model** (top of leaderboard)
2. Review:
   - **Metrics**: R², MAE (Mean Absolute Error), RMSE
   - **Feature importance**: Which features most influence predictions
3. Note the **Model name** for next step (e.g., `AutoML_Run1_Model3`)

---

## 📊 PART 4: Generate Predictions (5 minutes)

### **Step 4.1: Create Scoring Notebook**

1. In workspace, click **+ New** → **Notebook**
2. Name: `ML_Generate_Predictions`
3. Attach to Lakehouse: `MaintenanceML`

### **Step 4.2: Load Model and Score**

**Cell 1: Load Trained Model**
```python
import mlflow

# Load the best model from experiment
# Replace with your actual model URI from AutoML run
model_name = "AutoML_Run1_Model3"  # Update this!
model_uri = f"runs:/{model_name}/model"

# Alternative: Load from registered model
# model_uri = "models:/PredictiveMaintenance/1"

loaded_model = mlflow.sklearn.load_model(model_uri)
print(f"✅ Model loaded: {model_name}")
```

**Cell 2: Prepare Latest Data for Prediction**
```python
# Load feature table
df_features = spark.read.table("MaintenanceML.ml_features").toPandas()

# Get latest state per machine (most recent timestamp)
df_latest = df_features.sort_values('Timestamp').groupby('MachineID').tail(1).reset_index(drop=True)

# Select feature columns (exclude target and identifiers)
feature_cols = [
    'CumulativeBitRotation', 'RotationCount',
    'Rot_LastHour_Sum', 'Rot_LastHour_Avg',
    'Torque_LastHour_Avg', 'Torque_LastHour_Std',
    'CycleTime_LastHour_Avg', 'CycleTime_LastHour_Max',
    'PassRate_LastHour',
    'ActualTorque', 'ActualAngle', 'CycleTime_ms'
]

X_predict = df_latest[feature_cols]

print(f"Predicting for {len(df_latest)} machines")
df_latest[['MachineID', 'Timestamp', 'CumulativeBitRotation']].head()
```

**Cell 3: Generate Predictions**
```python
# Make predictions
predictions = loaded_model.predict(X_predict)

# Add predictions to dataframe
df_latest['ML_PredictedDays'] = predictions

# Calculate confidence/risk level
df_latest['RiskLevel'] = pd.cut(
    df_latest['ML_PredictedDays'],
    bins=[0, 2, 7, 14, 365],
    labels=['🔴 CRITICAL', '🟠 URGENT', '🟡 WARNING', '🟢 GOOD']
)

# Add prediction timestamp
from datetime import datetime
df_latest['PredictionTimestamp'] = datetime.utcnow()

print("✅ Predictions generated")
df_latest[['MachineID', 'ML_PredictedDays', 'RiskLevel', 'CumulativeBitRotation']].head(10)
```

**Cell 4: Save Predictions to Lakehouse**
```python
# Select columns for prediction table
prediction_cols = [
    'PredictionTimestamp', 'Timestamp', 'MachineID',
    'CumulativeBitRotation', 'RotationCount',
    'Rot_LastHour_Sum', 'PassRate_LastHour',
    'DaysUntilReplacement',  # Rule-based prediction
    'ML_PredictedDays',       # ML prediction
    'RiskLevel'
]

df_predictions = df_latest[prediction_cols].copy()

# Convert to Spark and save
spark_predictions = spark.createDataFrame(df_predictions)
spark_predictions.write.mode("overwrite").saveAsTable("MaintenanceML.ml_predictions")

print("✅ Predictions saved to: MaintenanceML.ml_predictions")
print(f"Total predictions: {len(df_predictions)}")
print("\n📊 Risk Distribution:")
print(df_predictions['RiskLevel'].value_counts())
```

---

## 📈 PART 5: Visualize in Power BI (5 minutes)

### **Step 5.1: Connect Power BI to Lakehouse**

1. Open **Power BI Desktop**
2. Click **Home** → **Get Data** → **More**
3. Search for: **Microsoft Fabric**
4. Select **Lakehouse** → **Connect**
5. Sign in with your Fabric credentials
6. Navigate to workspace → Select `MaintenanceML` lakehouse
7. Select tables:
   - ✅ `ml_predictions`
   - ✅ `machine_data_raw` (optional, for drill-down)
8. Click **Load**

### **Step 5.2: Create DAX Measures**

**Measure 1: Average ML Prediction**
```dax
AvgML_PredictedDays = AVERAGE(ml_predictions[ML_PredictedDays])
```

**Measure 2: Average Rule-Based Prediction**
```dax
AvgRule_PredictedDays = AVERAGE(ml_predictions[DaysUntilReplacement])
```

**Measure 3: Prediction Difference**
```dax
PredictionDifference = [AvgML_PredictedDays] - [AvgRule_PredictedDays]
```

**Measure 4: Critical Machines Count**
```dax
CriticalMachines = 
CALCULATE(
    DISTINCTCOUNT(ml_predictions[MachineID]),
    ml_predictions[RiskLevel] = "🔴 CRITICAL"
)
```

### **Step 5.3: Build Dashboard**

#### **Visual 1: KPI Cards (Top Row)**

1. **Card: ML Predicted Days (Avg)**
   - Field: `[AvgML_PredictedDays]`
   - Format: 0 "days"

2. **Card: Rule-Based Days (Avg)**
   - Field: `[AvgRule_PredictedDays]`
   - Format: 0 "days"

3. **Card: Prediction Improvement**
   - Field: `[PredictionDifference]`
   - Conditional formatting: Green if negative (ML predicts sooner)

4. **Card: Critical Machines**
   - Field: `[CriticalMachines]`
   - Background: Red

#### **Visual 2: Risk Heatmap Matrix**

5. **Matrix: Machine Risk Status**
   - Rows: `MachineID`
   - Columns: `RiskLevel`
   - Values: `ML_PredictedDays` (average)
   - Conditional formatting on values:
     - Red: 0-7 days
     - Orange: 7-14 days
     - Yellow: 14-30 days
     - Green: 30+ days

#### **Visual 3: Comparison Charts**

6. **Clustered Bar Chart: ML vs Rule-Based**
   - Y-axis: `MachineID`
   - X-axis: 
     - `ML_PredictedDays`
     - `DaysUntilReplacement`
   - Legend: Measure names
   - Title: "ML Predictions vs Rule-Based by Machine"

7. **Scatter Plot: Rotation vs Predicted Days**
   - X-axis: `CumulativeBitRotation`
   - Y-axis: `ML_PredictedDays`
   - Legend: `RiskLevel`
   - Size: `Rot_LastHour_Sum`
   - Title: "Rotation Pattern vs ML Prediction"

#### **Visual 4: Feature Importance (Manual)**

8. **Table: Top Predictive Features**

Create a manual table in Power BI:
- **Home** → **Enter Data**
- Table name: `FeatureImportance`

| Feature | Importance | Impact |
|---------|------------|--------|
| CumulativeBitRotation | 0.42 | Very High |
| Rot_LastHour_Sum | 0.28 | High |
| Torque_LastHour_Std | 0.15 | Medium |
| CycleTime_LastHour_Max | 0.08 | Medium |
| PassRate_LastHour | 0.07 | Low |

9. **Bar Chart: Feature Importance**
   - Y-axis: `Feature`
   - X-axis: `Importance`
   - Data labels: On
   - Sort by: Importance (descending)

---

## 🎓 Key Insights & Interpretation

### **What the ML Model Learns**

1. **Rotation Patterns**: Machines with sudden increases in rotation rate may fail sooner
2. **Torque Variability**: High standard deviation indicates wear/instability
3. **Cycle Time**: Consistently slow cycles suggest mechanical degradation
4. **Pass Rate**: Declining quality correlates with approaching failure

### **ML vs Rule-Based Predictions**

| Aspect | Rule-Based | ML-Based |
|--------|------------|----------|
| Method | Linear extrapolation | Pattern recognition |
| Accuracy | Good for steady-state | Better for variable patterns |
| Considers | Rotation count only | Multiple features + trends |
| Adapts | No | Yes (with retraining) |

### **When ML Provides Better Predictions**

✅ **ML predicts sooner** when:
- Torque variance increases suddenly
- Cycle times become inconsistent
- Pass rate starts declining
- Multiple warning signs appear together

❌ **Rule-based is sufficient** when:
- Machine operates steadily
- No quality issues
- Linear wear pattern

---

## 🔄 Optional: Schedule Automated Predictions

### **Create Pipeline for Daily Predictions**

1. In Fabric workspace, click **+ New** → **Data pipeline**
2. Name: `Daily_ML_Predictions`
3. Add activities:
   - **Activity 1**: Run Notebook → `ML_Feature_Engineering`
   - **Activity 2**: Run Notebook → `ML_Generate_Predictions`
4. Set schedule:
   - Frequency: Daily
   - Time: 1:00 AM UTC
5. Click **Publish**

---

## 📚 Next Steps: Production Deployment

### **Week 2-4: Connect to Real-Time Data**

1. **Azure Data Factory + Self-Hosted IR**:
   - Install SHIR on industrial PC
   - Create pipeline: On-prem folder → Azure Blob → Fabric Lakehouse
   - Schedule: Every 15 minutes

2. **Update pipeline**:
   - Incremental load (only new files)
   - Append to `machine_data_raw` table

### **Month 2: Model Monitoring & Retraining**

1. **Track prediction accuracy**:
   - Log actual replacement dates when they occur
   - Compare with predicted dates
   - Calculate MAE and RMSE monthly

2. **Automated retraining**:
   - Trigger when error exceeds threshold (e.g., MAE > 3 days)
   - Use new data (last 90 days)
   - A/B test new model vs current

3. **Alerting**:
   - Power Automate flow when `CriticalMachines > 2`
   - Send email/Teams notification with machine list

---

## ✅ Lab Completion Checklist

- [ ] CSV uploaded to Fabric Lakehouse
- [ ] Feature engineering notebook created and run
- [ ] AutoML experiment completed (R² > 0.80)
- [ ] Predictions generated and saved to table
- [ ] Power BI connected to `ml_predictions` table
- [ ] Dashboard created with 9 visuals
- [ ] ML vs Rule-based comparison visible

---

## 🎯 Expected Outcomes

**Model Performance:**
- R² (R-squared): 0.85-0.95 (excellent predictive power)
- MAE (Mean Absolute Error): 1-3 days
- RMSE (Root Mean Squared Error): 2-5 days

**Business Impact:**
- ✅ **Reduce unplanned downtime** by 30-50%
- ✅ **Optimize maintenance scheduling** with 2-3 day accuracy
- ✅ **Lower maintenance costs** by avoiding premature replacements
- ✅ **Improve production efficiency** through predictive planning

---

## 🚀 Advanced Enhancements

### **1. Multi-Component Prediction**
Extend to predict Spindle, Gearbox, Bearing separately:
```python
# Train separate models for each component
components = ['Bit', 'Spindle', 'Gearbox', 'Bearing']
for component in components:
    # Adjust target variable
    df[f'{component}_RemainingDays'] = calculate_remaining(component)
    # Train component-specific model
```

### **2. Survival Analysis**
Use survival models (Cox Proportional Hazards) for probability distributions:
```python
from lifelines import CoxPHFitter
cph = CoxPHFitter()
cph.fit(df, duration_col='DaysUntilReplacement', event_col='FailureOccurred')
```

### **3. Real-Time Scoring API**
Deploy model as REST endpoint:
```python
# Azure ML deployment
from azureml.core import Workspace, Model
model = Model.register(workspace, model_path, model_name)
service = Model.deploy(workspace, service_name, [model], inference_config, deployment_config)
```

---

**Congratulations! You've built a production-ready ML predictive maintenance system in 30 minutes! 🤖🏭**

---

## 📖 Appendix: Troubleshooting

### **Issue: AutoML training fails**
**Solution:** Reduce data size - use last 7 days only:
```python
df_features_subset = df_features[df_features['Timestamp'] > df_features['Timestamp'].max() - pd.Timedelta(days=7)]
```

### **Issue: Power BI can't connect to Lakehouse**
**Solution:** 
1. Verify Fabric workspace permissions (Contributor or Admin)
2. Ensure Lakehouse has at least one table
3. Try refreshing connection in Power BI: Data source settings → Refresh

### **Issue: Predictions are unrealistic (negative or >1000 days)**
**Solution:** Add validation in scoring notebook:
```python
# Clip predictions to realistic range
df_latest['ML_PredictedDays'] = df_latest['ML_PredictedDays'].clip(0, 365)
```

### **Issue: Model R² is low (<0.60)**
**Causes:**
- Insufficient data (need 10k+ records)
- High noise in data
- Missing important features

**Solutions:**
- Collect more historical data
- Add more rolling window features (3H, 6H, 24H)
- Consider filtering out anomalous cycles before training
