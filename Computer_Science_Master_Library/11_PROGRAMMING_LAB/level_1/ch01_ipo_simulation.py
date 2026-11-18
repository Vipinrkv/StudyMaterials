"""
Practical Lab 1.1: Simulation of the Input-Process-Output (IPO) Cycle
File: 11_PROGRAMMING_LAB/level_1/ch01_ipo_simulation.py
Author: Computer Science Master Library
Description: Demonstrates raw data acquisition, conversion, logical
             and arithmetic processing, and human-readable information output.
"""

from typing import Dict, Any


def ingest_raw_sensor_data(sensor_voltage: float) -> float:
    """
    INPUT STAGE:
    Simulates analog-to-digital sensor voltage conversion.
    A temperature sensor outputs 0.0V to 3.3V representing -20°C to +80°C.
    """
    calculated_temp_celsius = (sensor_voltage / 3.3) * 100.0 - 20.0
    return round(calculated_temp_celsius, 2)


def process_temperature(temp_celsius: float) -> Dict[str, Any]:
    """
    PROCESSING STAGE:
    Applies business logic and arithmetic conversion to raw data.
    Transforms raw temperature into categorized information.
    """
    temp_fahrenheit = round((temp_celsius * 9.0 / 5.0) + 32.0, 2)

    if temp_celsius < 0.0:
        status = "FREEZING_WARNING"
        action_required = "Activate heating elements immediately."
    elif 0.0 <= temp_celsius <= 37.5:
        status = "NORMAL_OPTIMAL"
        action_required = "Maintain standard ventilation."
    elif 37.5 < temp_celsius <= 50.0:
        status = "ELEVATED_TEMPERATURE"
        action_required = "Activate secondary cooling fans."
    else:
        status = "CRITICAL_OVERHEAT"
        action_required = "Emergency shutdown triggered to protect equipment."

    return {
        "celsius": temp_celsius,
        "fahrenheit": temp_fahrenheit,
        "status": status,
        "action": action_required,
    }


def output_alert(info: Dict[str, Any]) -> None:
    """
    OUTPUT STAGE:
    Presents structured information to human operators or downstream systems.
    """
    print("=" * 60)
    print("        SERVER ROOM TELEMETRY MONITORING REPORT")
    print("=" * 60)
    print(f"Recorded Temperature : {info['celsius']} °C ({info['fahrenheit']} °F)")
    print(f"Operational Status   : {info['status']}")
    print(f"Required Protocol    : {info['action']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    raw_reading_1 = 1.65
    temp_1 = ingest_raw_sensor_data(raw_reading_1)
    report_1 = process_temperature(temp_1)
    output_alert(report_1)

    raw_reading_2 = 2.80
    temp_2 = ingest_raw_sensor_data(raw_reading_2)
    report_2 = process_temperature(temp_2)
    output_alert(report_2)
    print("All IPO tests passed successfully.")
