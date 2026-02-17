"""
    Updated February 2026
    Joey Reback
    PyQt6 Implementation
"""

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                              QTextEdit, QStatusBar, QFrame, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import os
import math
import time
import odrive
from odrive.enums import *
import threading


class RamBOTToolQt(QMainWindow):
    """
        ### RamBOT Tool PyQt6 Class
    """
    def __init__(self):
        super().__init__()
        self.odrive_config = None
        self.plotter_running = False
        self.plot_times = []
        self.plot_currents = []
        self.plot_start_time = time.time()
        self.data_lock = threading.Lock()
        self.setup_main_window()
        
    def set_odrive(self, odrive_config):
        """Set the ODrive configuration object"""
        self.odrive_config = odrive_config
        # Set callback for feedback
        self.odrive_config.set_feedback_callback(self.update_status)
        
    def setup_main_window(self):
        """Main Window Setup"""
        self.setWindowTitle("RamBOT Tool")
        self.setMinimumSize(900, 750)
        
        # Set icon
        try:
            self.setWindowIcon(QIcon("o-drive/logo.png"))
        except:
            pass
        
        # Apply dark theme stylesheet
        self.apply_stylesheet()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create banner label above tabs
        self.banner_label = QLabel()
        self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner_label.setStyleSheet("background-color: #1e1e1e; padding: 10px;")
        
        # Try to load banner image
        try:
            banner_pixmap = QPixmap("o-drive/banner.png")
            if not banner_pixmap.isNull():
                # Scale the image to fit nicely (maintain aspect ratio)
                scaled_pixmap = banner_pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
                self.banner_label.setPixmap(scaled_pixmap)
            else:
                # Fallback if image doesn't exist
                self.banner_label.setText("RamBOT Tool")
                self.banner_label.setStyleSheet("background-color: #1e1e1e; padding: 20px; font-size: 24pt; font-weight: bold; color: #4a90e2;")
        except:
            # Fallback if image loading fails
            self.banner_label.setText("RamBOT Tool")
            self.banner_label.setStyleSheet("background-color: #1e1e1e; padding: 20px; font-size: 24pt; font-weight: bold; color: #4a90e2;")
        
        main_layout.addWidget(self.banner_label)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_calibrate_tab()
        self.create_diagnose_tab()
        self.create_plotter_tab()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
    def apply_stylesheet(self):
        """Apply dark theme stylesheet"""
        stylesheet = """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #e8e8e8;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 9pt;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #e8e8e8;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4a90e2;
            }
            QTabBar::tab:hover {
                background-color: #4d4d4d;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a9ff2;
            }
            QPushButton:pressed {
                background-color: #3a80d2;
            }
            QLabel {
                color: #e8e8e8;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #e8e8e8;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                padding: 5px;
            }
            QStatusBar {
                background-color: #3d3d3d;
                color: #e8e8e8;
                border-top: 1px solid #4d4d4d;
            }
        """
        self.setStyleSheet(stylesheet)
        
    def create_calibrate_tab(self):
        """Create the calibration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Calibrate O-Drive")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Connection status
        self.connection_status = QLabel("Not Connected")
        self.connection_status.setFont(QFont("Segoe UI", 10))
        self.connection_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_status.setStyleSheet("color: #ff6b6b;")
        layout.addWidget(self.connection_status)
        
        # Connect button
        self.connect_btn = QPushButton("Connect to ODrive")
        self.connect_btn.clicked.connect(self.connect_odrive)
        self.connect_btn.setMinimumWidth(200)
        self.connect_btn.setMinimumHeight(40)
        layout.addWidget(self.connect_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Calibrate button
        self.calibrate_btn = QPushButton("Start Calibration")
        self.calibrate_btn.clicked.connect(self.start_calibration)
        self.calibrate_btn.setMinimumWidth(200)
        self.calibrate_btn.setMinimumHeight(40)
        self.calibrate_btn.setEnabled(False)
        layout.addWidget(self.calibrate_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        self.tabs.addTab(tab, "Calibrate")
        
    def create_diagnose_tab(self):
        """Create the diagnostics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Diagnose O-Drive")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Run Diagnostics button
        run_diag_btn = QPushButton("Run Diagnostics")
        run_diag_btn.clicked.connect(self.run_diagnostics)
        run_diag_btn.setMinimumHeight(35)
        button_layout.addWidget(run_diag_btn)
        
        # Clear Errors button
        clear_btn = QPushButton("Clear Errors")
        clear_btn.clicked.connect(self.clear_errors)
        clear_btn.setMinimumHeight(35)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Output label
        output_label = QLabel("Diagnostic Output:")
        output_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(output_label)
        
        # Diagnostic output text area
        self.diag_text = QTextEdit()
        self.diag_text.setReadOnly(True)
        self.diag_text.setMinimumHeight(400)
        layout.addWidget(self.diag_text)
        
        self.tabs.addTab(tab, "Diagnose")
        
    def create_plotter_tab(self):
        """Create the plotter tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Real-Time Current Monitor")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Control panel
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Axis selector
        axis_label = QLabel("Axis:")
        control_layout.addWidget(axis_label)
        
        self.axis_combo = QComboBox()
        self.axis_combo.addItems(["Axis 0", "Axis 1"])
        self.axis_combo.setMinimumWidth(100)
        control_layout.addWidget(self.axis_combo)
        
        # Current type selector
        current_label = QLabel("Current:")
        control_layout.addWidget(current_label)
        
        self.current_combo = QComboBox()
        self.current_combo.addItems(["Iq (Torque)", "Id (Flux)", "Iq Setpoint", "Id Setpoint"])
        self.current_combo.setMinimumWidth(150)
        control_layout.addWidget(self.current_combo)
        
        # Start/Stop button
        self.plot_btn = QPushButton("Start Plotting")
        self.plot_btn.clicked.connect(self.toggle_plotting)
        self.plot_btn.setMinimumHeight(35)
        control_layout.addWidget(self.plot_btn)
        
        layout.addLayout(control_layout)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1e1e1e')
        self.figure.patch.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='#e8e8e8')
        self.ax.spines['bottom'].set_color('#3d3d3d')
        self.ax.spines['top'].set_color('#3d3d3d')
        self.ax.spines['left'].set_color('#3d3d3d')
        self.ax.spines['right'].set_color('#3d3d3d')
        self.ax.grid(True, color='#3d3d3d', linestyle='-', linewidth=0.5)
        
        layout.addWidget(self.canvas)
        
        # Setup timer for plot updates
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.update_plot)
        
        self.tabs.addTab(tab, "Plotter")
        
    def update_status(self, message):
        """Callback method to update status from ODrive operations"""
        self.statusBar.showMessage(message)
        QApplication.processEvents()  # Force UI update
    
    def connect_odrive(self):
        """Manually connect to ODrive"""
        self.update_status("Connecting to ODrive...")
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Connecting...")
        QApplication.processEvents()
        
        try:
            if self.odrive_config.find_odrive():
                self.connection_status.setText("Connected")
                self.connection_status.setStyleSheet("color: #51cf66;")
                self.connect_btn.setText("Reconnect")
                self.calibrate_btn.setEnabled(True)
                self.update_status("ODrive connected successfully")
            else:
                self.connection_status.setText("Connection Failed")
                self.connection_status.setStyleSheet("color: #ff6b6b;")
                self.connect_btn.setText("Retry Connection")
                self.calibrate_btn.setEnabled(False)
                self.update_status("Failed to connect to ODrive")
        except Exception as e:
            self.connection_status.setText("Connection Error")
            self.connection_status.setStyleSheet("color: #ff6b6b;")
            self.connect_btn.setText("Retry Connection")
            self.calibrate_btn.setEnabled(False)
            self.update_status(f"Error: {e}")
        finally:
            self.connect_btn.setEnabled(True)
        
    def start_calibration(self):
        """Start calibration process"""
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
                self.diag_text.setPlainText(report)
                self.update_status("Diagnostics complete")
            except Exception as e:
                self.update_status(f"Diagnostics failed: {e}")
                self.diag_text.setPlainText(f"Error running diagnostics:\n{e}")
        else:
            self.update_status("Error: ODrive not connected")
            self.diag_text.setPlainText("ODrive not connected. Cannot run diagnostics.")
            
    def clear_errors(self):
        """Clear ODrive errors"""
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
    
    def toggle_plotting(self):
        """Start or stop plotting"""
        if not self.odrive_config or not self.odrive_config.odrive:
            self.update_status("Error: ODrive not connected")
            return
            
        if self.plotter_running:
            # Stop plotting
            self.plotter_running = False
            self.plot_timer.stop()
            self.plot_btn.setText("Start Plotting")
            self.update_status("Plotting stopped")
        else:
            # Start plotting
            self.plotter_running = True
            self.plot_start_time = time.time()
            with self.data_lock:
                self.plot_times.clear()
                self.plot_currents.clear()
            
            # Start data collection thread
            self.data_thread = threading.Thread(target=self.read_current_loop, daemon=True)
            self.data_thread.start()
            
            # Start plot update timer (100ms = 10 FPS)
            self.plot_timer.start(100)
            self.plot_btn.setText("Stop Plotting")
            self.update_status("Plotting started")
    
    def read_current_loop(self):
        """Background thread to read current data"""
        while self.plotter_running:
            try:
                current_time = time.time() - self.plot_start_time
                
                # Get selected axis
                axis_idx = self.axis_combo.currentIndex()
                axis = self.odrive_config.odrive.axis0 if axis_idx == 0 else self.odrive_config.odrive.axis1
                
                # Get selected current type
                current_type = self.current_combo.currentIndex()
                if current_type == 0:  # Iq measured
                    current = axis.motor.current_control.Iq_measured
                elif current_type == 1:  # Id measured
                    current = axis.motor.current_control.Id_measured
                elif current_type == 2:  # Iq setpoint
                    current = axis.motor.current_control.Iq_setpoint
                else:  # Id setpoint
                    current = axis.motor.current_control.Id_setpoint
                
                with self.data_lock:
                    self.plot_times.append(current_time)
                    self.plot_currents.append(current)
                    
                    # Keep only last 15 seconds
                    while self.plot_times and (self.plot_times[-1] - self.plot_times[0]) > 15:
                        self.plot_times.pop(0)
                        self.plot_currents.pop(0)
                
                time.sleep(0.05)  # 20 Hz sampling
            except Exception as e:
                print(f"Error reading current: {e}")
                time.sleep(0.1)
    
    def exponential_moving_average(self, data, alpha=0.2):
        """Smooth data using exponential moving average"""
        if not data:
            return []
        smoothed = [data[0]]
        for point in data[1:]:
            smoothed.append(alpha * point + (1 - alpha) * smoothed[-1])
        return smoothed
    
    def update_plot(self):
        """Update the plot with new data"""
        with self.data_lock:
            if not self.plot_times:
                return
            
            times_copy = self.plot_times.copy()
            currents_copy = self.plot_currents.copy()
        
        # Apply smoothing
        smoothed = self.exponential_moving_average(currents_copy)
        
        # Update plot
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')
        self.ax.plot(times_copy, smoothed, color='#2e6d00', linewidth=2, label='Current (A)')
        self.ax.set_xlabel('Time (s)', color='#e8e8e8')
        self.ax.set_ylabel('Current (A)', color='#e8e8e8')
        
        # Get current type name
        current_name = self.current_combo.currentText()
        axis_name = self.axis_combo.currentText()
        self.ax.set_title(f'{axis_name} - {current_name}', color='#e8e8e8')
        
        self.ax.set_ylim(-40, 40)
        self.ax.grid(True, color='#3d3d3d', linestyle='-', linewidth=0.5)
        self.ax.tick_params(colors='#e8e8e8')
        self.ax.spines['bottom'].set_color('#3d3d3d')
        self.ax.spines['top'].set_color('#3d3d3d')
        self.ax.spines['left'].set_color('#3d3d3d')
        self.ax.spines['right'].set_color('#3d3d3d')
        self.ax.legend(loc='upper right', facecolor='#2b2b2b', edgecolor='#3d3d3d', labelcolor='#e8e8e8')
        
        self.figure.tight_layout()
        self.canvas.draw()
            
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Stop plotting if running
            if self.plotter_running:
                self.plotter_running = False
                self.plot_timer.stop()
            
            if self.odrive_config:
                self.odrive_config.detach()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        event.accept()


class Config_ODrive:
    """ODrive Configuration and Control Class"""
    
    def __init__(self):
        self.odrive = None
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
        """Set axis and component references"""
        self.ax0 = self.odrive.axis0
        self.ax1 = self.odrive.axis1
        self.mo0 = self.ax0.motor
        self.mo1 = self.ax1.motor
        self.enc0 = self.ax0.encoder
        self.enc1 = self.ax1.encoder
        self.contr0 = self.ax0.controller
        self.contr1 = self.ax1.controller
    
    def define_constants(self):
        """Define motor and controller constants"""
        self.mo0.config.current_lim = 22.0
        self.mo1.config.current_lim = 22.0
        self.mo0.config.current_lim_margin = 9.0
        self.mo1.config.current_lim_margin = 9.0
        self.enc0.config.cpr = 16384                         
        self.enc1.config.cpr = 16384
        self.mo0.config.pole_pairs = 20
        self.mo1.config.pole_pairs = 20
        self.mo0.config.torque_constant = 0.092
        self.mo1.config.torque_constant = 0.092
        self.contr0.config.pos_gain = 60
        self.contr1.config.pos_gain = 60
        self.contr0.config.vel_gain = 0.1
        self.contr1.config.vel_gain = 0.1
        self.contr0.config.vel_integrator_gain = 0.2
        self.contr1.config.vel_integrator_gain = 0.2
        self.contr0.config.vel_limit = math.inf
        self.contr1.config.vel_limit = math.inf

    def calibrate_motor(self, axis):
        """Calibrate a motor"""
        self.send_feedback(f"Calibrating motor on {axis}...")
        axis.requested_state = 4
        while not axis.motor.is_calibrated:
            pass
        axis.motor.config.pre_calibrated = True
        self.send_feedback(f"Motor {axis} calibrated")

    def calibrate_encoders(self, axis):
        """Calibrate an encoder"""
        self.send_feedback(f"Calibrating encoder on {axis}...")
        axis.requested_state = 6
        while not axis.encoder.is_ready:
            pass
        axis.encoder.config.pre_calibrated = True
        self.send_feedback(f"Encoder {axis} calibrated")

    def find_odrive(self):
        """Find and connect to ODrive"""
        try:
            self.send_feedback("Searching for ODrive...")
            odrv = odrive.find_any()
            self.send_feedback("ODrive found and connected")
            self.odrive = odrv
            return odrv
        except Exception as e:
            self.send_feedback(f"Error finding ODrive: {e}")
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
        """Convert bitfield error values into human-readable names"""
        if error_value == 0:
            return ["no error"]
        errors = []
        for name, value in error_dict.items():
            if error_value & value:
                errors.append(name)
        return errors
    
    def get_axis_report(self, axis, axis_name="axis"):
        """Generate detailed diagnostic report for a given axis"""
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
        """Run complete diagnostic check and return formatted report"""
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
        """Clear all ODrive errors"""
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
        """Save configuration and reboot ODrive"""
        try:
            self.odrive.save_configuration()
            self.odrive.reboot()
        except Exception as e:
            print(f"Error saving configuration: {e}")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application-wide font for better rendering
    app.setFont(QFont("Segoe UI", 9))
    
    window = RamBOTToolQt()
    window.show()
    
    # Create ODrive config but don't auto-connect
    odrive_config = Config_ODrive()
    window.set_odrive(odrive_config)
    
    window.update_status("Ready - Click 'Connect to ODrive' to begin")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
