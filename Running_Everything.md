# Running Everyting

After learning about the magic of PipFile, the goal is to run all of our test code from the command line and combine everything into a single test suite.

## Requirements
* pip, python, and pipenv must be installed to run this supercode, so get those on your path
* For windows use 
```
py -m pip install pipenv
``` 
and 
```
py -m pipenv run <SCRIPTNAME>
```
* any non-python code should be run from it's respective directory

## Running the Code

### LIDAR Scripts
Test out running the LiDAR sensor and displaying it in real-time:
```
pipenv run lidar_sim
```

### O-Drive Scripts
Run current calibration script (Recommended):
```
pipenv run calibrate
```

Run old calibration script:
```
pipenv run calibrate_old
```

Run simple diagnostic script:
```
pipenv run diagnostic
```

Run single motor calibration axis 0 (for the testbench hip):
```
pipenv run calibrate_axis0
```

Run single motor calibration axis 1:
```
pipenv run calibrate_axis1
```

### Plotter Code
Run code that plots current in real-time (O-Drive must be plugged in):
```
pipenv run plotter
```

### Single Leg Test Code
Run old code to operate single leg (old teensy code must be loaded):
```
pipenv run com_sim
```

Run single leg code for Linux:
```
pipenv run com_sim_linux
```
