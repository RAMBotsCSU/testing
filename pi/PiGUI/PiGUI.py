import PySimpleGUI as sg
import os
from PIL import Image, ImageTk

filename="/home/pi/Desktop/RAMBots_Git/testing/pi/PiGUI/Resources/RamBOTs_Logo.png"
size = (100,100)
im = Image.open(filename)
im = im.resize(size, resample=Image.BICUBIC)

sg.theme('DarkGreen2')

layout = [[sg.Text("Hello from RamBOTs")], [sg.Button("CLOSE")], [sg.Image(key="-IMAGE-")],
          [sg.Text('Some text on Row 1')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]
#330,178 is size with small white borders
#331,179 is size without small borders, but not the whole frame
window = sg.Window("RamBOTs GUI", layout, margins=(331,179), finalize=True)

image = ImageTk.PhotoImage(image=im)

window["-IMAGE-"].update(data=image)
#print(os.path())
while True:
	event, values = window.read()
	if event == "CLOSE" or event == sg.WIN_CLOSED:
		break
	print('You entered ', values[0])

window.close()
