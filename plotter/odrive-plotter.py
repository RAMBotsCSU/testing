import odrive
from odrive.enums import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import threading

# Initialize data storage
times = []
currents = []
start_time = time.time()

# Lock for thread-safe plotting
data_lock = threading.Lock()

# Connect to ODrive
print("Searching for ODrive...")
odrv = odrive.find_any()
print("Connected to ODrive")

def read_current_loop():
    while True:
        current_time = time.time() - start_time
        current = odrv.axis0.motor.current_control.Iq_setpoint  # or Id_measured

        with data_lock:
            times.append(current_time)
            currents.append(current)

            # Keep only the last 10 seconds of data
            while times and (times[-1] - times[0]) > 15:
                times.pop(0)
                currents.pop(0)

        time.sleep(0.05)  # 20 Hz

def exponential_moving_average(data, alpha=0.2):
    if not data:
        return []
    smoothed = [data[0]]
    for point in data[1:]:
        smoothed.append(alpha * point + (1 - alpha) * smoothed[-1])
    return smoothed

def update_plot(frame):
    with data_lock:
        smoothed_currents = exponential_moving_average(currents)
        plt.cla()
        plt.ylim(-20, 20)  # Set the Y-axis limits
        plt.plot(times, smoothed_currents, label="Smoothed Iq_measured (EMA)")
        plt.xlabel("Time (s)")
        plt.ylabel("Current (A)")
        plt.title("Smoothed ODrive Motor Current Over Time")
        plt.grid(True)
        plt.legend(loc="upper right")
        plt.tight_layout()


# Start background thread to read data
thread = threading.Thread(target=read_current_loop, daemon=True)
thread.start()

# Start plot animation
fig = plt.figure()
ani = animation.FuncAnimation(fig, update_plot, interval=100)
plt.show()
