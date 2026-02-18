import odrive
import fibre.libfibre
import math
import time
import sys

if len(sys.argv) != 2 or sys.argv[1] not in ["0", "1"]:
    print("Usage: python script.py [0|1]")
    sys.exit(1)

axis_id = int(sys.argv[1])

print(f"Configuring Axis {axis_id}...")

# Erase config (ODrive will disconnect)
dev0 = odrive.find_any()
try:
    dev0.erase_configuration()
except fibre.libfibre.ObjectLostError:
    pass

dev0 = odrive.find_any()
ax = dev0.axis0 if axis_id == 0 else dev0.axis1
mo = ax.motor
enc = ax.encoder
contr = ax.controller

# General configuration
mo.config.current_lim = 22.0
mo.config.current_lim_margin = 9.0
enc.config.cpr = 16384                         
mo.config.pole_pairs = 20
mo.config.torque_constant = 0.025  # 8.27/90  

contr.config.pos_gain = 60
contr.config.vel_gain = 0.1
contr.config.vel_integrator_gain = 0.2
contr.config.vel_limit = math.inf 

# Encoder SPI settings
dev0.config.gpio7_mode = 0  # digital
dev0.config.gpio8_mode = 0  # digital
enc.config.abs_spi_cs_gpio_pin = 7 if axis_id == 0 else 8
enc.config.mode = 257  # ABS_SPI

# Optional power-related config
dev0.config.brake_resistance = 2.0
dev0.config.dc_bus_undervoltage_trip_level = 8.0
# dev0.config.dc_bus_overvoltage_trip_level = 56.0
# dev0.config.dc_max_positive_current = 20.0
# dev0.config.dc_max_negative_current = -3.0

dev0.config.enable_brake_resistor = True

try:
    dev0.save_configuration()
    dev0.reboot()
except fibre.libfibre.ObjectLostError:
    pass

# Reconnect after reboot
dev0 = odrive.find_any()
ax = dev0.axis0 if axis_id == 0 else dev0.axis1
mo = ax.motor
enc = ax.encoder
contr = ax.controller

# Calibrate motor
print("Starting motor calibration...")
ax.requested_state = 4  # FULL_CALIBRATION_SEQUENCE
while not mo.is_calibrated:
    time.sleep(2)
    print(f"motor {axis_id} not calibrated")
    print(mo.error)
mo.config.pre_calibrated = True

# Calibrate encoder
print("Starting encoder calibration...")
ax.requested_state = 7  # ENCODER_OFFSET_CALIBRATION
while not enc.is_ready:
    time.sleep(2)
    print(f"encoder {axis_id} not calibrated")
    print(enc.error)
enc.config.pre_calibrated = True

# Enable startup closed loop only for selected axis
ax.config.startup_closed_loop_control = True
dev0.clear_errors()

try:
    dev0.save_configuration()
except fibre.libfibre.ObjectLostError:
    pass

print(f"Axis {axis_id} successfully configured and calibrated.")
