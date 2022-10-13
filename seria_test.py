#********************************************************
#* Simple teensy communication script                   *
#* Communicate back and forth with the Teensy           *
#********************************************************

import serial

ser = serial.Serial('/dev/ttyACM0',9600, timeout = 1)
s = [0,1]
while True:
	read_serial=ser.readline()
	s[0] = str(ser.readline())
	print (s[0])
	print (str(read_serial))
	write_serial=ser.write('hello'.encode('utf-8'))




#	read_serial=ser.readline()
#	s[0] = str(int (ser.readline(),16))
#	print (s[0])
#	print (str(int(read_serial,16)))
#	write_serial=ser.write('hello'.encode('utf-8'))
