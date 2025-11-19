"""
Telemetry generator for screw robot IoT devices.
Generates realistic sensor data with configurable anomalies and degradation.
"""

import random
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TelemetryGenerator:
    """
    Generates telemetry data for a screw robot device.
    Maintains operational state and simulates sensor readings.
    """

    def __init__(self, device_id: str):
        """
        Initialize the telemetry generator for a specific device.

        Args:
            device_id: Unique identifier for the device
        """
        self.device_id = device_id
        self.operational_hours = 0.0  # In-memory counter, resets on restart
        self.total_operations = 0
        self.bit_rotation_counter = 0  # Total bit rotations for wear tracking
        
        # Component health scores (0.0 to 1.0, where 1.0 is perfect health)
        self.component_health = {
            "motor": 1.0,
            "bearing": 1.0,
            "sensor": 1.0,
        }
        
        # Product catalog for random selection
        self.product_catalog = [
            "PROD-A100", "PROD-A200", "PROD-B150", "PROD-C300",
            "PROD-D250", "PROD-E175", "PROD-F225", "PROD-G190"
        ]

        logger.info(f"Telemetry generator initialized for {device_id}")

    def generate_screwing_event(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete screwing operation event with telemetry data.

        Args:
            config: Current runtime configuration from ConfigLoader

        Returns:
            Dictionary containing all telemetry data for the event
        """
        # Extract configuration
        speed_rpm = config["constant_speed_rpm"]
        anomaly_rate = config["anomaly_rate"]
        temp_threshold = config["temp_anomaly_threshold"]
        vibration_threshold = config["vibration_spike_threshold"]
        speed_variance = config["speed_variance_percent"]
        enable_degradation = config["enable_degradation"]

        # Determine if this operation will be anomalous
        is_anomaly = random.random() < anomaly_rate

        # Generate screwing duration
        duration = self._generate_duration(is_anomaly)

        # Generate actual speed (with potential anomaly)
        actual_speed = self._generate_speed(speed_rpm, is_anomaly, speed_variance)

        # Calculate rotation count
        rotation_count = int((actual_speed * duration) / 60.0)

        # Generate sensor readings
        temperature = self._generate_temperature(
            is_anomaly, temp_threshold, enable_degradation
        )
        vibration = self._generate_vibration(
            is_anomaly, vibration_threshold, enable_degradation
        )
        power_consumption = self._generate_power_consumption(
            actual_speed, duration, enable_degradation
        )

        # Update operational hours (convert duration to hours)
        self.operational_hours += duration / 3600.0

        # Update degradation if enabled
        if enable_degradation:
            self._apply_degradation(duration)

        # Update counters
        self.total_operations += 1
        self.bit_rotation_counter += rotation_count
        
        # Generate industrial screw tightening parameters
        product_id = random.choice(self.product_catalog)
        screw_position = random.randint(1, 8)  # 8 screw positions on assembly
        
        # Torque calculations (Nm) - target based on speed
        target_torque = round(15.0 + (actual_speed / 1800.0) * 10.0, 2)  # 15-25 Nm range
        torque_variance = 0.15 if is_anomaly else 0.05  # Higher variance for anomalies
        actual_torque = round(target_torque * random.uniform(1 - torque_variance, 1 + torque_variance), 2)
        
        # Angle calculations (degrees) - target based on rotations
        target_angle = rotation_count * 360
        angle_variance = 45 if is_anomaly else 15  # Higher variance for anomalies
        actual_angle = target_angle + random.randint(-angle_variance, angle_variance)
        
        # Pulse count (encoder pulses)
        pulse_count = rotation_count * 4  # 4 pulses per rotation
        
        # Determine cycle status and error code
        torque_ok = abs(actual_torque - target_torque) <= (target_torque * 0.1)  # ±10% tolerance
        angle_ok = abs(actual_angle - target_angle) <= 30  # ±30° tolerance
        duration_ok = 1.0 <= duration <= 3.0
        
        cycle_ok = torque_ok and angle_ok and duration_ok
        
        # Error codes: 0=OK, 1=Torque, 2=Angle, 3=Timeout, 4=Multiple
        error_code = 0
        if not cycle_ok:
            errors = []
            if not torque_ok:
                errors.append(1)
            if not angle_ok:
                errors.append(2)
            if not duration_ok:
                errors.append(3)
            error_code = errors[0] if len(errors) == 1 else 4
        
        # Cycle time in milliseconds
        cycle_time_ms = int(duration * 1000)

        # Build telemetry payload with industrial schema
        telemetry = {
            "Timestamp": datetime.now(timezone.utc).isoformat(),
            "MachineID": self.device_id,
            "ProductID": product_id,
            "ScrewPosition": screw_position,
            "TargetTorque": target_torque,
            "ActualTorque": actual_torque,
            "TargetAngle": target_angle,
            "ActualAngle": actual_angle,
            "PulseCount": pulse_count,
            "CycleOK": cycle_ok,
            "CycleTime_ms": cycle_time_ms,
            "SpindleRotationCounter": rotation_count,
            "BitRotationCounter": self.bit_rotation_counter,
            "ErrorCode": error_code,
        }

        logger.debug(
            f"{self.device_id}: Generated event "
            f"(CycleOK: {cycle_ok}, Torque: {actual_torque}Nm, Time: {cycle_time_ms}ms)"
        )

        return telemetry

    def _generate_duration(self, is_anomaly: bool) -> float:
        """
        Generate screwing operation duration.
        Normal: 1-3 seconds
        Anomaly: <1 second or >3 seconds

        Args:
            is_anomaly: Whether this should be an anomalous duration

        Returns:
            Duration in seconds
        """
        if is_anomaly:
            # 50% chance of too short, 50% chance of too long
            if random.random() < 0.5:
                # Too short: 0.3 to 0.9 seconds
                return random.uniform(0.3, 0.9)
            else:
                # Too long: 3.5 to 5.0 seconds
                return random.uniform(3.5, 5.0)
        else:
            # Normal operation: 1.0 to 3.0 seconds
            return random.uniform(1.0, 3.0)

    def _generate_speed(
        self, nominal_speed: float, is_anomaly: bool, variance_percent: float
    ) -> float:
        """
        Generate actual screwing speed with potential anomaly.

        Args:
            nominal_speed: Nominal constant speed in RPM
            is_anomaly: Whether this is an anomalous operation
            variance_percent: Percentage variance for speed anomalies

        Returns:
            Actual speed in RPM
        """
        if is_anomaly and random.random() < 0.3:  # 30% of anomalies affect speed
            # Speed drops during anomaly
            variance = random.uniform(0, variance_percent / 100.0)
            return nominal_speed * (1.0 - variance)
        else:
            # Normal operation with minor variance (±2%)
            variance = random.uniform(-0.02, 0.02)
            return nominal_speed * (1.0 + variance)

    def _generate_temperature(
        self, is_anomaly: bool, threshold: float, enable_degradation: bool
    ) -> float:
        """
        Generate temperature reading in Celsius.

        Args:
            is_anomaly: Whether this is an anomalous operation
            threshold: Temperature threshold for anomaly
            enable_degradation: Whether degradation affects temperature

        Returns:
            Temperature in Celsius
        """
        # Base temperature range: 60-75°C (normal operation)
        base_temp = random.uniform(60, 75)

        # Add degradation effect
        if enable_degradation:
            # Temperature rises as motor health degrades
            degradation_impact = (1.0 - self.component_health["motor"]) * 15
            base_temp += degradation_impact

        # Anomaly: temperature spike
        if is_anomaly and random.random() < 0.4:  # 40% of anomalies cause temp spike
            base_temp += random.uniform(threshold - base_temp, 25)

        return base_temp

    def _generate_vibration(
        self, is_anomaly: bool, threshold: float, enable_degradation: bool
    ) -> float:
        """
        Generate vibration reading in g-force.

        Args:
            is_anomaly: Whether this is an anomalous operation
            threshold: Vibration threshold for anomaly
            enable_degradation: Whether degradation affects vibration

        Returns:
            Vibration in g-force
        """
        # Base vibration: 0.2-0.6 g (normal operation)
        base_vibration = random.uniform(0.2, 0.6)

        # Add degradation effect
        if enable_degradation:
            # Vibration increases as bearing health degrades
            degradation_impact = (1.0 - self.component_health["bearing"]) * 1.5
            base_vibration += degradation_impact

        # Anomaly: vibration spike
        if is_anomaly and random.random() < 0.5:  # 50% of anomalies cause vibration
            base_vibration += random.uniform(
                threshold - base_vibration, threshold + 0.5
            )

        return max(0.1, base_vibration)  # Minimum 0.1 g

    def _generate_power_consumption(
        self, speed: float, duration: float, enable_degradation: bool
    ) -> float:
        """
        Generate power consumption in kilowatts.

        Args:
            speed: Actual screwing speed in RPM
            duration: Operation duration in seconds
            enable_degradation: Whether degradation affects power consumption

        Returns:
            Power consumption in kW
        """
        # Base power consumption proportional to speed
        # Typical screw robot: 3-6 kW
        base_power = 3.0 + (speed / 1800.0) * 3.0

        # Add degradation effect
        if enable_degradation:
            # Power consumption increases as motor efficiency degrades
            degradation_impact = (1.0 - self.component_health["motor"]) * 2.0
            base_power += degradation_impact

        # Add minor random variance
        base_power *= random.uniform(0.95, 1.05)

        return base_power

    def _apply_degradation(self, duration: float) -> None:
        """
        Apply component degradation based on operational hours.
        Different components degrade at different rates.

        Args:
            duration: Duration of the operation in seconds
        """
        # Degradation rates per 1000 hours of operation
        # Motor degrades fastest, sensors slowest
        degradation_rates = {
            "motor": 0.15,  # 15% degradation per 1000 hours
            "bearing": 0.12,  # 12% degradation per 1000 hours
            "sensor": 0.05,  # 5% degradation per 1000 hours
        }

        # Calculate degradation for this operation
        hours_fraction = duration / 3600.0  # Convert seconds to hours
        degradation_fraction = hours_fraction / 1000.0  # Per 1000 hours

        for component, rate in degradation_rates.items():
            # Apply degradation with some randomness
            degradation = rate * degradation_fraction * random.uniform(0.8, 1.2)
            self.component_health[component] = max(
                0.0, self.component_health[component] - degradation
            )

    def _determine_anomaly_type(
        self,
        duration: float,
        temperature: float,
        vibration: float,
        actual_speed: float,
        nominal_speed: float,
    ) -> str:
        """
        Determine the type of anomaly detected.

        Args:
            duration: Operation duration
            temperature: Temperature reading
            vibration: Vibration reading
            actual_speed: Actual speed
            nominal_speed: Nominal speed

        Returns:
            String describing the anomaly type
        """
        anomaly_types = []

        if duration < 1.0:
            anomaly_types.append("duration_too_short")
        elif duration > 3.0:
            anomaly_types.append("duration_too_long")

        if temperature > 85:
            anomaly_types.append("temperature_spike")

        if vibration > 2.0:
            anomaly_types.append("excessive_vibration")

        if actual_speed < nominal_speed * 0.85:
            anomaly_types.append("speed_drop")

        return ",".join(anomaly_types) if anomaly_types else "unspecified"

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get operational statistics for the device.

        Returns:
            Dictionary containing device statistics
        """
        return {
            "MachineID": self.device_id,
            "operationalHours": round(self.operational_hours, 2),
            "totalOperations": self.total_operations,
            "bitRotationCounter": self.bit_rotation_counter,
            "componentHealth": self.component_health,
        }
