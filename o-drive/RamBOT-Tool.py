import tkinter as tk
from tkinter import ttk, Menu, PhotoImage, scrolledtext
import csv, re, math
import odrive
from odrive.enums import *
import time
import sys
import os

class RamBOTTool:
    '''
        ### RamBOT Tool Class
    '''
    def __init__(self):
        self.root = tk.Tk()
        self.odrive_config = None
        self.setup_main_window()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def set_odrive(self, odrive_config):
        self.odrive_config = odrive_config
        # Set callback for feedback
        self.odrive_config.set_feedback_callback(self.update_status)

    def setup_main_window(self):
        '''
            ### Main Window Setup
            Main menu definitions
        '''
        self.root.title("RamBOT Tool")
        self.root.option_add('*tearOff', False)
        
        # Configure colors and styling
        self.bg_color = "#2b2b2b"  # Dark background
        self.fg_color = "#e8e8e8"  # Light text
        self.accent_color = "#4a90e2"  # Accent blue
        
        self.root.configure(bg=self.bg_color)
        
        # Configure ttk styling
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for better customization
        
        # Configure styles
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color, font=('Helvetica', 9))
        style.configure('TButton', font=('Helvetica', 9))
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', font=('Helvetica', 9), padding=[10, 5])
        
        # Configure font rendering for better anti-aliasing
        self.default_font = ('Helvetica', 9)
        self.heading_font = ('Helvetica', 14, 'bold')
        self.mono_font = ('Consolas', 9)

        # Set icon
        self.icon = PhotoImage(file="o-drive/logo.png")
        self.root.iconphoto(True, self.icon)

        # Configure root window grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.create_tab_view()
        self.create_calibrate_tab()
        self.create_diagnose_tab()
        self.create_status_bar()

    # Menu Bar
    def create_menu(self):
        menubar = Menu(self.root)
        file_menu = Menu(menubar, tearoff=0)
        help_menu = Menu(menubar, tearoff=0)

        menubar.add_cascade(menu=file_menu, label="File")
        menubar.add_cascade(menu=help_menu, label="Help")
        self.root.config(menu=menubar)

    def create_tab_view(self):
        self.tabControl = ttk.Notebook(self.root)
        self.tabControl.grid(column=0, row=0, sticky="nsew")

        self.tab1 = ttk.Frame(self.tabControl)
        self.tab2 = ttk.Frame(self.tabControl)

        self.tabControl.add(self.tab1, text='Calibrate')
        self.tabControl.add(self.tab2, text='Diagnose')

        # Configure tab grids
        self.tab1.columnconfigure(0, weight=1)
        self.tab2.columnconfigure(0, weight=1)
    
    def create_calibrate_tab(self):
        ttk.Label(self.tab1, text="Calibrate O-Drive", font=self.heading_font).grid(column=0, row=0, padx=30, pady=(30,10))
        
        calibrate_btn = ttk.Button(self.tab1, text='Start Calibration', command=self.start_calibration)
        calibrate_btn.grid(column=0, row=1, padx=30, pady=10)
            
    def create_diagnose_tab(self):
        ttk.Label(self.tab2, text="Diagnose O-Drive", font=self.heading_font).grid(column=0, row=0, padx=30, pady=(30,10), columnspan=2)
        
        # Button frame
        button_frame = ttk.Frame(self.tab2)
        button_frame.grid(column=0, row=1, padx=30, pady=10, columnspan=2)
        
        run_diag_btn = ttk.Button(button_frame, text='Run Diagnostics', command=self.run_diagnostics)
        run_diag_btn.pack(side=tk.LEFT, padx=5)
        
        clear_errors_btn = ttk.Button(button_frame, text='Clear Errors', command=self.clear_errors)
        clear_errors_btn.pack(side=tk.LEFT, padx=5)
        
        # Diagnostic output text area
        ttk.Label(self.tab2, text="Diagnostic Output:", font=self.default_font).grid(column=0, row=2, padx=30, pady=(10,5), sticky='w', columnspan=2)
        
        self.diag_text = scrolledtext.ScrolledText(self.tab2, height=20, width=70, wrap=tk.WORD, 
                                                   bg="#1e1e1e", fg=self.fg_color, 
                                                   font=self.mono_font, insertbackground=self.fg_color)
        self.diag_text.grid(column=0, row=3, padx=30, pady=(0,20), columnspan=2, sticky='nsew')
        self.diag_text.config(state=tk.DISABLED)
        
        # Configure tab grid weights for expansion
        self.tab2.rowconfigure(3, weight=1)
        self.tab2.columnconfigure(0, weight=1)
    
    def create_status_bar(self):
        # Status bar at bottom of window
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(column=0, row=1, sticky="ew", padx=5, pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN, 
                                      anchor=tk.W, font=self.default_font)
        self.status_label.pack(fill=tk.X)
        
        # Adjust root grid to accommodate status bar
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
    
    def update_status(self, message):
        """Callback method to update status from ODrive operations"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_calibration(self):
        if self.odrive_config:
            self.update_status("Starting calibration...")
            try:
                self.odrive_config.calibrate()
                self.update_status("Calibration complete!")
            except Exception as e:
                self.update_status(f"Calibration failed: {e}")
        else:
            self.update_status("Error: ODrive not connected")
    
    def run_diagnostics(self):
        """Run full diagnostic report and display in text area"""
        if self.odrive_config:
            self.update_status("Running diagnostics...")
            try:
                report = self.odrive_config.run_diagnostics()
                self.diag_text.config(state=tk.NORMAL)
                self.diag_text.delete(1.0, tk.END)
                self.diag_text.insert(1.0, report)
                self.diag_text.config(state=tk.DISABLED)
                self.update_status("Diagnostics complete")
            except Exception as e:
                self.update_status(f"Diagnostics failed: {e}")
                self.diag_text.config(state=tk.NORMAL)
                self.diag_text.delete(1.0, tk.END)
                self.diag_text.insert(1.0, f"Error running diagnostics:\n{e}")
                self.diag_text.config(state=tk.DISABLED)
        else:
            self.update_status("Error: ODrive not connected")
            self.diag_text.config(state=tk.NORMAL)
            self.diag_text.delete(1.0, tk.END)
            self.diag_text.insert(1.0, "ODrive not connected. Cannot run diagnostics.")
            self.diag_text.config(state=tk.DISABLED)
    
    def clear_errors(self):
        if self.odrive_config:
            self.update_status("Clearing errors...")
            try:
                self.odrive_config.clear_errors()
                self.update_status("Errors cleared")
                # Re-run diagnostics after clearing
                self.run_diagnostics()
            except Exception as e:
                self.update_status(f"Clear errors failed: {e}")
        else:
            self.update_status("Error: ODrive not connected")
    
    def on_closing(self):
        """Clean shutdown when window is closed"""
        try:
            if self.odrive_config:
                self.odrive_config.detach()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            # Force exit to prevent hanging
            os._exit(0)

class Config_ODrive:
    def __init__(self):
        self.odrive = self.find_odrive()
        self.feedback_callback = None
    
    def set_feedback_callback(self, callback):
        """Set callback function for sending status updates to GUI"""
        self.feedback_callback = callback
    
    def send_feedback(self, message):
        """Send feedback message to GUI if callback is set"""
        if self.feedback_callback:
            self.feedback_callback(message)
        else:
            print(message)
        
    def calibrate(self):
        """Full calibration sequence"""
        self.send_feedback("Setting constants...")
        self.set_constants()
        self.define_constants()
        
        self.send_feedback("Calibrating motors...")
        self.calibrate_motor(self.ax0)
        self.calibrate_motor(self.ax1)
        
        self.send_feedback("Calibrating encoders...")
        self.calibrate_encoders(self.ax0)
        self.calibrate_encoders(self.ax1)
        
        self.send_feedback("Applying configuration...")
        self.cleanup()
        self.save_and_reboot()
        
        self.send_feedback("Calibration complete!")

    def set_constants(self):
        self.ax0 = self.odrive.axis0
        self.ax1 = self.odrive.axis1
        self.mo0 = self.ax0.motor
        self.mo1 = self.ax1.motor
        self.enc0 = self.ax0.encoder
        self.enc1 = self.ax1.encoder
        self.contr0 = self.ax0.controller
        self.contr1 = self.ax1.controller
    
    def define_constants(self):
        self.mo0.config.current_lim = 22.0
        self.mo1.config.current_lim = 22.0
        self.mo0.config.current_lim_margin = 9.0
        self.mo1.config.current_lim_margin = 9.0
        self.enc0.config.cpr = 16384                         
        self.enc1.config.cpr = 16384                         #Has different value in SPI
        self.mo0.config.pole_pairs = 20
        self.mo1.config.pole_pairs = 20
        self.mo0.config.torque_constant =  0.092  # 8.27/90  
        self.mo1.config.torque_constant = 0.092 # 8.27/90
        self.contr0.config.pos_gain = 60
        self.contr1.config.pos_gain = 60
        self.contr0.config.vel_gain = 0.1
        self.contr1.config.vel_gain = 0.1
        self.contr0.config.vel_integrator_gain = 0.2
        self.contr1.config.vel_integrator_gain = 0.2
        self.contr0.config.vel_limit = math.inf              #500 without resistors
        self.contr1.config.vel_limit = math.inf   

    def calibrate_motor(self, axis):
        self.send_feedback(f"Calibrating motor on {axis}...")
        axis.requested_state = 4
        while(not(axis.motor.is_calibrated)):
            pass
        axis.motor.config.pre_calibrated = True
        self.send_feedback(f"Motor {axis} calibrated")

    def calibrate_encoders(self, axis):
        self.send_feedback(f"Calibrating encoder on {axis}...")
        axis.requested_state = 6
        while(not(axis.encoder.is_ready)):
            pass
        axis.encoder.config.pre_calibrated = True
        self.send_feedback(f"Encoder {axis} calibrated")

    def find_odrive(self):
        try:
            odrv = odrive.find_any()
            print("ODrive found.")
            return odrv
        except Exception as e:
            print(f"Error finding ODrive: {e}")
            return None

    def cleanup(self):
        """Apply final configuration settings"""
        if self.odrive:
            self.odrive.config.enable_brake_resistor = True
            self.ax0.config.startup_closed_loop_control = True
            self.ax1.config.startup_closed_loop_control = True
    
    def detach(self):
        """Detach from ODrive without stopping motors"""
        if self.odrive:
            try:
                self.send_feedback("Detaching from ODrive...")
                # Properly release the ODrive connection
                if hasattr(self.odrive, '__channel__'):
                    self.odrive.__channel__.close()
                self.odrive = None
                self.send_feedback("ODrive detached")
            except Exception as e:
                print(f"Error detaching: {e}")
                self.odrive = None

    def decode_errors(self, error_value, error_dict):
        """Convert bitfield error values into human-readable names."""
        if error_value == 0:
            return ["no error"]
        errors = []
        for name, value in error_dict.items():
            if error_value & value:
                errors.append(name)
        return errors
    
    def get_axis_report(self, axis, axis_name="axis"):
        """Generate detailed diagnostic report for a given axis."""
        report = []
        report.append(f"\n--- {axis_name.upper()} DIAGNOSTIC REPORT ---")
        
        try:
            axis_errors = self.decode_errors(axis.error, AXIS_ERROR)
            report.append(f"Axis Error(s): {', '.join(axis_errors)}")
        except Exception as e:
            report.append(f"Axis Error: Could not read - {e}")
        
        try:
            motor_errors = self.decode_errors(axis.motor.error, MOTOR_ERROR)
            report.append(f"Motor Error(s): {', '.join(motor_errors)}")
        except Exception as e:
            report.append(f"Motor Error: Could not read - {e}")
        
        try:
            encoder_errors = self.decode_errors(axis.encoder.error, ENCODER_ERROR)
            report.append(f"Encoder Error(s): {', '.join(encoder_errors)}")
        except Exception as e:
            report.append(f"Encoder Error: Could not read - {e}")
        
        try:
            controller_errors = self.decode_errors(axis.controller.error, CONTROLLER_ERROR)
            report.append(f"Controller Error(s): {', '.join(controller_errors)}")
        except Exception as e:
            report.append(f"Controller Error: Could not read - {e}")
        
        # Optional subcomponents
        if hasattr(axis, "sensorless_estimator"):
            try:
                report.append(f"Sensorless Estimator Error: {axis.sensorless_estimator.error}")
            except:
                pass
        
        if hasattr(axis.motor, "drv_fault"):
            try:
                drv = axis.motor.drv_fault
                report.append(f"DRV Fault: {drv if drv else 'none'}")
            except:
                pass
        
        return "\n".join(report)
    
    def run_diagnostics(self):
        """Run complete diagnostic check and return formatted report."""
        if not self.odrive:
            return "ERROR: ODrive not connected"
        
        self.send_feedback("Running diagnostics...")
        report = []
        report.append("=" * 60)
        report.append("ODrive Diagnostic Report")
        report.append("=" * 60)
        
        # Firmware version
        try:
            fw_version = f"{self.odrive.fw_version_major}.{self.odrive.fw_version_minor}.{self.odrive.fw_version_revision}"
            report.append(f"Firmware Version: {fw_version}")
        except Exception as e:
            report.append(f"Firmware Version: Could not read - {e}")
        
        # System error
        try:
            report.append(f"System Error: {self.odrive.system_stats.error}")
        except Exception as e:
            report.append(f"System Error: Could not read - {e}")
        
        # Voltage
        try:
            report.append(f"Bus Voltage: {self.odrive.vbus_voltage:.2f}V")
        except Exception as e:
            report.append(f"Bus Voltage: Could not read - {e}")
        
        # Axis 0 report
        try:
            report.append(self.get_axis_report(self.odrive.axis0, "axis0"))
        except Exception as e:
            report.append(f"\nERROR reading axis0: {e}")
        
        # Axis 1 report
        try:
            report.append(self.get_axis_report(self.odrive.axis1, "axis1"))
        except AttributeError:
            report.append("\nNo axis1 detected on this ODrive.")
        except Exception as e:
            report.append(f"\nERROR reading axis1: {e}")
        
        report.append("\n" + "=" * 60)
        report.append("Diagnostic Complete")
        report.append("=" * 60)
        
        self.send_feedback("Diagnostics complete")
        return "\n".join(report)
    
    def clear_errors(self):
        if self.odrive:
            self.send_feedback("Clearing ODrive errors...")
            try:
                self.odrive.axis0.clear_errors()
                time.sleep(0.1)
                if hasattr(self.odrive, 'axis1'):
                    self.odrive.axis1.clear_errors()
                    time.sleep(0.1)
                self.odrive.clear_errors()
                self.send_feedback("Errors cleared")
            except Exception as e:
                self.send_feedback(f"Error clearing: {e}")
                raise

    def apply_configuration(self):
        """Apply configuration without full calibration"""
        self.send_feedback("Applying configuration...")
        self.define_constants()
        self.send_feedback("Configuration applied")

    def save_and_reboot(self):
        try:
            self.odrive.save_configuration()
            self.odrive.reboot()
        except Exception as e:
            print(f"Error saving configuration: {e}")

# Run File
if __name__ == "__main__":
    app = RamBOTTool()
    app.set_odrive(Config_ODrive())