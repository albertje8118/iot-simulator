# PowerShell script to register 10 IoT devices in Azure IoT Hub
# This script registers screw-robot-001 through screw-robot-010

param(
    [string]$IoTHubName = "lab-iot01",
    [int]$NumDevices = 10,
    [string]$DevicePrefix = "screw-robot"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IoT Device Registration Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IoT Hub: $IoTHubName" -ForegroundColor Yellow
Write-Host "Number of Devices: $NumDevices" -ForegroundColor Yellow
Write-Host "Device Prefix: $DevicePrefix" -ForegroundColor Yellow
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "✓ Azure CLI detected: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "✗ Azure CLI not found. Please install from: https://aka.ms/InstallAzureCLIDirect" -ForegroundColor Red
    exit 1
}

# Check if logged in
Write-Host "Checking Azure login status..." -ForegroundColor Cyan
$account = az account show 2>$null
if (-not $account) {
    Write-Host "✗ Not logged in to Azure. Running 'az login'..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Login failed" -ForegroundColor Red
        exit 1
    }
}

$accountInfo = az account show | ConvertFrom-Json
Write-Host "✓ Logged in as: $($accountInfo.user.name)" -ForegroundColor Green
Write-Host "✓ Subscription: $($accountInfo.name)" -ForegroundColor Green
Write-Host ""

# Register devices
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Registering Devices..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0
$deviceKeys = @()

for ($i = 1; $i -le $NumDevices; $i++) {
    $deviceId = "{0}-{1:D3}" -f $DevicePrefix, $i
    
    Write-Host "[$i/$NumDevices] Registering device: $deviceId" -ForegroundColor Cyan
    
    # Check if device already exists
    $existingDevice = az iot hub device-identity show --hub-name $IoTHubName --device-id $deviceId 2>$null
    
    if ($existingDevice) {
        Write-Host "  ℹ Device already exists, skipping..." -ForegroundColor Yellow
        $successCount++
        
        # Get the existing key
        $connectionString = az iot hub device-identity connection-string show --hub-name $IoTHubName --device-id $deviceId --output json | ConvertFrom-Json
        $deviceKeys += $connectionString.connectionString
    } else {
        # Create the device
        $result = az iot hub device-identity create --hub-name $IoTHubName --device-id $deviceId 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Device created successfully" -ForegroundColor Green
            $successCount++
            
            # Get connection string
            $connectionString = az iot hub device-identity connection-string show --hub-name $IoTHubName --device-id $deviceId --output json | ConvertFrom-Json
            $deviceKeys += $connectionString.connectionString
        } else {
            Write-Host "  ✗ Failed to create device: $result" -ForegroundColor Red
            $failCount++
        }
    }
    
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Registration Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Successful: $successCount" -ForegroundColor Green
Write-Host "✗ Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($successCount -gt 0) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Extracting Shared Access Key" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Get the shared access key from first device
    if ($deviceKeys.Count -gt 0) {
        $firstConnectionString = $deviceKeys[0]
        
        # Parse connection string to extract SharedAccessKey
        $parts = $firstConnectionString -split ';'
        $hostname = ($parts | Where-Object { $_ -like 'HostName=*' }) -replace 'HostName=', ''
        $sharedAccessKey = ($parts | Where-Object { $_ -like 'SharedAccessKey=*' }) -replace 'SharedAccessKey=', ''
        
        Write-Host "✓ IoT Hub Hostname: $hostname" -ForegroundColor Green
        Write-Host "✓ Shared Access Key: $sharedAccessKey" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Update Your .env File" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Copy these values to your .env file:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "IOTHUB_HOSTNAME=$hostname" -ForegroundColor White
        Write-Host "IOTHUB_SHARED_ACCESS_KEY_NAME=" -ForegroundColor White
        Write-Host "IOTHUB_SHARED_ACCESS_KEY=$sharedAccessKey" -ForegroundColor White
        Write-Host "DEVICE_ID_PREFIX=$DevicePrefix" -ForegroundColor White
        Write-Host "NUM_DEVICES=$NumDevices" -ForegroundColor White
        Write-Host ""
        
        # Offer to update .env automatically
        Write-Host "Would you like to automatically update .env? (y/n): " -ForegroundColor Yellow -NoNewline
        $response = Read-Host
        
        if ($response -eq 'y' -or $response -eq 'Y') {
            $envPath = Join-Path $PSScriptRoot ".env"
            
            if (Test-Path $envPath) {
                Write-Host "Updating .env file..." -ForegroundColor Cyan
                
                $envContent = Get-Content $envPath -Raw
                
                # Update the values
                $envContent = $envContent -replace 'IOTHUB_HOSTNAME=.*', "IOTHUB_HOSTNAME=$hostname"
                $envContent = $envContent -replace 'IOTHUB_SHARED_ACCESS_KEY_NAME=.*', "IOTHUB_SHARED_ACCESS_KEY_NAME="
                $envContent = $envContent -replace 'IOTHUB_SHARED_ACCESS_KEY=.*', "IOTHUB_SHARED_ACCESS_KEY=$sharedAccessKey"
                $envContent = $envContent -replace 'DEVICE_ID_PREFIX=.*', "DEVICE_ID_PREFIX=$DevicePrefix"
                $envContent = $envContent -replace 'NUM_DEVICES=.*', "NUM_DEVICES=$NumDevices"
                
                Set-Content -Path $envPath -Value $envContent -NoNewline
                
                Write-Host "✓ .env file updated successfully!" -ForegroundColor Green
                Write-Host ""
                Write-Host "You can now run: python main.py" -ForegroundColor Cyan
            } else {
                Write-Host "✗ .env file not found at: $envPath" -ForegroundColor Red
                Write-Host "Please create it from .env.example first" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Registration Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update your .env file with the values above (if not done automatically)" -ForegroundColor White
Write-Host "2. Run the simulator: python main.py" -ForegroundColor White
Write-Host "3. Monitor IoT Hub in Azure Portal for incoming messages" -ForegroundColor White
Write-Host ""
