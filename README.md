# RamBOTs Testing Repo
                   
This is the official CSU RAMBots testing repository. 
Visit us at our [website](https://projects-web.engr.colostate.edu/ece-sr-design/AY22/RamBOTs).


<img src="https://user-images.githubusercontent.com/112744753/196563382-2745e707-77d6-42d5-98a0-a29530e21c9a.png" width=50% height=50%>

Files:
------

| File                       | Description           |
| ---------------------------|-------------|
| README                     | this file |
| teensy/teensy_serial_main/...     | Serial communication between the Pi and Teensy from the Teensy's end      |
| teensy/test_rambot_gyro/...    | Test of gyroscope implementation on the Teensy      |
| teensy/test_stepper/...    | MechE's basic motor test program      |
| teensy/MechETest/...    | MechE's test program for ODrive and encoder implementation     |
| pi/pi_serial_main.py    | Serial communication between the Pi and Teensy from the Pi's end      |
| pi/color_test.sh    | Bash script used to change LED color of the PS4 controller      |
| pi/PiGUI/...   | RamBOT GUI for Pi touchscreen display      |
| O-Drives/ConfigSteps  | Instructions for configuring an ODrive for initialization     |


History:
--------
 **2022-10-12:**  
 <pre>Began work to connect PS4 controller to the Raspberry Pi via bluetooth using the pyps4 library.
 Began work on serial communication between the Raspberry Pi and Teensy via microUSB.
 Pushed:  PiPS4_test.py
          serial_test.py
          serial_test_single.py
          </pre>

 **2022-10-13:**  
 <pre>Combined the PS4 and serial communication test scripts to pass buttons pressed on the controller
 to the Pi and finally to the Teensy. Works consistently, but with large gaps in timing. Button presses
 take ~1.25 seconds to be received on the Pi. Will look into why this is later.
 Pushed:   Serial_and_PS4_test.py
</pre>

 **2022-10-18:**  
 <pre>Improved serial communication program. It seems the Pi waits a second for the serial buffer to fill
 before sending a message. Passing a 127 character string will happen near-instantaneously, for instance.
 Created a padding function to make every button press be sent as a 127 character string. Pi-Teensy communication
 should now be sufficiently fast. 
 Updated:   Serial_and_PS4_test.py
</pre>

 **2022-10-19:**  
 <pre>The pyps4 library works very well, but takes over control of the entire program. Worked on finding a way
 to break out of the pyps4 script, but made little progess. Tried multithreading, but struggled to share
 variables between the threads while locked in the pyps4 loop. Ultimately decided to work with an older library,
 pygame. Pygame functions entirely within a while loop that can easily be entered and exited as desired. Kept
 multithreading functionality. Need to make sure child threads are killed once program stops. Also, CPU usage
 on this program can exceed 50%. This is undesirable as the machine learning program requires over 50% CPU usage
 as well. Will look into limiting the resources of each thread. 
 Updated:   Serial_and_PS4_test.py
 Pushed:    multithreading_Serial_PS4_Test.py
            multithreadingTest.py
            pygame_test.py     
</pre>


 **2022-10-20:**  
 <pre>Ensured child threads are terminated upon closure of the program. Added support for changing the color
 of the PS4 controller's LEDs with the change of controller mode.
 Pushed:   color_test.py
           pi_serial_main.py
</pre>


 **2022-10-24:**  
 <pre>Added code for the Teensy. Reorganized directory with subfolders for Pi and Teensy code
 Pushed:   teensy_serial_main.ino
</pre>

 **2022-11-02:**  
 <pre>Improved communication between the controller, Pi, and Teensy, Axes for the left joystick, right joystick,
 left trigger, and right trigger are normalized to the range [-1.0,1.0] and sent to the Teensy in an array which 
 is acknowledged and returned to the Pi. These six axes are likely the most complex values which will be sent to 
 the Teensy--programming the rest of the buttons into this array should be fairly trivial. Next step is to parse 
 this data in the Teensy and reorganize it intoo the format expected by the OpenDogV3 code.
 Updated:   teensy_serial_main.ino
            pi_serial_main.py
</pre>

 **2022-11-10:**  
 <pre>Changed heightto be controlled by the D-pad up and down (0.2,-0.2), setting to 0 when neither are pressed.
 Left trigger and right triggered both control the roll, (-1:0) on left (0:1) on right. Implemented a trigger lock
 to ensure only one trigger is presssed at a time. Implemented a mode lock to disable controls if mode is not on
 mode 0. Values are set to defaults if mode is switched. Enabled keyword detection for the driver thread and the
 teensy.
 Updated:   teensy_serial_main.ino
            pi_serial_main.py
</pre>

 **2022-11-15:**  
 <pre>Integrated OpenDogV3 code into serial_test.ino. Added files ODriveInit.ino and kinematics.ino, which are called
 from within serial_test.ino. Corrected all dependencies and removed code that will not be used. Program successfully
 compiles and calls the OpenDog kinematics function, but has not been tested yet.
 Updated:   teensy_serial_main.ino

</pre>

 **2022-11-16:**  
 <pre>Troubleshooting the integration of OpenDog. Attempting to call the kinematics function the Teensy hangs.
 This occurs at a call to odrive.setposition and its cause is currently unknown. Possibly due to no feedback
 from a connected ODrive or problems with serial ports. Will look into this next time.
 Updated:   teensy_serial_main.ino

</pre>

 **2022-11-17:**  
 <pre>Began implementation of user interface using PiGUI. Currently a simple test program that displays the RamBOTs
 logo. Added Kyle's test program for gyroscope implementation. Added MechE's motor test program.
 Added:   pi/PiGUI/...
          teensy/test_rambot_gyro/...

</pre>

 **2022-11-28:**  
 <pre>Over break made great progress on the implementation of ODrives and motor encoders. teensy_serial_main has
 been updated to reflect these developments and soon move an entire leg. Added teensy/MechETest which contains
 the tests the mechanical engineers created to get the ODrives and encoders working. Added O-Drives/ConfigSteps
 which contains the instructions for configuring an ODrive.
 Updated:   teensy/teensy_serial_main.ino
 Added:     teesny/MechETest
            O-Drives/ConfigSteps

</pre>

 **2022-11-30:**  
 <pre>Looked into PiSimpleGUI and PyGame examples. PiSimpleGUI seems ideal for the RamBOT GUI, though PyGame
 notably offers support for playing mp3 files which may be utilized in the final product. Will begin work
 on the official GUI soon.
 Added:     pi/PiGUI/Dashboard_Example.py
            pi/PiGUI/pygame_Test.py
            pi/PiGUI/Demo_Animated_GIFS.py

</pre>

</pre>

 **2022-12-08:**  
 <pre>Modified the Odrive configuration to remove the closed loop control on startup. Modified the teensy code to enable closed loop control after index's have been found.
 Updated:    teensy/teensy_serial_main.ino

</pre>

 **2023-01-17:**  
 <pre>Set up a USB speaker on the Pi to make the RamBOT play sounds on command using pygame. Currently, pressing the left
 d-pad will randomly play one of four sheep sounds. In the future this will be used for a low battery alarm.
 Updated:    pi_serial_main.py
             pi/PiGUI/pygame_Test.py

</pre>


 **2023-01-19:**  
 <pre>Began work on RamBOTs GUI using PySimpleGUI. Practiced using the library's features and created a basic prototype with
 multiple tabs to switch between windows. Not yet sure how seamlessly the machine learning webcam feed and multithreading can
 be incorporated into PySimpleGUI. Next step is to continue work on prototype and look into these features. 
 Added:    pi/PiGUI/RamBOTs_UI.py    

</pre>

 **2023-01-30:**  
 <pre>Imported contents of the mechs' temporary repository.
 Added:    O-Drives/SinWaveTest 

</pre>

 **2023-03-20:**  
 <pre>Created standalone kinematics to test kinematics function without a PS4 controller. Includes different functions to test
 including range of motion, setting specific values, and testing functions. Kinematics helper was created to make our programming
 mesh more easily with openDogV3 code. Includes functions to smooth out movement, as well as a triangle function to be used
 in the regular walk cycle. Commented out a five second delay in openDogV3 kinematics code. 
 Added:    teensy/standalone_Kinematics
</pre>


 **2023-03-21:**  
 <pre>Updated teensy_serial_main to control a single leg with three axes of the PS4 controller. In mode 1 it will take values
 from the Pi corresponding to x and y on the left joystick and up/down on the dpad, all within range [-1,1], then map those values
 to each joint's range of movement and repeatedly call the openDog kinematics function using the new values. Testing was successful.  
 Updated:    teensy/teensy_serial_main
             pi/pi_serial_main
</pre>

 **2023-03-29:**  
 <pre>Created programs pi_simple_controller and teensy_serial_main_opendog to directly interface the PS4 controller with openDogv3 code.
 Pi_simple_controller improves upon pi_serial_main by switching from pygame to pyPS4Controller and using polling. Every 0.01ms the 
 print_controller_values thread will take the current values in the controller class and print them to the teensy serial port. After every
 message the Teensy will take these values and map them to ranges suitable for openDog walk cycle. This program appears to function correctly.
 We only have two legs working right now, but with two more the robot should be walking. The next step is to implement polling into the original
 controller/serial communication program. 
 Added:      teensy/teensy_serial_main_opendog
             pi/pi_simple_controller
</pre>
