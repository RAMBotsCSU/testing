import PySimpleGUI as sg

sg.theme('DarkGreen2')

table = None

# Slider settings
slider_min = 0
slider_max = 100
slider_default = 50
slider_step = 1

tab1_layout = [
    [
        sg.Column([[sg.T('MOVEMENT ARRAY', font=("Helvetica", 14))]]),
        sg.Column([[sg.T('                            ', font=("Helvetica", 14))]]),
        sg.Column([[sg.Text("MODE 1: WALKING", font=("Helvetica", 14), key='-MODE_TEXT-', pad=(0, 0))]])
    ],
    [
        sg.Table(
            values=[['Left Stick', 'Loading GUI'], ['Left Trigger', 'Please wait!'], ['Right Stick', ' 	⊂(◉‿◉)つ            '], ['Right Trigger', ''],['Mode', ''],
                    ['Dpad Array', ''], ['Shape Button Array', ''], ['Misc Button Array', ''], ['           ', '           ']],
            headings=['Parameter', 'Value'],
            key='-TABLE-',
            num_rows=9,
            hide_vertical_scroll=True,
            pad=(0, 0)
        ),
        sg.Column([
            [sg.Slider(range=(slider_min, slider_max), default_value=slider_default, orientation='h', size=(40, 20), key='-SLIDER-', resolution=slider_step, pad=(0, 0))],
            [sg.Text('Volume', justification='center', pad=(0, 0))]
        ])
    ],
    [sg.Image('./Resources/RamBOTs_Logo_Small.png')],
]

layout = [tab1_layout]

window = sg.Window('RamBOTs', layout, size=(800, 420))

# Initial slider value
previous_slider_value = slider_default

# Event loop
while True:
    event, values = window.read(timeout=100)

    if event == sg.WIN_CLOSED:
        break

    # Check for slider value updates
    current_slider_value = values['-SLIDER-']
    if current_slider_value != previous_slider_value:
        print('Slider value:', current_slider_value)
        previous_slider_value = current_slider_value

        # You can now use 'current_slider_value' variable in your program
        # Add your code here

window.close()
