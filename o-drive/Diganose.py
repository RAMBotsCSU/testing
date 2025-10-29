#!/usr/bin/env python3
"""
ODrive Error Diagnostic + Auto-Clear Tool
Author: ChatGPT (GPT-5)
Date: 2025-10-14

Connects to an ODrive, prints detailed diagnostics for each axis,
and optionally clears all detected errors.
"""

import odrive
from odrive.enums import *
import time

def decode_errors(error_value, error_dict):
    """Convert bitfield error values into human-readable names."""
    if error_value == 0:
        return ["no error"]
    errors = []
    for name, value in error_dict.items():
        if error_value & value:
            errors.append(name)
    return errors

def print_error_report(axis, axis_name="axis"):
    """Prints a detailed report for a given ODrive axis."""
    print(f"\n--- {axis_name.upper()} DIAGNOSTIC REPORT ---")

    axis_errors = decode_errors(axis.error, AXIS_ERROR)
    print(f"Axis Error(s): {', '.join(axis_errors)}")

    motor_errors = decode_errors(axis.motor.error, MOTOR_ERROR)
    print(f"Motor Error(s): {', '.join(motor_errors)}")

    encoder_errors = decode_errors(axis.encoder.error, ENCODER_ERROR)
    print(f"Encoder Error(s): {', '.join(encoder_errors)}")

    controller_errors = decode_errors(axis.controller.error, CONTROLLER_ERROR)
    print(f"Controller Error(s): {', '.join(controller_errors)}")

    # Optional subcomponents
    if hasattr(axis, "sensorless_estimator"):
        print(f"Sensorless Estimator Error: {axis.sensorless_estimator.error}")

    if hasattr(axis.motor, "drv_fault"):
        drv = axis.motor.drv_fault
        print(f"DRV Fault: {drv if drv else 'none'}")

def clear_axis_errors(axis, axis_name="axis"):
    """Clears errors for a given ODrive axis."""
    print(f"Clearing errors for {axis_name}...")
    axis.clear_errors()
    time.sleep(0.2)
    print(f"{axis_name} errors cleared.\n")

def main():
    print("🔍 Connecting to ODrive... (this may take a few seconds)")
    odrv = odrive.find_any()
    print("✅ Connected to ODrive.")
    print(f"Firmware version: {odrv.fw_version_major}.{odrv.fw_version_minor}.{odrv.fw_version_revision}")

    # System-level error
    print(f"\nSystem Error: {odrv.system_stats.error}")

    # Diagnostic reports
    print_error_report(odrv.axis0, "axis0")
    try:
        print_error_report(odrv.axis1, "axis1")
    except AttributeError:
        print("\nNo axis1 detected on this ODrive.")

    # Ask user if they want to clear
    resp = input("\nDo you want to clear all ODrive errors now? (y/N): ").strip().lower()
    if resp == "y":
        clear_axis_errors(odrv.axis0, "axis0")
        try:
            clear_axis_errors(odrv.axis1, "axis1")
        except AttributeError:
            pass
        print("✅ All errors cleared successfully.")
    else:
        print("ℹ️ Errors left intact. No changes made.")

    print("\n✅ Diagnostic complete.")

if __name__ == "__main__":
    main()
