import odrive
import fibre.libfibre
import math
import time
import sys
import os

#erase config, except that the oDrive will disconnect
dev0 = odrive.find_any()
try:
    dev0.erase_configuration()
except fibre.libfibre.ObjectLostError:
    pass

#refind oDrive and simplify naming scheme
dev0 = odrive.find_any()
ax0 = dev0.axis0
ax1 = dev0.axis1
mo0 = ax0.motor
mo1 = ax1.motor
enc0 = ax0.encoder
enc1 = ax1.encoder
contr0 = ax0.controller
contr1 = ax1.controller

mo0.config.current_lim = 22.0
mo1.config.current_lim = 22.0
mo0.config.current_lim_margin = 9.0
mo1.config.current_lim_margin = 9.0
enc0.config.cpr = 16384                         
enc1.config.cpr = 16384                         #Has different value in SPI
mo0.config.pole_pairs = 20
mo1.config.pole_pairs = 20
mo0.config.torque_constant = 8.27/90
mo1.config.torque_constant = 8.27/90
contr0.config.pos_gain = 60
contr1.config.pos_gain = 60
contr0.config.vel_gain = 0.1
contr1.config.vel_gain = 0.1
contr0.config.vel_integrator_gain = 0.2
contr1.config.vel_integrator_gain = 0.2
contr0.config.vel_limit = math.inf              #500 without resistors
contr1.config.vel_limit = math.inf              #500 without resistors

# odrv0.config.brake_resistance = 2.0 //if have resistors
# odrv0.config.dc_bus_undervoltage_trip_level = 8.0
# odrv0.config.dc_bus_overvoltage_trip_level = 56.0
# odrv0.config.dc_max_positive_current = 20.0
# odrv0.config.dc_max_negative_current = -3.0
# odrv0.config.max_regen_current = 0

dev0.config.gpio7_mode = 0                      #Set pin to digital
dev0.config.gpio8_mode = 0                      #Set pin to digital
enc0.config.abs_spi_cs_gpio_pin = 7             #Set pin to SPI mode
enc1.config.abs_spi_cs_gpio_pin = 8             #Set pin to SPI mode
enc0.config.mode = 257                          #Set encoder to SPI mode
enc1.config.mode = 257                          #Set encoder to SPI mode

try:
    dev0.save_configuration()
    dev0.reboot()
except fibre.libfibre.ObjectLostError:
    pass
dev0 = odrive.find_any()
ax0 = dev0.axis0
ax1 = dev0.axis1
mo0 = ax0.motor
mo1 = ax1.motor
enc0 = ax0.encoder
enc1 = ax1.encoder
contr0 = ax0.controller
contr1 = ax1.controller



ax0.requested_state = 4                         #Motor calibration
while(not(mo0.is_calibrated)):
    time.sleep(2)
    print('motor 0 not calibrated')
    print(mo0.error)
mo0.config.pre_calibrated = True

ax1.requested_state = 4                         #Motor calibration
while(not(mo1.is_calibrated)):
    time.sleep(2)
    print('motor 1 not calibrated')
    print(mo1.error)
mo1.config.pre_calibrated = True

ax0.requested_state = 7                         #Encoder calibration
while(not(enc0.is_ready)):
    time.sleep(2)
    print('encoder 0 not calibrated')
    print(enc0.error)
enc0.config.pre_calibrated = True

ax1.requested_state = 7                         #Encoder calibration
while(not(enc1.is_ready)):
    time.sleep(2)
    print('encoder 1 not calibrated')
    print(enc1.error)
enc1.config.pre_calibrated = True

dev0.config.enable_brake_resistor = True        #If have resistors (resistance is at 2 ohms per default)
dev0.clear_errors()                             #Must do this to enable resistor
ax0.config.startup_closed_loop_control = True   #Go into closed loop on restart
ax1.config.startup_closed_loop_control = True   #Go into closed loop on restart

try:
    dev0.save_configuration()
except fibre.libfibre.ObjectLostError:
    pass

