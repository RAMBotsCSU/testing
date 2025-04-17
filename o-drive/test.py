import odrive

odrv = odrive.find_any()

odrv.axis0.config.voltage_limit = 48
odrv.config.dc_bus_overvoltage_trip_level = 53
odrv.config.enable_brake_resistor = True
odrv.config.brake_resistance = 2.0  # Example value — depends on your resistor
odrv.axis0.motor.config.current_lim = 30  # Adjust based on motor
odrv.axis0.controller.config.vel_limit = 2000  # Adjust as needed
