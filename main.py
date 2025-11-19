"""
Main entry point for IoT screw robot simulator.
Orchestrates multiple device simulators running concurrently.
"""

import asyncio
import logging
import signal
import sys
from typing import List

from config_loader import ConfigLoader
from telemetry_generator import TelemetryGenerator
from device_simulator import DeviceSimulator


# Global list to track running simulators for graceful shutdown
simulators: List[DeviceSimulator] = []


def setup_logging(log_level: str) -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Convert string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure logging format
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Reduce noise from Azure SDK
    logging.getLogger("azure.iot.device").setLevel(logging.WARNING)
    logging.getLogger("azure.core").setLevel(logging.WARNING)


def print_banner(config: dict) -> None:
    """
    Print startup banner with configuration information.

    Args:
        config: Configuration dictionary
    """
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║           IoT Screw Robot Simulator for Azure IoT Hub           ║
╚══════════════════════════════════════════════════════════════════╝

Configuration:
  • Number of devices: {num_devices}
  • Screwing interval: {interval}s (±{jitter}s jitter)
  • Constant speed: {speed} RPM
  • Anomaly rate: {anomaly_rate:.1%}
  • Degradation: {degradation}
  • Log level: {log_level}

Hot-Reload Enabled:
  ✓ You can modify .env while the simulator is running
  ✓ Changes will be applied before each screwing operation
  ✓ Try changing ANOMALY_RATE to test different scenarios

Press Ctrl+C to stop the simulation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".format(
        num_devices=config["num_devices"],
        interval=config["screwing_interval_seconds"],
        jitter=config["interval_jitter_seconds"],
        speed=config["constant_speed_rpm"],
        anomaly_rate=config["anomaly_rate"],
        degradation="Enabled" if config["enable_degradation"] else "Disabled",
        log_level=config["log_level"],
    )
    print(banner)


async def shutdown(signal_type=None) -> None:
    """
    Gracefully shutdown all device simulators.

    Args:
        signal_type: Signal that triggered shutdown (optional)
    """
    if signal_type:
        logging.info(f"Received signal {signal_type}, shutting down gracefully...")
    else:
        logging.info("Shutting down gracefully...")

    # Stop all simulators
    if simulators:
        logging.info(f"Stopping {len(simulators)} device simulators...")
        stop_tasks = [simulator.stop() for simulator in simulators]
        await asyncio.gather(*stop_tasks, return_exceptions=True)

    logging.info("Shutdown complete")


def setup_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    """
    Setup signal handlers for graceful shutdown on Windows.

    Args:
        loop: Event loop
    """
    # Windows doesn't support all POSIX signals
    # Use signal.signal for Windows compatibility
    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        loop.create_task(shutdown(signal.Signals(signum).name))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main() -> None:
    """
    Main async function to run the simulator.
    """
    try:
        # Load initial configuration
        config_loader = ConfigLoader(".env")
        config = config_loader.get_config()

        # Setup logging based on configuration
        setup_logging(config["log_level"])
        logger = logging.getLogger(__name__)

        # Print startup banner
        print_banner(config)

        # Get configuration values
        num_devices = config["num_devices"]
        iothub_hostname = config["iothub_hostname"]
        device_keys = config["device_keys"]
        device_id_prefix = config["device_id_prefix"]

        # Create device simulators
        logger.info(f"Initializing {num_devices} device simulators...")

        for i in range(num_devices):
            device_id = f"{device_id_prefix}-{i+1:03d}"
            device_key = device_keys[i]
            
            # Build connection string dynamically for this device
            connection_string = (
                f"HostName={iothub_hostname};"
                f"DeviceId={device_id};"
                f"SharedAccessKey={device_key}"
            )

            # Create telemetry generator for this device
            telemetry_gen = TelemetryGenerator(device_id)

            # Create device simulator
            simulator = DeviceSimulator(
                device_id=device_id,
                connection_string=connection_string,
                config_loader=config_loader,  # Shared config loader
                telemetry_generator=telemetry_gen,
            )

            simulators.append(simulator)

        # Start all simulators with staggered startup
        logger.info("Starting device simulators with staggered startup...")
        tasks = []

        for i, simulator in enumerate(simulators):
            # Stagger startup by 1.5 seconds per device
            if i > 0:
                await asyncio.sleep(1.5)

            # Create task for this simulator
            task = asyncio.create_task(simulator.run())
            tasks.append(task)

        logger.info(f"All {num_devices} devices started successfully")
        logger.info("Simulation running... (Press Ctrl+C to stop)")

        # Wait for all simulators to complete (or be cancelled)
        await asyncio.gather(*tasks, return_exceptions=True)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await shutdown()


if __name__ == "__main__":
    # Check if .env file exists
    import os
    from pathlib import Path

    env_file = Path(".env")
    if not env_file.exists():
        print("ERROR: .env file not found!")
        print()
        print("Please create a .env file based on .env.example:")
        print("  1. Copy .env.example to .env")
        print("  2. Update connection strings with your Azure IoT Hub device credentials")
        print()
        print("See README.md for detailed setup instructions")
        sys.exit(1)

    # Run the main async function
    try:
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(loop)

        # Run the main coroutine
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    finally:
        # Close the event loop
        loop.close()
