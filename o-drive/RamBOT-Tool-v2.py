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
import odrive.utils
from odrive.device_manager import *
import threading
from odrive.enums import AxisState

# Common ODrive error code mappings
AXIS_ERROR_CODES = {
    0x00: "No Error",
    0x01: "UNDERCURRENT_FAULT",
    0x02: "OVERCURRENT_FAULT",
    0x04: "MOTOR_OVERSPEED_FAULT",
    0x08: "MOTOR_PHASE_RESISTANCE_OUT_OF_RANGE",
    0x10: "MOTOR_PHASE_INDUCTANCE_OUT_OF_RANGE",
    0x20: "ADC_FAILED",
    0x40: "DRV_FAULT",
    0x80: "CONTROL_DEADLINE_MISSED",
    0x100: "NOT_IDLE_FOR_CALIBRATION",
    0x200: "CALIBRATION_TIMEOUT",
    0x400: "MOTOR_FAILED",
}

MOTOR_ERROR_CODES = {
    0x00: "No Error",
    0x01: "PHASE_RESISTANCE_OUT_OF_RANGE",
    0x02: "PHASE_INDUCTANCE_OUT_OF_RANGE",
    0x04: "ADC_FAILED",
    0x08: "DRV_FAULT",
    0x10: "CONTROL_DEADLINE_MISSED",
    0x20: "NOT_CALIBRATED",
    0x40: "ENCODER_ERROR",
}

ENCODER_ERROR_CODES = {
    0x00: "No Error",
    0x01: "UNSTABLE_GAIN",
    0x02: "CPR_OUT_OF_RANGE",
    0x04: "NO_RESPONSE",
    0x08: "TIMEOUT",
    0x10: "HALL_EFFECT_BAD",
    0x20: "INDEX_NOT_FOUND",
    0x40: "ABS_SPI_TIMEOUT",
    0x80: "ABS_SPI_COM_FAIL",
}

