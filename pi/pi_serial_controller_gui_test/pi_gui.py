import PySimpleGUI as sg    

sg.theme('DarkGreen2')

x1 = "hello"

tab1_layout = [
    [
        sg.Column([[sg.T('MOVEMENT ARRAY', font=("Helvetica", 14))]]),
        sg.Column([[sg.T('                            ', font=("Helvetica", 14))]]),
        sg.Column([[sg.Text("MODE 1: WALKING", font=("Helvetica", 14), key='-MODE_TEXT-', pad=(0, 0))]])
    ],
    [sg.Table(
        values=[['Left Stick', '(0.00,0.00)'], ['Left Trigger', '0.00'], ['Right Stick', '(0.00,0.00)'], ['Right Trigger', '0.00'],
                ['Dpad Array', '↑:0  ↓:0  ←:0  →:0'], ['Shape Button Array', '□:0  △:0  ○:0  X:0'], ['Misc Button Array', 'x1'], ['           ', '           ']],
        headings=['Parameter', 'Value'],
        key='-TABLE-',
        num_rows=8
    )],
    [sg.Image('./Resources/RamBOTs_Logo_Small.png')],
    [sg.Submit(), sg.Cancel()]
]

layout = [tab1_layout]    
          
window = sg.Window('RamBOTs', layout, size=(800, 420))    

def update_table_cell(table, row, col, value):
    table.Widget.set(table.Widget.get_children()[row], "#" + str(col + 1), value)

def start_gui():

    while True:    
        event, values = window.read()    
        print(event, values)    
        if event == sg.WIN_CLOSED:           # way out of UI    
            break
        elif event == 'Submit':
            # Update the value in the second row, second column
            table = window['-TABLE-']
            update_table_cell(table, 0, 1, "(1.00,0.00)")
            update_table_cell(table, 1, 1, "(xxx)")


start_gui()
