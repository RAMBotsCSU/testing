import serial

ser = serial.Serial('/dev/ttyACM0',9600)#, timeout = 2)
s = [0,1]
i = 0

while i < 1000:
    print("waiting for response ", i)
    #read_serial=ser.readline()
    #s[0] = str(ser.readline())
    # print (s[0])
    print (str( ser.readline() ))
    #write_serial=ser.write('h'.encode('utf-8'))
    i = i + 1




#	read_serial=ser.readline()
#	s[0] = str(int (ser.readline(),16))
#	print (s[0])
#	print (str(int(read_serial,16)))
#	write_serial=ser.write('hello'.encode('utf-8'))

