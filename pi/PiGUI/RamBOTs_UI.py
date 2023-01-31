import PySimpleGUI as sg    

sg.theme('DarkGreen2')

tab1_layout = [[sg.T('Movement Array                                                                                                                                                                      ')],
               [sg.Table([['Strafe','x1'], ['Forback','x1'], ['Roll','x1'], ['Turn','x1'], ['Pitch','x1'], ['Height','x1'], ['Yaw','x1'], ['           ','           ']], ['Parameter','Value'], num_rows=8)],
               [sg.Image('./Resources/RamBOTs_Logo_Small.png')],
               [sg.Submit(), sg.Cancel()]]

tab2_layout =  [[sg.T('This is inside tab 2')],[sg.Text('Machine Learning Command Line Parameters', font=('Helvetica', 16))],      
              [sg.Text('Passes', size=(15, 1)), sg.Spin(values=[i for i in range(1, 1000)], initial_value=20, size=(6, 1)),      
               sg.Text('Steps', size=(18, 1)), sg.Spin(values=[i for i in range(1, 1000)], initial_value=20, size=(6, 1))],      
              [sg.Text('ooa', size=(15, 1)), sg.In(default_text='6', size=(10, 1)), sg.Text('nn', size=(15, 1)),      
               sg.In(default_text='10', size=(10, 1))],      
              [sg.Text('q', size=(15, 1)), sg.In(default_text='ff', size=(10, 1)), sg.Text('ngram', size=(15, 1)),      
               sg.In(default_text='5', size=(10, 1))],      
              [sg.Text('l', size=(15, 1)), sg.In(default_text='0.4', size=(10, 1)), sg.Text('Layers', size=(15, 1)),      
               sg.Drop(values=('BatchNorm', 'other'), auto_size_text=True)],      
              [sg.Text('_'  * 100, size=(65, 1))],      
              [sg.Text('Flags', font=('Helvetica', 15), justification='left')],      
              [sg.Checkbox('Normalize', size=(12, 1), default=True), sg.Checkbox('Verbose', size=(20, 1))],      
              [sg.Checkbox('Cluster', size=(12, 1)), sg.Checkbox('Flush Output', size=(20, 1), default=True)],      
              [sg.Checkbox('Write Results', size=(12, 1)), sg.Checkbox('Keep Intermediate Data', size=(20, 1))],      
              [sg.Text('_'  * 100, size=(65, 1))],      
              [sg.Text('Loss Functions', font=('Helvetica', 15), justification='left')],      
              [sg.Radio('Cross-Entropy', 'loss', size=(12, 1)), sg.Radio('Logistic', 'loss', default=True, size=(12, 1))],      
              [sg.Radio('Hinge', 'loss', size=(12, 1)), sg.Radio('Huber', 'loss', size=(12, 1))],      
              [sg.Radio('Kullerback', 'loss', size=(12, 1)), sg.Radio('MAE(L1)', 'loss', size=(12, 1))],      
              [sg.Radio('MSE(L2)', 'loss', size=(12, 1)), sg.Radio('MB(L0)', 'loss', size=(12, 1))],      
              [sg.Submit(), sg.Cancel()]]    



tab3_layout = [[sg.T('Based on OpenDogV3 by James Bruton')],
               [sg.T('MIT License')],
               [sg.T('Copyright (c) 2021 James Bruton')],
               [sg.Image('./Resources/RamBOTs_Logo_Small.png')],
               [sg.Submit(), sg.Cancel()]]  

layout = [[sg.TabGroup([[sg.Tab('Feed', tab1_layout, tooltip='tip'), sg.Tab('Settings', tab2_layout, tooltip='TIP3'), sg.Tab('Info', tab3_layout)]], tooltip='TIP2')],    
          [sg.Button('Read')]]    

window = sg.Window('RamBOTs', layout, size=(800,420))    

while True:    
    event, values = window.read()    
    print(event,values)    
    if event == sg.WIN_CLOSED:           # way out of UI    
        break 
