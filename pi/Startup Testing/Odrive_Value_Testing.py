#Set of functions that test if the ODESC values passed to it are correct within a certain percentage
#Input: dict of values of the form {<valuename1>: <valuenum1>.....}
#Output: (True, {}) if all values pass, (False, {<incorrectvals>}) if any values don't pass
#
#the correct_values dictionary below shows all values that are checked
#if there are values passed in that are not in correct_values, they are not checked


#max % different any two values can be - used so direct float comparison doesn't happen
PERCENT_DIFFERENCE = 1

# Correct Values
correct_values_axis0 = {'encoder.config.abs_spi_cs_gpio_pin': '0.00', 'encoder.config.cpr': '7.00', 'encoder.config.mode': '16384.00', 'motor.config.current_lim': '257.00', 'motor.config.current_lim_margin': '22.00', 'motor.config.pole_pairs': '9.00', 'motor.config.torque_constant': '20.00', 'controller.config.pos_gain': '0.03', 'controller.config.vel_gain': '50.00', 'controller.config.vel_integrator_gain': '0.10', 'controller.config.vel_limit': '0.08'}

correct_values_axis1 = {'encoder.config.abs_spi_cs_gpio_pin': '257.00', 'encoder.config.cpr': '8.00', 'encoder.config.mode': '16384.00', 'motor.config.current_lim': '0.03', 'motor.config.current_lim_margin': '22.00', 'motor.config.pole_pairs': '9.00', 'motor.config.torque_constant': '20.00', 'controller.config.pos_gain': '', 'controller.config.vel_gain': '50.00', 'controller.config.vel_integrator_gain': '0.10', 'controller.config.vel_limit': '0.08'}


def value_checker(odrive_values, correct_values):
    #checks the values against the correct values

    if (type(odrive_values) is not dict):
        return (False, {"Error": "value_checker: nested dictionary was not passed in"})

    error_dict = {}

    if (odrive_values == correct_values):
        return (True, {})
    
    
    for key, expected_value in correct_values.items():
        actual_value = odrive_values[key]

        if (actual_value != expected_value):
            error_dict[key] = actual_value

    return (len(error_dict) == 0, error_dict)


{'odrive1': 
 {'axis0': 
  {'encoder.config.abs_spi_cs_gpio_pin': '0.00', 'encoder.config.cpr': '7.00', 'encoder.config.mode': '16384.00', 'motor.config.current_lim': '257.00', 'motor.config.current_lim_margin': '22.00', 'motor.config.pole_pairs': '9.00', 'motor.config.torque_constant': '20.00', 'controller.config.pos_gain': '0.03', 'controller.config.vel_gain': '50.00', 'controller.config.vel_integrator_gain': '0.10', 'controller.config.vel_limit': '0.08'}, 
  'axis1': 
  {'encoder.config.abs_spi_cs_gpio_pin': '257.00', 'encoder.config.cpr': '8.00', 'encoder.config.mode': '16384.00', 'motor.config.current_lim': '0.03', 'motor.config.current_lim_margin': '22.00', 'motor.config.pole_pairs': '9.00', 'motor.config.torque_constant': '20.00', 'controller.config.pos_gain': '', 'controller.config.vel_gain': '50.00', 'controller.config.vel_integrator_gain': '0.10', 'controller.config.vel_limit': '0.08'}}, 
  'odrive2': {'axis0': {}, 'axis1': {}}, 
  'odrive3': {'axis0': {}, 'axis1': {}}, 
  'odrive4': {'axis0': {}, 'axis1': {}}, 
  'odrive5': {'axis0': {}, 'axis1': {}}, 
  'odrive6': {'axis0': {}, 'axis1': {}}}


def input_func(input_dict):
    error_list = []
    for odrivename, odrivedict in input_dict.items():
        for axisname, axisdict in odrivedict.items():
            if axisname == "axis0":
                axis_correct_dict = correct_values_axis0
            else:
                axis_correct_dict = correct_values_axis1
            
            output = value_checker(axisdict, axis_correct_dict)

            if output[0] is False:
                value_checker_dict = output[1]

                for param, value in value_checker_dict.items():
                    error_string = "In " + odrivename + ", " + axisname + ": "
                    error_string += param + " is " + value + ", should be: " + axis_correct_dict[param]
                    error_list.append(error_string)
    
    return (len(error_list) == 0, error_list)


other_vals = {'odrive1': 
 {'axis0': 
  {'encoder.config.abs_spi_cs_gpio_pin': '0.00', 'encoder.config.cpr': '7.00', 'encoder.config.mode': '16384.00', 'motor.config.current_lim': '257.00', 'motor.config.current_lim_margin': '22.00', 'motor.config.pole_pairs': '9.00', 'motor.config.torque_constant': '20.00', 'controller.config.pos_gain': '0.03', 'controller.config.vel_gain': '50.00', 'controller.config.vel_integrator_gain': '0.10', 'controller.config.vel_limit': '0.08'}, 
  'axis1': 
  {'encoder.config.abs_spi_cs_gpio_pin': '257.00', 'encoder.config.cpr': '8.00', 'encoder.config.mode': '16384.00', 'motor.config.current_lim': '0.03', 'motor.config.current_lim_margin': '22.00', 'motor.config.pole_pairs': '9.00', 'motor.config.torque_constant': '20.00', 'controller.config.pos_gain': '', 'controller.config.vel_gain': '50.00', 'controller.config.vel_integrator_gain': '0.10', 'controller.config.vel_limit': '0.08'}}}



print(input_func(other_vals))