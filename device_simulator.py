"""
IoT device simulator for screw robot.
Manages connection to Azure IoT Hub and sends telemetry data.
"""

import asyncio
import json
import random
import logging
from typing import Optional
from datetime import datetime, timezone

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from azure.iot.device.exceptions import (
    ConnectionFailedError,
    ConnectionDroppedError,
    CredentialError,
    OperationTimeout,
)

from config_loader import ConfigLoader
from telemetry_generator import TelemetryGenerator

logger = logging.getLogger(__name__)


class DeviceSimulator:
    """
    Simulates a screw robot IoT device sending telemetry to Azure IoT Hub.
    Supports hot-reload of configuration and graceful shutdown.
    """

    def __init__(
        self,
        device_id: str,
        connection_string: str,
        config_loader: ConfigLoader,
        telemetry_generator: TelemetryGenerator,
    ):
        """
        Initialize the device simulator.

        Args:
            device_id: Unique identifier for the device
            connection_string: Azure IoT Hub device connection string
            config_loader: Shared configuration loader instance
            telemetry_generator: Telemetry generator for this device
        """
        self.device_id = device_id
        self.connection_string = connection_string
        self.config_loader = config_loader
        self.telemetry_generator = telemetry_generator
        self.client: Optional[IoTHubDeviceClient] = None
        self.running = False
        self.messages_sent = 0

    async def connect(self) -> None:
        """
        Establish connection to Azure IoT Hub.
        """
        try:
            self.client = IoTHubDeviceClient.create_from_connection_string(
                self.connection_string,
                keep_alive=60,
                connection_retry=True,
                connection_retry_interval=10,
            )

            await self.client.connect()
            self.running = True
            logger.info(f"{self.device_id}: Connected to IoT Hub")

        except CredentialError as e:
            logger.error(f"{self.device_id}: Authentication failed: {e}")
            raise
        except ConnectionFailedError as e:
            logger.error(f"{self.device_id}: Connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"{self.device_id}: Unexpected error during connection: {e}")
            raise

    async def disconnect(self) -> None:
        """
        Disconnect from Azure IoT Hub.
        """
        self.running = False
        if self.client:
            try:
                await self.client.disconnect()
                logger.info(
                    f"{self.device_id}: Disconnected from IoT Hub "
                    f"(sent {self.messages_sent} messages)"
                )
            except Exception as e:
                logger.error(f"{self.device_id}: Error during disconnect: {e}")

    async def send_telemetry(self, telemetry_data: dict) -> bool:
        """
        Send telemetry message to Azure IoT Hub with retry logic.

        Args:
            telemetry_data: Dictionary containing telemetry data

        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self.client:
            logger.error(f"{self.device_id}: Client not connected")
            return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Create message with JSON payload
                message_json = json.dumps(telemetry_data)
                message = Message(message_json)

                # Set message properties
                message.content_type = "application/json"
                message.content_encoding = "utf-8"

                # Add custom properties for routing and filtering
                message.custom_properties["iothub-creation-time-utc"] = datetime.now(
                    timezone.utc
                ).isoformat()
                message.custom_properties["deviceType"] = "screw-robot"
                
                # Quality control routing
                cycle_ok = telemetry_data.get("CycleOK", True)
                error_code = telemetry_data.get("ErrorCode", 0)
                
                # Set alert level based on cycle status
                if not cycle_ok:
                    message.custom_properties["alertLevel"] = "warning"
                    message.custom_properties["qualityStatus"] = "NOK"
                else:
                    message.custom_properties["alertLevel"] = "normal"
                    message.custom_properties["qualityStatus"] = "OK"
                
                # Add error code for routing
                message.custom_properties["errorCode"] = str(error_code)

                # Send message to IoT Hub
                await self.client.send_message(message)

                self.messages_sent += 1
                logger.info(
                    f"{self.device_id}: Sent message #{self.messages_sent} "
                    f"(CycleOK: {cycle_ok}, Error: {error_code})"
                )

                return True

            except (ConnectionDroppedError, OperationTimeout) as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(
                        f"{self.device_id}: Message send failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {wait_time}s... Error: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"{self.device_id}: Failed to send message after {max_retries} attempts: {e}"
                    )
                    return False

            except Exception as e:
                logger.error(f"{self.device_id}: Unexpected error sending message: {e}")
                return False

        return False

    async def run(self) -> None:
        """
        Main simulation loop. Connects to IoT Hub and sends telemetry events.
        Reloads configuration before each screwing operation.
        """
        try:
            # Connect to IoT Hub
            await self.connect()

            logger.info(f"{self.device_id}: Starting simulation loop")

            while self.running:
                try:
                    # Reload configuration if it has changed
                    config_changed = self.config_loader.reload_if_changed()
                    if config_changed:
                        logger.info(
                            f"{self.device_id}: Configuration reloaded, "
                            "applying new settings"
                        )

                    # Get current configuration
                    config = self.config_loader.get_config()

                    # Generate screwing event telemetry
                    telemetry = self.telemetry_generator.generate_screwing_event(
                        config
                    )

                    # Send telemetry to IoT Hub
                    await self.send_telemetry(telemetry)

                    # Calculate sleep interval with jitter
                    base_interval = config["screwing_interval_seconds"]
                    jitter = config["interval_jitter_seconds"]
                    sleep_time = base_interval + random.uniform(-jitter, jitter)
                    sleep_time = max(1, sleep_time)  # Minimum 1 second

                    logger.debug(
                        f"{self.device_id}: Waiting {sleep_time:.1f}s until next operation"
                    )
                    await asyncio.sleep(sleep_time)

                except asyncio.CancelledError:
                    logger.info(f"{self.device_id}: Simulation cancelled")
                    break
                except Exception as e:
                    logger.error(
                        f"{self.device_id}: Error in simulation loop: {e}", exc_info=True
                    )
                    # Continue running despite errors
                    await asyncio.sleep(5)

        finally:
            # Ensure disconnect is called
            await self.disconnect()

            # Log final statistics
            stats = self.telemetry_generator.get_statistics()
            logger.info(f"{self.device_id}: Final statistics: {stats}")

    async def stop(self) -> None:
        """
        Stop the simulation gracefully.
        """
        logger.info(f"{self.device_id}: Stopping simulation...")
        self.running = False
