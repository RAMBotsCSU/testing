# RamBOTs Locomotion Repo
                   
This is the official CSU RAMBots locomotion repository. 
Visit us at our [website](https://projects-web.engr.colostate.edu/ece-sr-design/AY22/RamBOTs).


<img src="https://user-images.githubusercontent.com/112744753/196563382-2745e707-77d6-42d5-98a0-a29530e21c9a.png" width=50% height=50%>

Files:
------

| File        | Description           |
| ------------- |-------------|
| README      | this file |
| todo        |       |


  
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
           mult_Ser_PS4_Exit_Exit.py
</pre>


 **2022-10-24:**  
 <pre>Added code for the Teensy. Reorganized directory with subfolders for Pi and Teensy code
 Pushed:   serial_test.ino
</pre>
