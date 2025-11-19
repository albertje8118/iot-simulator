"""
Generate historical IoT telemetry data for the past 1 month.
Creates CSV file with 1-minute resolution data for all 10 devices.
"""

import csv
import random
import uuid
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any

from config_loader import ConfigLoader
from telemetry_generator import TelemetryGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_historical_data(
    num_devices: int = 10,
    days_back: int = 30,
    interval_minutes: int = 1,
    output_file: str = "historical_telemetry.csv"
) -> None:
    """
    Generate historical telemetry data and save to CSV.
    
    Args:
        num_devices: Number of devices to simulate
        days_back: Number of days in the past to generate data for
        interval_minutes: Interval between events in minutes
        output_file: Output CSV filename
    """
    logger.info(f"Starting historical data generation:")
    logger.info(f"  - Devices: {num_devices}")
    logger.info(f"  - Period: {days_back} days")
    logger.info(f"  - Resolution: {interval_minutes} minute(s)")
    
    # Calculate time range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days_back)
    total_records = num_devices * days_back * 24 * (60 // interval_minutes)
    
    logger.info(f"  - Start: {start_time.isoformat()}")
    logger.info(f"  - End: {end_time.isoformat()}")
    logger.info(f"  - Expected records: {total_records:,}")
    
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.get_config()
    
    # Create telemetry generators for each device
    device_id_prefix = config["device_id_prefix"]
    generators = {}
    for i in range(1, num_devices + 1):
        device_id = f"{device_id_prefix}-{i:03d}"
        generators[device_id] = TelemetryGenerator(device_id)
    
    logger.info(f"Initialized {len(generators)} telemetry generators")
    
    # Prepare CSV file
    output_path = Path(output_file)
    fieldnames = [
        "Timestamp",
        "MachineID",
        "ProductID",
        "ScrewPosition",
        "TargetTorque",
        "ActualTorque",
        "TargetAngle",
        "ActualAngle",
        "PulseCount",
        "CycleOK",
        "CycleTime_ms",
        "SpindleRotationCounter",
        "BitRotationCounter",
        "ErrorCode"
    ]
    
    records_written = 0
    progress_interval = total_records // 20  # Report progress every 5%
    
    logger.info(f"Writing data to: {output_path.absolute()}")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Generate data for each timestamp
        current_time = start_time
        
        while current_time <= end_time:
            # Generate event for each device at this timestamp
            for device_id, generator in generators.items():
                # Generate telemetry event
                telemetry = generator.generate_screwing_event(config)
                
                # Override timestamp with historical time
                telemetry["Timestamp"] = current_time.isoformat()
                
                # CSV row with new schema (no flattening needed)
                row = {
                    "Timestamp": telemetry["Timestamp"],
                    "MachineID": telemetry["MachineID"],
                    "ProductID": telemetry["ProductID"],
                    "ScrewPosition": telemetry["ScrewPosition"],
                    "TargetTorque": telemetry["TargetTorque"],
                    "ActualTorque": telemetry["ActualTorque"],
                    "TargetAngle": telemetry["TargetAngle"],
                    "ActualAngle": telemetry["ActualAngle"],
                    "PulseCount": telemetry["PulseCount"],
                    "CycleOK": telemetry["CycleOK"],
                    "CycleTime_ms": telemetry["CycleTime_ms"],
                    "SpindleRotationCounter": telemetry["SpindleRotationCounter"],
                    "BitRotationCounter": telemetry["BitRotationCounter"],
                    "ErrorCode": telemetry["ErrorCode"]
                }
                
                writer.writerow(row)
                records_written += 1
                
                # Progress reporting
                if records_written % progress_interval == 0:
                    progress = (records_written / total_records) * 100
                    logger.info(f"Progress: {progress:.1f}% ({records_written:,} / {total_records:,} records)")
            
            # Move to next timestamp
            current_time += timedelta(minutes=interval_minutes)
    
    logger.info(f"✓ Data generation complete!")
    logger.info(f"  - Total records: {records_written:,}")
    logger.info(f"  - File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    logger.info(f"  - Output: {output_path.absolute()}")
    
    # Print summary statistics
    print_summary_statistics(generators)


def print_summary_statistics(generators: Dict[str, TelemetryGenerator]) -> None:
    """
    Print summary statistics for all devices.
    
    Args:
        generators: Dictionary of device_id to TelemetryGenerator
    """
    logger.info("\n" + "="*60)
    logger.info("SUMMARY STATISTICS")
    logger.info("="*60)
    
    for device_id, generator in generators.items():
        stats = generator.get_statistics()
        logger.info(f"\n{device_id}:")
        logger.info(f"  - Total operations: {stats['totalOperations']:,}")
        logger.info(f"  - Operational hours: {stats['operationalHours']:.2f} hrs")
        logger.info(f"  - Bit rotation counter: {stats['bitRotationCounter']:,}")
        logger.info(f"  - Component health:")
        logger.info(f"      Motor: {stats['componentHealth']['motor']:.3f}")
        logger.info(f"      Bearing: {stats['componentHealth']['bearing']:.3f}")
        logger.info(f"      Sensor: {stats['componentHealth']['sensor']:.3f}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate historical IoT telemetry data for screw robots"
    )
    parser.add_argument(
        "--devices",
        type=int,
        default=10,
        help="Number of devices (default: 10)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to generate data for (default: 30)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="Interval between events in minutes (default: 1)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="historical_telemetry.csv",
        help="Output CSV filename (default: historical_telemetry.csv)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.devices < 1 or args.devices > 100:
        logger.error("Number of devices must be between 1 and 100")
        return
    
    if args.days < 1 or args.days > 365:
        logger.error("Number of days must be between 1 and 365")
        return
    
    if args.interval < 1 or args.interval > 1440:
        logger.error("Interval must be between 1 and 1440 minutes")
        return
    
    # Estimate output size
    estimated_records = args.devices * args.days * 24 * (60 // args.interval)
    estimated_size_mb = (estimated_records * 200) / 1024 / 1024  # ~200 bytes per row
    
    logger.info(f"\nEstimated output size: ~{estimated_size_mb:.1f} MB")
    
    # Confirmation for large datasets
    if estimated_records > 1_000_000:
        logger.warning(f"⚠️  Large dataset: {estimated_records:,} records")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            logger.info("Cancelled by user")
            return
    
    try:
        generate_historical_data(
            num_devices=args.devices,
            days_back=args.days,
            interval_minutes=args.interval,
            output_file=args.output
        )
    except KeyboardInterrupt:
        logger.info("\n⚠️  Generation interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error during generation: {e}", exc_info=True)


if __name__ == "__main__":
    main()
