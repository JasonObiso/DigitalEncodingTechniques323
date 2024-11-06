import subprocess
import sys
import importlib.util

def check_and_install(package_name):
    if importlib.util.find_spec(package_name) is None:
        print(f"{package_name} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    else:
        print(f"{package_name} is already installed.")

required_packages = ["matplotlib", "numpy", "tkinter"]

for package in required_packages:
    check_and_install(package)

import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox

# Dictionary to handle plot styling based on encoding type
PLOT_STYLES = {
    "NRZ-L": {"color": "blue", "linestyle": "-", "marker": "o", "ylim": (-1.5, 1.5), "linewidth": 2},
    "NRZ-I": {"color": "green", "linestyle": "--", "marker": "s", "ylim": (-1.5, 1.5), "linewidth": 2},
    "Bipolar AMI": {"color": "red", "linestyle": "-.", "marker": "x", "ylim": (-1.5, 1.5), "linewidth": 2},
    "Pseudoternary": {"color": "purple", "linestyle": ":", "marker": "d", "ylim": (-1.5, 1.5), "linewidth": 2},
    "Manchester": {"color": "orange", "linestyle": "-", "ylim": (-1.5, 1.5), "linewidth": 3},
    "Differential Manchester": {"color": "teal", "linestyle": "--", "ylim": (-1.5, 1.5), "linewidth": 3},
}

def plot_signal(time, signal, title, binary_data):
    plt.figure(figsize=(12, 4))
    style = PLOT_STYLES.get(title, {"color": "black", "linestyle": "-", "ylim": (-1.5, 1.5), "linewidth": 2})
    
    # Plot signal with specified styles
    plt.step(time, signal, where='post', color=style["color"], linestyle=style["linestyle"], 
             linewidth=style["linewidth"], marker=style.get("marker", ""))
    plt.ylim(style["ylim"])
    plt.xlim(-0.1, max(time) + 0.1)
    plt.title(title)
    plt.xlabel('Input Data')
    plt.ylabel('Signal Level')
    
    # Add vertical lines at each second (or appropriate intervals for other encodings)
    for t in np.arange(0, max(time), 1):
        plt.axvline(x=t, color='gray', linestyle='--', linewidth=0.5)
    
    # Replace x-axis ticks with the binary data labels
    plt.xticks(ticks=np.arange(0, len(binary_data), 1), labels=binary_data)
    
    plt.grid()
    plt.show()

# Signal encoding functions
def nrz_l(data):
    return [1 if bit == '1' else -1 for bit in data]

def nrz_i(data): 
    return [-1 if bit == '1' else 1 for bit in data]

def bipolar_ami(data): 
    signal = []
    level = 1  # Start with +1 for the first '1' bit
    for bit in data:
        if bit == '1':
            signal.append(level)
            level *= -1  # Toggle polarity for the next '1'
        else:
            signal.append(0)  # '0' is represented as 0
    return signal

def pseudoternary(data): 
    signal = []
    level = 1  # Start with +1 for the first '0' bit
    for bit in data:
        if bit == '0':
            signal.append(level)
            level *= -1  # Toggle polarity for the next '0'
        else:
            signal.append(0)  # '1' is represented as 0
    return signal

def manchester(data):
    signal = []
    for bit in data:
        if bit == '1':
            signal.extend([1, -1])  # Represent '1' as [1, -1]
        else:
            signal.extend([-1, 1])  # Represent '0' as [-1, 1]
    return signal

def differential_manchester(data):
    signal = []
    level = 1  # Initial level can be 1 or -1
    for bit in data:
        if bit == '1':
            level *= -1  # Toggle level for '1' at the start of the bit period
            signal.extend([level, -level])  # Transition within the bit period
        else:
            signal.extend([level, level])  # Maintain level, but transition mid-bit
            level *= -1  # Ensure a mid-bit transition
    return signal

# Handle encoding selection and plotting
def plot_selected_encoding():
    encoding = encoding_var.get()
    binary_data = data_entry.get()

    try:
        # Check if an encoding is selected
        if encoding == "" or encoding == '0':  # Ensure '0' is not considered a valid selection
            raise ValueError("Please select an encoding technique.")

        if binary_data == "":
            messagebox.showwarning("Input Error", "Please enter binary data.")
            return

        if not all(bit in '01' for bit in binary_data):
            messagebox.showwarning("Input Error", "Please enter a valid binary sequence (only 0s and 1s).")
            return

        # Signal generation based on encoding
        encoding_funcs = {
            "NRZ-L": nrz_l, "NRZ-I": nrz_i, "Bipolar AMI": bipolar_ami, 
            "Pseudoternary": pseudoternary, "Manchester": manchester, "Differential Manchester": differential_manchester
        }

        signal = encoding_funcs[encoding](list(binary_data))

        # Adjust time for Manchester and Differential Manchester to plot lines every second
        if encoding in ["Manchester", "Differential Manchester"]:
            time = np.arange(0, len(signal) / 2, 0.5)  # Half-bit intervals for signal
        else:
            time = np.arange(0, len(signal), 1)  # Whole seconds for other encodings

        plot_signal(time, signal, encoding, binary_data)

    except ValueError as ve:
        messagebox.showwarning("Input Error", str(ve))  # Show the error message in a pop-up

# Create the main application window
root = tk.Tk()
root.title("Digital Encoding Techniques")
root.geometry("500x500")  # Set a larger window size

# Center the window
window_width = 400
window_height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_position = int(screen_width / 2 - window_width / 2)
y_position = int(screen_height / 2 - window_height / 2)

root.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')

# Use a stylish frame with a white background for better aesthetics
frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
frame.pack(padx=20, pady=20, fill="both", expand=True)

encoding_var = tk.StringVar(value=0)

# Label for the title
title_label = tk.Label(frame, text="Select Encoding and Enter Data", font=("Helvetica", 14, "bold"), bg="#f0f0f0")
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

# Create radio buttons for each encoding technique with nicer design
encoding_options = [
    "NRZ-L", "NRZ-I", "Bipolar AMI", "Pseudoternary", "Manchester", "Differential Manchester"
]
for i, option in enumerate(encoding_options):
    rb = tk.Radiobutton(frame, text=option, variable=encoding_var, value=option, font=("Helvetica", 12), 
                        bg="#f0f0f0", anchor="w", padx=10)
    rb.grid(row=i + 1, column=0, sticky="w", pady=5)

# Label and Entry for binary data input with nice padding
data_label = tk.Label(frame, text="Enter binary data (e.g., 1011001101):", font=("Helvetica", 12), bg="#f0f0f0")
data_label.grid(row=len(encoding_options) + 1, column=0, sticky="w", pady=(20, 5))

data_entry = tk.Entry(frame, font=("Helvetica", 12), width=30, borderwidth=2, relief="solid")
data_entry.grid(row=len(encoding_options) + 2, column=0, pady=10)

# Create a button to plot the selected encoding with a better style
plot_button = tk.Button(frame, text="Plot Signal", command=plot_selected_encoding, font=("Helvetica", 12, "bold"), 
                        bg="#4CAF50", fg="white", padx=20, pady=10, relief="raised")
plot_button.grid(row=len(encoding_options) + 3, column=0, pady=10)

# Start the GUI event loop
root.mainloop()