CONTROLLER_ERROR_CODES = {
    0x00: "No Error",
    0x01: "OVERSPEED",
    0x02: "INVALID_INPUT_MODE",
    0x04: "UNSTABLE_GAIN",
    0x08: "INVALID_MIRROR_AXIS",
    0x10: "HOMING_INCOMPLETE",
}


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
        # Set callback for GUI connection status updates
        self.odrive_config.update_gui_connection = self.update_connection_status
        
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
    
    def update_connection_status(self, connected):
        """Update GUI connection status indicators"""
        if connected:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: #51cf66;")
            self.connect_btn.setText("Reconnect")
            self.calibrate_btn.setEnabled(True)
        else:
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("color: #ff6b6b;")
            self.connect_btn.setText("Connect to ODrive")
            self.calibrate_btn.setEnabled(False)
        QApplication.processEvents()  # Force UI update
    
    def connect_odrive(self):
        """Manually connect to ODrive"""
        self.update_status("Connecting to ODrive...")
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Connecting...")
        QApplication.processEvents()
        
        try:
            if self.odrive_config.find_odrive():
                self.update_connection_status(True)
                self.update_status("ODrive connected successfully")
            else:
                self.update_connection_status(False)
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
        self.subscription = None
        self.device_manager = get_device_manager()
        self._is_connected = False
    
    def set_feedback_callback(self, callback):
        """Set callback function for sending status updates to GUI"""
        self.feedback_callback = callback
    
    def send_feedback(self, message):
        """Send feedback message to GUI if callback is set"""
        if self.feedback_callback:
            self.feedback_callback(message)
        else:
            print(message)
    
    def get_error_name(self, error_code, error_type="axis"):
        """Get human-readable error name from error code"""
        if error_type == "axis":
            return AXIS_ERROR_CODES.get(error_code, f"Unknown Error Code 0x{error_code:04X}")
        elif error_type == "motor":
            return MOTOR_ERROR_CODES.get(error_code, f"Unknown Error Code 0x{error_code:04X}")
        elif error_type == "encoder":
            return ENCODER_ERROR_CODES.get(error_code, f"Unknown Error Code 0x{error_code:04X}")
        elif error_type == "controller":
            return CONTROLLER_ERROR_CODES.get(error_code, f"Unknown Error Code 0x{error_code:04X}")
        else:
            return f"Unknown Error Code 0x{error_code:04X}"
        
    def calibrate(self):
        """Full calibration sequence - matches calibrate.py with subscription model"""
        # Step 1: Erase configuration
        self.send_feedback("Erasing configuration...")
        try:
            self.odrive.erase_configuration()
        except Exception as e:
            self.send_feedback(f"Erase completed (connection lost as expected)")
        
        # Reconnect after erase
        self.send_feedback("Reconnecting after erase...")
        time.sleep(2)
        if not self.find_odrive():
            self.send_feedback("Failed to reconnect")
            return
        
        # Step 2: Configure GPIO and encoders
        self.send_feedback("Configuring GPIO and encoders...")
        self.configure_spi_encoders()
        
        # Step 3: Set motor parameters
        self.send_feedback("Setting motor parameters...")
        self.define_constants()
        
        # Step 4: Save and reconnect
        self.send_feedback("Saving configuration...")
        try:
            self.odrive.save_configuration()
        except Exception as e:
            self.send_feedback(f"Save completed (connection may be lost temporarily)")
        
        time.sleep(2)
        if not self.find_odrive():
            self.send_feedback("Failed to reconnect")
            return
        
        # Step 5: Clear errors before calibration
        self.odrive.clear_errors()
        time.sleep(0.5)
        
        # Step 6: Calibrate motors and encoders
        self.send_feedback("Calibrating axis0...")
        self.calibrate_axis(self.odrive.axis0, "axis0")
        
        self.send_feedback("Calibrating axis1...")
        self.calibrate_axis(self.odrive.axis1, "axis1")
        
        # Step 7: Clear errors and save
        self.odrive.clear_errors()
        self.send_feedback("Saving final configuration...")
        try:
            self.odrive.save_configuration()
        except Exception as e:
            self.send_feedback(f"Save completed (connection will be lost temporarily)")
        
        # Step 8: Wait for device to reboot and reconnect
        self.send_feedback("Waiting for ODrive to reboot...")
        time.sleep(3)
        
        self.send_feedback("Reconnecting after reboot...")
        if self.find_odrive():
            self.send_feedback("Calibration complete! ODrive reconnected successfully.")
        else:
            self.send_feedback("Calibration complete but failed to reconnect. Click 'Connect to ODrive' to reconnect.")

    def configure_spi_encoders(self):
        """Configure SPI absolute encoders on GPIO pins 7 and 8"""
        # Set GPIO pins to digital mode
        self.odrive.config.gpio7_mode = 0
        self.odrive.config.gpio8_mode = 0
        
        # Configure SPI chip select pins
        self.odrive.axis0.encoder.config.abs_spi_cs_gpio_pin = 7
        self.odrive.axis1.encoder.config.abs_spi_cs_gpio_pin = 8
    
    def define_constants(self):
        """Define motor and encoder constants - matches calibrate.py"""
        for axis in [self.odrive.axis0, self.odrive.axis1]:
            axis.motor.config.pole_pairs = 20
            axis.encoder.config.mode = 257  # SPI mode
            axis.encoder.config.cpr = 16384

    def calibrate_axis(self, axis, axis_name):
        """Calibrate motor and encoder for an axis - matches calibrate.py"""
        time.sleep(1)
        
        # Motor calibration
        self.send_feedback(f"{axis_name}: Starting motor calibration...")
        axis.requested_state = AxisState.MOTOR_CALIBRATION
        time.sleep(1)
        
        # Wait for motor calibration to complete (state returns to IDLE = 1)
        while axis.current_state != 1:
            time.sleep(2)
            self.send_feedback(f"{axis_name}: Motor calibrating...")
        
        axis.motor.config.pre_calibrated = True
        self.send_feedback(f"{axis_name}: Motor calibration complete")
        
        # Encoder calibration
        self.send_feedback(f"{axis_name}: Starting encoder calibration...")
        axis.requested_state = AxisState.ENCODER_OFFSET_CALIBRATION
        time.sleep(1)
        
        # Wait for encoder calibration to complete (state returns to IDLE = 1)
        while axis.current_state != 1:
            time.sleep(2)
            self.send_feedback(f"{axis_name}: Encoder calibrating...")
        
        axis.encoder.config.pre_calibrated = True
        self.send_feedback(f"{axis_name}: Encoder calibration complete")
        
        time.sleep(1)

    def on_found(self, dev):
        """Callback when ODrive device is found"""
        serial = dev.info.serial_number if hasattr(dev, 'info') else 'unknown'
        self.send_feedback(f"Found ODrive (S/N: {serial})")
        return True  # Always connect to found devices
    
    def on_lost(self, dev):
        """Callback when ODrive device is lost"""
        self._is_connected = False
        self.send_feedback("ODrive connection lost - searching...")
    
    def on_connected(self, dev):
        """Callback when connected to ODrive"""
        self._is_connected = True
        self.odrive = dev
        serial = dev.info.serial_number if hasattr(dev, 'info') else 'unknown'
        self.send_feedback(f"Connected to ODrive (S/N: {serial})")
        
        # Update GUI connection status if callback exists
        if hasattr(self, 'update_gui_connection'):
            self.update_gui_connection(True)
    
    def on_disconnected(self, dev):
        """Callback when disconnected from ODrive"""
        self._is_connected = False
        self.odrive = None
        self.send_feedback("ODrive disconnected - will auto-reconnect")
        
        # Update GUI connection status if callback exists
        if hasattr(self, 'update_gui_connection'):
            self.update_gui_connection(False)
    
    def find_odrive(self):
        """Find and connect to ODrive using subscription"""
        try:
            self.send_feedback("Searching for ODrive...")
            
            # Try simple connection first (works better on Windows with driver issues)
            try:
                self.send_feedback("Attempting direct connection...")
                self.odrive = odrive.find_any(timeout=3)
                if self.odrive:
                    self._is_connected = True
                    self.send_feedback("ODrive connected successfully (direct method)")
                    return self.odrive
            except Exception as direct_error:
                self.send_feedback(f"Direct connection failed: {direct_error}")
            
            # Fallback to subscription method
            self.send_feedback("Trying subscription method...")
            
            # Create subscription if not already created
            if self.subscription is None:
                self.subscription = Subscription(
                    debug_name="RamBOT-Tool",
                    on_found=self.on_found,
                    on_lost=self.on_lost,
                    on_connected=self.on_connected,
                    on_disconnected=self.on_disconnected
                )
                self.device_manager.subscribe(self.subscription)
            
            # Wait a moment for connection
            max_wait = 5  # seconds
            start_time = time.time()
            while not self._is_connected and (time.time() - start_time) < max_wait:
                time.sleep(0.1)
            
            if self._is_connected:
                self.send_feedback("ODrive connected successfully")
                return self.odrive
            else:
                self.send_feedback("Connection failed - Check USB connection and drivers")
                self.send_feedback("Windows users: Install WinUSB driver with Zadig")
                return None
                
        except Exception as e:
            self.send_feedback(f"Error finding ODrive: {e}")
            print(f"Error finding ODrive: {e}")
            self.send_feedback("Tip: On Windows, use Zadig to install WinUSB driver")
            return None

    def cleanup(self):
        """Apply final configuration settings (optional - not in calibrate.py)"""
        # This method is kept for backwards compatibility but not used in calibration
        if self.odrive:
            self.odrive.config.enable_brake_resistor = True
            self.odrive.axis0.config.startup_closed_loop_control = True
            self.odrive.axis1.config.startup_closed_loop_control = True
    
    def detach(self):
        """Detach from ODrive without stopping motors"""
        try:
            self.send_feedback("Detaching from ODrive...")
            
            # Unsubscribe from device manager
            if self.subscription:
                try:
                    self.device_manager.unsubscribe(self.subscription)
                    self.subscription = None
                except Exception as e:
                    print(f"Error unsubscribing: {e}")
            
            # Clear ODrive reference
            self.odrive = None
            self._is_connected = False
            self.send_feedback("ODrive detached")
            
        except Exception as e:
            print(f"Error detaching: {e}")
            self.odrive = None
            self._is_connected = False
    
    def get_axis_report(self, axis, axis_name="axis"):
        """Generate detailed diagnostic report for a given axis"""
        report = []
        report.append(f"\n--- {axis_name.upper()} DIAGNOSTIC REPORT ---")
        
        # Read error codes directly
        try:
            axis_error = axis.error
            error_name = self.get_error_name(axis_error, "axis")
            report.append(f"Axis Error: {error_name} (0x{axis_error:04X})")
            if axis_error == 0:
                report.append("  Status: OK")
            else:
                report.append(f"  Status: ERROR")
        except Exception as e:
            report.append(f"Axis Error: Could not read - {e}")
        
        try:
            motor_error = axis.motor.error
            error_name = self.get_error_name(motor_error, "motor")
            report.append(f"\nMotor Error: {error_name} (0x{motor_error:04X})")
            if motor_error == 0:
                report.append("  Status: OK")
            else:
                report.append(f"  Status: ERROR")
        except Exception as e:
            report.append(f"\nMotor Error: Could not read - {e}")
        
        try:
            encoder_error = axis.encoder.error
            error_name = self.get_error_name(encoder_error, "encoder")
            report.append(f"\nEncoder Error: {error_name} (0x{encoder_error:04X})")
            if encoder_error == 0:
                report.append("  Status: OK")
            else:
                report.append(f"  Status: ERROR")
        except Exception as e:
            report.append(f"\nEncoder Error: Could not read - {e}")
        
        try:
            controller_error = axis.controller.error
            error_name = self.get_error_name(controller_error, "controller")
            report.append(f"\nController Error: {error_name} (0x{controller_error:04X})")
            if controller_error == 0:
                report.append("  Status: OK")
            else:
                report.append(f"  Status: ERROR")
        except Exception as e:
            report.append(f"\nController Error: Could not read - {e}")
        
        # Current state
        try:
            current_state = axis.current_state
            state_name = {0: "UNDEFINED", 1: "IDLE", 2: "STARTUP_SEQUENCE", 4: "MOTOR_CALIBRATION", 
                         6: "ENCODER_OFFSET_CALIBRATION", 8: "CLOSED_LOOP_CONTROL"}.get(current_state, f"Unknown ({current_state})")
            report.append(f"\nCurrent State: {state_name}")
        except Exception as e:
            report.append(f"\nCurrent State: Could not read - {e}")
        
        # Motor calibration status
        try:
            is_calibrated = axis.motor.is_calibrated
            report.append(f"Motor Calibrated: {is_calibrated}")
        except Exception as e:
            report.append(f"Motor Calibrated: Could not read - {e}")
        
        # Encoder status
        try:
            is_ready = axis.encoder.is_ready
            report.append(f"Encoder Ready: {is_ready}")
        except Exception as e:
            report.append(f"Encoder Ready: Could not read - {e}")
        
        # Optional: DRV fault
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
        
        # Serial number
        try:
            serial = self.odrive.serial_number if hasattr(self.odrive, 'serial_number') else 'N/A'
            report.append(f"Serial Number: {serial}")
        except Exception as e:
            report.append(f"Serial Number: Could not read - {e}")
        
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
