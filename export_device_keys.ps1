# PowerShell script to export all device keys to .env file
param(
    [string]$IoTHubName = "lab-iot01",
    [int]$NumDevices = 10,
    [string]$DevicePrefix = "screw-robot"
)

Write-Host "Fetching device keys from Azure IoT Hub..." -ForegroundColor Cyan

$envContent = @"
# ==============================================================================
# Azure IoT Hub Configuration - AUTO-GENERATED
# ==============================================================================
# Individual device connection strings

IOTHUB_HOSTNAME=$IoTHubName.azure-devices.net
DEVICE_ID_PREFIX=$DevicePrefix
NUM_DEVICES=$NumDevices

"@

for ($i = 1; $i -le $NumDevices; $i++) {
    $deviceId = "{0}-{1:D3}" -f $DevicePrefix, $i
    
    Write-Host "Fetching key for $deviceId..." -NoNewline
    
    $connStr = az iot hub device-identity connection-string show --hub-name $IoTHubName --device-id $deviceId --output json | ConvertFrom-Json
    
    if ($connStr) {
        $parts = $connStr.connectionString -split ';'
        $key = ($parts | Where-Object { $_ -like 'SharedAccessKey=*' }) -replace 'SharedAccessKey=', ''
        
        $envContent += "DEVICE_KEY_$i=$key`r`n"
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ✗ Failed" -ForegroundColor Red
    }
}

# Add remaining configuration
$envContent += @"

# ==============================================================================
# Simulation Parameters
# ==============================================================================

# Base interval between screwing operations (seconds)
SCREWING_INTERVAL_SECONDS=60

# Random jitter added to interval (±seconds) for realistic variance
INTERVAL_JITTER_SECONDS=10

# Constant screwing speed in rotations per minute (RPM)
CONSTANT_SPEED_RPM=1800

# ==============================================================================
# Anomaly Configuration
# ==============================================================================

# Probability of generating anomalies (0.0 to 1.0)
ANOMALY_RATE=0.05

# Temperature anomaly threshold (°C)
TEMP_ANOMALY_THRESHOLD=85

# Vibration spike threshold (g-force)
VIBRATION_SPIKE_THRESHOLD=2.0

# Speed variance percentage for speed anomalies (%)
SPEED_VARIANCE_PERCENT=15

# ==============================================================================
# Degradation Simulation
# ==============================================================================

ENABLE_DEGRADATION=false

# ==============================================================================
# Logging Configuration
# ==============================================================================

LOG_LEVEL=INFO
"@

# Save to .env
$envPath = Join-Path $PSScriptRoot ".env"
Set-Content -Path $envPath -Value $envContent -NoNewline

Write-Host "`n✓ .env file updated with all device keys!" -ForegroundColor Green
Write-Host "Run: python main.py" -ForegroundColor Cyan
