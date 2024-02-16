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

correct_shoulder_values = {}

correct_knee_values = {}



def percent_error_checker(trueval, expectedval):
    #checks if expectedval is more than 1% different from trueval and returns False if so
    pass



def value_checker(odrive_values, correct_values):
    #checks the hip values against correct_hip_values
    odrive_value_dict = odrive_values[str(list(odrive_values.keys())[0])] #gets the dictionary with all values

    if (type(odrive_value_dict) is not dict):
        return (False, {"Error": "value_checker: nested dictionary was not passed in"})

    error_dict = {}

    if (odrive_value_dict == correct_values):
        return (True, {})
    
    
    for key, expected_value in correct_values.items():
        actual_value = odrive_value_dict[key]

        if (actual_value != expected_value):
            if (not percent_error_checker(actual_value, expected_value)):
                error_dict[key] = actual_value

    return (False, error_dict)




def odrive_values_test(odrive_values):
    #input function
    #checks if motor is hip, shoulder, or knee and redirects appropriately
    
    motor_name = list(odrive_values.keys())[0][2] #gets the third char of the motor name - will be H, S, or K
    
    if (motor_name == 'H'):
        return value_checker(odrive_values, correct_hip_values)
    elif (motor_name == 'S'):
        return value_checker(odrive_values, correct_shoulder_values)
    elif (motor_name == 'K'):
        return value_checker(odrive_values, correct_knee_values)
    else:
        return (False, {"Error": "odrive_values_test: incorrect motor name"})

