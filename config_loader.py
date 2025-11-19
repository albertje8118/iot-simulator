"""
Configuration loader with hot-reload capability.
Monitors .env file for changes and reloads configuration dynamically.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Manages application configuration with hot-reload support.
    Tracks .env file modification time and reloads only when changed.
    """

    def __init__(self, env_file: str = ".env"):
        """
        Initialize the configuration loader.

        Args:
            env_file: Path to the .env file (default: ".env")
        """
        self.env_file = Path(env_file)
        self.last_mtime: Optional[float] = None
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from .env file with type conversion and validation.

        Returns:
            Dictionary containing typed configuration values
        """
        try:
            # Load environment variables from .env file
            load_dotenv(self.env_file, override=True)

            # Update modification time
            if self.env_file.exists():
                self.last_mtime = self.env_file.stat().st_mtime

            # Parse and validate configuration
            new_config = {
                # IoT Hub configuration
                "iothub_hostname": os.getenv("IOTHUB_HOSTNAME", ""),
                "device_id_prefix": os.getenv("DEVICE_ID_PREFIX", "screw-robot"),
                "num_devices": int(os.getenv("NUM_DEVICES", "10")),
                # Device keys (individual keys per device)
                "device_keys": [
                    os.getenv(f"DEVICE_KEY_{i}", "")
                    for i in range(1, 11)
                ],
                # Simulation parameters
                "screwing_interval_seconds": int(
                    os.getenv("SCREWING_INTERVAL_SECONDS", "60")
                ),
                "interval_jitter_seconds": int(
                    os.getenv("INTERVAL_JITTER_SECONDS", "10")
                ),
                "constant_speed_rpm": int(os.getenv("CONSTANT_SPEED_RPM", "1800")),
                # Anomaly configuration
                "anomaly_rate": float(os.getenv("ANOMALY_RATE", "0.05")),
                "temp_anomaly_threshold": float(
                    os.getenv("TEMP_ANOMALY_THRESHOLD", "85")
                ),
                "vibration_spike_threshold": float(
                    os.getenv("VIBRATION_SPIKE_THRESHOLD", "2.0")
                ),
                "speed_variance_percent": float(
                    os.getenv("SPEED_VARIANCE_PERCENT", "15")
                ),
                # Degradation simulation
                "enable_degradation": os.getenv("ENABLE_DEGRADATION", "false").lower()
                == "true",
                # Logging
                "log_level": os.getenv("LOG_LEVEL", "INFO").upper(),
            }

            # Validate configuration
            self._validate_config(new_config)

            # Store new configuration
            old_config = self.config.copy()
            self.config = new_config

            # Log changes if config was previously loaded
            if old_config:
                self._log_config_changes(old_config, new_config)
            else:
                logger.info("Configuration loaded successfully")

            return self.config

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # If we have a previous good config, keep using it
            if self.config:
                logger.warning("Using last known good configuration")
                return self.config
            # Otherwise, re-raise the exception
            raise

    def reload_if_changed(self) -> bool:
        """
        Check if .env file has been modified and reload if necessary.
        Uses file modification time (mtime) for efficient change detection.

        Returns:
            True if configuration was reloaded, False otherwise
        """
        try:
            if not self.env_file.exists():
                logger.warning(f"Configuration file {self.env_file} not found")
                return False

            current_mtime = self.env_file.stat().st_mtime

            # Check if file has been modified
            if self.last_mtime is None or current_mtime > self.last_mtime:
                logger.debug(
                    f"Configuration file changed (mtime: {current_mtime}), reloading..."
                )
                self.load_config()
                return True

            logger.debug("Configuration file unchanged, using cached config")
            return False

        except Exception as e:
            logger.error(f"Error checking configuration file: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.

        Returns:
            Dictionary containing current configuration
        """
        return self.config

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration values.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate number of devices
        if not 1 <= config["num_devices"] <= 10:
            raise ValueError("NUM_DEVICES must be between 1 and 10")

        # Validate intervals
        if config["screwing_interval_seconds"] <= 0:
            raise ValueError("SCREWING_INTERVAL_SECONDS must be positive")

        if config["interval_jitter_seconds"] < 0:
            raise ValueError("INTERVAL_JITTER_SECONDS must be non-negative")

        # Validate anomaly rate
        if not 0.0 <= config["anomaly_rate"] <= 1.0:
            raise ValueError("ANOMALY_RATE must be between 0.0 and 1.0")

        # Validate speed
        if config["constant_speed_rpm"] <= 0:
            raise ValueError("CONSTANT_SPEED_RPM must be positive")

        # Validate IoT Hub configuration
        if not config["iothub_hostname"]:
            raise ValueError("IOTHUB_HOSTNAME is required")
        
        # Validate device keys for active devices
        for i in range(config["num_devices"]):
            if not config["device_keys"][i]:
                raise ValueError(
                    f"Missing device key for device {i + 1} (DEVICE_KEY_{i + 1})"
                )

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config["log_level"] not in valid_log_levels:
            raise ValueError(
                f"LOG_LEVEL must be one of {valid_log_levels}, got {config['log_level']}"
            )

    def _log_config_changes(
        self, old_config: Dict[str, Any], new_config: Dict[str, Any]
    ) -> None:
        """
        Log configuration changes between old and new config.

        Args:
            old_config: Previous configuration
            new_config: New configuration
        """
        changes = []

        # Check for changed values (excluding sensitive data for security)
        sensitive_keys = ["device_keys", "iothub_hostname"]
        for key in new_config:
            if key in sensitive_keys:
                continue  # Don't log sensitive data

            if old_config.get(key) != new_config[key]:
                changes.append(f"{key}: {old_config.get(key)} -> {new_config[key]}")

        if changes:
            logger.info(f"Configuration changed: {', '.join(changes)}")
