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
    print("Connecting to ODrive... (this may take a few seconds)")
    try:
        odrv = odrive.find_any()
    except Exception as e:
        print(f"ERROR: Failed to connect to ODrive: {e}")
        return
    
    print("Connected to ODrive.")
    
    try:
        print(f"Firmware version: {odrv.fw_version_major}.{odrv.fw_version_minor}.{odrv.fw_version_revision}")
    except (AttributeError, Exception) as e:
        print(f"Warning: Could not read firmware version: {e}")

    # System-level error
    try:
        print(f"\nSystem Error: {odrv.system_stats.error}")
    except (AttributeError, Exception) as e:
        print(f"Warning: Could not read system stats: {e}")

    # Diagnostic reports
    try:
        print_error_report(odrv.axis0, "axis0")
    except (AttributeError, Exception) as e:
        print(f"\nError reading axis0: {e}")
    
    try:
        print_error_report(odrv.axis1, "axis1")
    except AttributeError:
        print("\nNo axis1 detected on this ODrive.")
    except Exception as e:
        print(f"\nError reading axis1: {e}")

    # Ask user if they want to clear
    resp = input("\nDo you want to clear all ODrive errors now? (y/N): ").strip().lower()
    if resp == "y":
        try:
            clear_axis_errors(odrv.axis0, "axis0")
        except (AttributeError, Exception) as e:
            print(f"Error clearing axis0: {e}")
        
        try:
            clear_axis_errors(odrv.axis1, "axis1")
        except AttributeError:
            pass
        except Exception as e:
            print(f"Error clearing axis1: {e}")
        
        print("All errors cleared successfully.")
    else:
        print("Errors left intact. No changes made.")

    print("\nDiagnostic complete.")

if __name__ == "__main__":
    main()
