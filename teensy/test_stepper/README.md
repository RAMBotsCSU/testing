# MotorMovement
Config setup steps and code used for movement


# Odrive Config Setup Steps:

-> Plug in with power  
-> In terminal/command window:  
odrivetool  
dump_errors(odrv0)  
odrv0.axis0.clear_errors()  
odrv0.axis1.clear_errors()  
odrv0.axis0.encoder.config.cpr = 4000  
odrv0.axis1.encoder.config.cpr = 4000  
odrv0.axis0.motor.config.pole_pairs = 20  
odrv0.axis1.motor.config.pole_pairs = 20  
odrv0.axis0.motor.config.torque_constant = 8.27/90  
odrv0.axis1.motor.config.torque_constant = 8.27/90  
odrv0.axis0.controller.config.pos_gain = 60  
odrv0.axis1.controller.config.pos_gain = 60  
odrv0.axis0.controller.config.vel_gain = 0.1  
odrv0.axis1.controller.config.vel_gain = 0.1  
odrv0.axis0.controller.config.vel_integrator_gain = 0.2  
odrv0.axis1.controller.config.vel_integrator_gain = 0.2  
import math  
odrv0.axis0.controller.config.vel_limit = math.inf  
odrv0.axis1.controller.config.vel_limit = math.inf  
odrv0.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION  
odrv0.axis1.requested_state = AXIS_STATE_MOTOR_CALIBRATION  
odrv0.axis0.motor.config.pre_calibrated = True  
odrv0.axis1.motor.config.pre_calibrated = True  
odrv0.axis0.requested_state = AxisState.ENCODER_INDEX_SEARCH  
odrv0.axis1.requested_state = AxisState.ENCODER_INDEX_SEARCH  
odrv0.axis0.requested_state = AxisState.ENCODER_OFFSET_CALIBRATION  
odrv0.axis1.requested_state = AxisState.ENCODER_OFFSET_CALIBRATION  
odrv0.axis0.config.startup_encoder_index_search = True  
odrv0.axis1.config.startup_encoder_index_search = True  
odrv0.axis0.encoder.config.pre_calibrated = True  
odrv0.axis1.encoder.config.pre_calibrated = True  
odrv0.axis0.config.startup_closed_loop_control = True  
odrv0.axis1.config.startup_closed_loop_control = True  
odrv0.save_configuration()  
odrv0.reboot()  