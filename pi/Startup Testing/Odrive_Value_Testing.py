#Set of functions that test if the ODESC values passed to it are correct within a certain percentage
#Input: dict of values of the form {<motor name>: {<valuename1>: <valuenum1>.....}}
#Output: (True, {}) if all values pass, (False, {<incorrectvals>}) if any values don't pass

# Correct Values
correct_hip_values = {
                      "PARAM_FLOAT_POS_SETPOINT": 0,
                      "PARAM_FLOAT_POS_GAIN": 0,
                      "PARAM_FLOAT_VEL_SETPOINT": 0,
                      "PARAM_FLOAT_VEL_GAIN": 0,
                      "PARAM_FLOAT_VEL_INTEGRATOR_GAIN": 0,
                      "PARAM_FLOAT_VEL_INTEGRATOR_CURRENT": 0,
                      "PARAM_FLOAT_VEL_LIMIT": 0,
                      "PARAM_FLOAT_CURRENT_SETPOINT": 0,
                      "PARAM_FLOAT_CALIBRATION_CURRENT": 0,
                      "PARAM_FLOAT_PHASE_INDUCTANCE": 0,
                      "PARAM_FLOAT_PHASE_RESISTANCE": 0,
                      "PARAM_FLOAT_CURRENT_MEAS_PHB": 0,
                      "PARAM_FLOAT_CURRENT_MEAS_PHC": 0,
                      "PARAM_FLOAT_DC_CALIB_PHB": 0,
                      "PARAM_FLOAT_DC_CALIB_PHC": 0,
                      "PARAM_FLOAT_SHUNT_CONDUCTANCE": 0,
                      "PARAM_FLOAT_PHASE_CURRENT_REV_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_CURRENT_LIM": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_P_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_I_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_V_CURRENT_CONTROL_INTEGRAL_D": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_V_CURRENT_CONTROL_INTEGRAL_Q": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_IBUS": 0,
                      "PARAM_FLOAT_ENCODER_PHASE": 0,
                      "PARAM_FLOAT_ENCODER_PLL_POS": 0,
                      "PARAM_FLOAT_ENCODER_PLL_VEL": 0,
                      "PARAM_FLOAT_ENCODER_PLL_KP": 0,
                      "PARAM_FLOAT_ENCODER_PLL_KI": 0
                      }


correct_shoulder_values = {
                      "PARAM_FLOAT_POS_SETPOINT": 0,
                      "PARAM_FLOAT_POS_GAIN": 0,
                      "PARAM_FLOAT_VEL_SETPOINT": 0,
                      "PARAM_FLOAT_VEL_GAIN": 0,
                      "PARAM_FLOAT_VEL_INTEGRATOR_GAIN": 0,
                      "PARAM_FLOAT_VEL_INTEGRATOR_CURRENT": 0,
                      "PARAM_FLOAT_VEL_LIMIT": 0,
                      "PARAM_FLOAT_CURRENT_SETPOINT": 0,
                      "PARAM_FLOAT_CALIBRATION_CURRENT": 0,
                      "PARAM_FLOAT_PHASE_INDUCTANCE": 0,
                      "PARAM_FLOAT_PHASE_RESISTANCE": 0,
                      "PARAM_FLOAT_CURRENT_MEAS_PHB": 0,
                      "PARAM_FLOAT_CURRENT_MEAS_PHC": 0,
                      "PARAM_FLOAT_DC_CALIB_PHB": 0,
                      "PARAM_FLOAT_DC_CALIB_PHC": 0,
                      "PARAM_FLOAT_SHUNT_CONDUCTANCE": 0,
                      "PARAM_FLOAT_PHASE_CURRENT_REV_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_CURRENT_LIM": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_P_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_I_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_V_CURRENT_CONTROL_INTEGRAL_D": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_V_CURRENT_CONTROL_INTEGRAL_Q": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_IBUS": 0,
                      "PARAM_FLOAT_ENCODER_PHASE": 0,
                      "PARAM_FLOAT_ENCODER_PLL_POS": 0,
                      "PARAM_FLOAT_ENCODER_PLL_VEL": 0,
                      "PARAM_FLOAT_ENCODER_PLL_KP": 0,
                      "PARAM_FLOAT_ENCODER_PLL_KI": 0
                      }


correct_knee_values = {
                      "PARAM_FLOAT_POS_SETPOINT": 0,
                      "PARAM_FLOAT_POS_GAIN": 0,
                      "PARAM_FLOAT_VEL_SETPOINT": 0,
                      "PARAM_FLOAT_VEL_GAIN": 0,
                      "PARAM_FLOAT_VEL_INTEGRATOR_GAIN": 0,
                      "PARAM_FLOAT_VEL_INTEGRATOR_CURRENT": 0,
                      "PARAM_FLOAT_VEL_LIMIT": 0,
                      "PARAM_FLOAT_CURRENT_SETPOINT": 0,
                      "PARAM_FLOAT_CALIBRATION_CURRENT": 0,
                      "PARAM_FLOAT_PHASE_INDUCTANCE": 0,
                      "PARAM_FLOAT_PHASE_RESISTANCE": 0,
                      "PARAM_FLOAT_CURRENT_MEAS_PHB": 0,
                      "PARAM_FLOAT_CURRENT_MEAS_PHC": 0,
                      "PARAM_FLOAT_DC_CALIB_PHB": 0,
                      "PARAM_FLOAT_DC_CALIB_PHC": 0,
                      "PARAM_FLOAT_SHUNT_CONDUCTANCE": 0,
                      "PARAM_FLOAT_PHASE_CURRENT_REV_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_CURRENT_LIM": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_P_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_I_GAIN": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_V_CURRENT_CONTROL_INTEGRAL_D": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_V_CURRENT_CONTROL_INTEGRAL_Q": 0,
                      "PARAM_FLOAT_CURRENT_CONTROL_IBUS": 0,
                      "PARAM_FLOAT_ENCODER_PHASE": 0,
                      "PARAM_FLOAT_ENCODER_PLL_POS": 0,
                      "PARAM_FLOAT_ENCODER_PLL_VEL": 0,
                      "PARAM_FLOAT_ENCODER_PLL_KP": 0,
                      "PARAM_FLOAT_ENCODER_PLL_KI": 0
                      }




def odrive_values_test(odrive_values):
    #input function
    #checks if motor is hip, shoulder, or knee and redirects appropriately
    pass