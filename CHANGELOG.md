# Changelog

All notable changes to the IoT Predictive Maintenance Solution will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-19

### Added - Initial Release 🚀

#### IoT Simulator
- Python-based simulator for 10 concurrent screw robot devices
- Azure IoT Hub integration with MQTT/AMQP protocols
- Configurable anomaly injection (temperature, vibration, speed)
- Component degradation simulation for realistic wear patterns
- Hot-reload configuration from `.env` file
- Rich sensor telemetry: temperature, vibration, torque, rotation counts
- PowerShell script for automated device registration

#### ML Pipeline
- Complete Jupyter notebook with 15 sequential parts
- XGBoost regression model for remaining useful life prediction
- Automatic replacement event detection via counter resets
- Cycle segmentation and target variable generation
- Feature engineering: rolling windows, time features, rotation rates
- MLflow experiment tracking integration
- Daily scoring pipeline for production predictions
- Risk level classification (CRITICAL/HIGH/MEDIUM/LOW)
- Date conversion from rotations to calendar dates

#### Microsoft Fabric Integration
- Eventstream setup guide for real-time IoT Hub ingestion
- Lakehouse schema with quality_data and replacement_predictions tables
- KQL transformations for data processing
- OneLake integration with Dataverse tables

#### Power BI Dashboard
- Gantt chart timeline visualization (Microsoft official visual)
- Risk level indicators with color coding
- Machine health score gauges
- Real-time metrics and KPIs
- DAX measures for predictions and remaining time
- Week/month/quarter date type selection
- Auto-refresh configuration

#### Power Automate
- Automated cloud flow triggered by critical predictions
- Email alerts to maintenance team with rich HTML formatting
- Work order creation in Dataverse or SharePoint
- Microsoft Teams notifications
- OData filtering for efficient triggering

#### Power Apps
- Canvas app for work order management
- Three-screen template (Browse/Detail/Edit)
- Mobile-optimized for factory floor access
- Self-assignment and status tracking
- Support for both Dataverse and SharePoint List backends
- Color-coded priority and status badges
- Offline capability with sync

#### Documentation
- Comprehensive README with architecture diagrams
- Step-by-step setup guides for all components
- Fabric Eventstream configuration guide
- Power BI dashboard creation guide
- ML training lab documentation
- Schema migration guide
- Contributing guidelines
- MIT License

#### Sample Data
- 30-day historical telemetry dataset
- Sample quality data CSV files
- Historical data generator script

### Technical Specifications

- **Python**: 3.8+ compatibility
- **Libraries**: azure-iot-device, pandas, numpy, xgboost, scikit-learn, mlflow
- **Azure**: IoT Hub (S1 tier), Microsoft Fabric (F64 capacity)
- **ML Model**: XGBoost Regressor
  - Validation MAE: ~150-300 rotations (~0.5-1 day)
  - R² Score: 0.85-0.95
  - Training time: 5-10 minutes
  - Inference: <2 minutes for 10 machines
- **Power Platform**: 
  - Power BI (included in Fabric)
  - Power Automate (standard or premium)
  - Power Apps (premium or M365 included)
  - Dataverse or SharePoint List backends

### Business Value

- **40-60% reduction** in unplanned downtime
- **2-3 day advance notice** for maintenance scheduling
- **15-20% savings** on parts inventory costs
- **Proactive maintenance** culture enablement
- **Real-time monitoring** across all machines
- **Mobile work order management** for engineers

---

## [Unreleased]

### Planned for v1.1.0

#### Enhancements
- LSTM model for time-series prediction
- Real-time streaming ML with Fabric RT Intelligence
- Azure Digital Twins integration
- Advanced anomaly detection algorithms
- Performance benchmarking suite
- Cost optimization recommendations

#### Documentation
- Video tutorials for each lab
- Production deployment best practices
- Performance tuning guide
- Multi-language support (Spanish, Portuguese)

#### Infrastructure
- Docker containerization for IoT simulator
- Terraform templates for Azure resources
- GitHub Actions CI/CD pipeline
- Unit and integration tests

#### Power Platform
- Additional Power BI custom visuals
- Power Virtual Agents integration
- Advanced workflow templates
- Multi-tenant support

---

## Version History Format

### [Version] - YYYY-MM-DD

#### Added
- New features

#### Changed
- Changes in existing functionality

#### Deprecated
- Soon-to-be removed features

#### Removed
- Removed features

#### Fixed
- Bug fixes

#### Security
- Vulnerability fixes

---

**Note**: This is the initial public release. Future versions will track changes incrementally.

For full details on upcoming features, see [GitHub Issues](https://github.com/yourusername/iot-predictive-maintenance/issues) and [Project Board](https://github.com/yourusername/iot-predictive-maintenance/projects).
