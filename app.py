import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import threading
import subprocess
import sys
from screen_ocr import start_recording, stop_recording, query, process_with_ollama
import pkg_resources

# Start/Stop flag
is_recording = False

def install_requirements():
    """
    Automatically install requirements from requirements.txt if not already installed.
    """
    # Read requirements from the requirements.txt file
    with open("requirements.txt") as f:
        required_packages = f.read().splitlines()
    
    # Find out which packages are already installed
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    
    # Identify packages that are not yet installed
    to_install = [pkg for pkg in required_packages if pkg.lower().split('==')[0] not in installed_packages]

    # If there are packages to install, proceed with the installation
    if to_install:
        print("Installing missing packages:", to_install)
        subprocess.call([sys.executable, "-m", "pip", "install", *to_install])
    else:
        print("All required packages are already installed.")

def start_recording_from_gui():
    global is_recording
    interval = int(interval_entry.get())
    duration_min = int(duration_min_entry.get())
    duration_sec = int(duration_sec_entry.get())
    duration = duration_min * 60 + duration_sec  # Total duration in seconds
    
    # Set the flag to start recording
    is_recording = True
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    progress_label.config(text="Recording...")

    # Start the screen recording in a separate thread
    threading.Thread(target=start_recording, args=(duration, interval)).start()

def stop_recording_from_gui():
    global is_recording
    is_recording = False  # Set the flag to stop recording
    stop_recording()  # Explicitly call the function to stop recording
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    progress_label.config(text="Recording Stopped.")

def fetch_file_content():
    try:
        with open('text.txt', 'r') as file:
            content = file.read()
            display_text.delete(1.0, tk.END)  # Clear previous content
            display_text.insert(tk.END, content)  # Insert new content
    except FileNotFoundError:
        messagebox.showerror("Error", "The file 'text.txt' was not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Set up the main application window
app = tk.Tk()
app.title("Screen Recorder")
app.state('zoomed')  # Start the window maximized

# Custom Styles
app.configure(bg="#1c1c1e")

style = ttk.Style()
style.theme_use("clam")

style.configure("TButton", font=("Segoe UI", 16), background="#0A84FF", foreground="white", borderwidth=0, focuscolor='none')
style.map("TButton", background=[("active", "#007AFF")])
style.configure("TLabel", font=("Segoe UI", 18), background="#1c1c1e", foreground="white")
style.configure("TEntry", font=("Segoe UI", 16), fieldbackground="#2c2c2e", foreground="white")

# Title Label
title_label = ttk.Label(app, text="Futuristic Screen Recorder", font=("Segoe UI", 30, "bold"))
title_label.pack(pady=30)

# Container Frame for Inputs
input_frame = tk.Frame(app, bg="#1c1c1e")
input_frame.pack(pady=10)

# Input fields for interval and duration
interval_label = ttk.Label(input_frame, text="Interval (seconds):")
interval_label.grid(row=0, column=0, padx=20, pady=20, sticky="e")
interval_entry = ttk.Entry(input_frame, width=10)
interval_entry.grid(row=0, column=1, padx=20, pady=20)

duration_min_label = ttk.Label(input_frame, text="Duration (minutes):")
duration_min_label.grid(row=1, column=0, padx=20, pady=20, sticky="e")
duration_min_entry = ttk.Entry(input_frame, width=10)
duration_min_entry.grid(row=1, column=1, padx=20, pady=20)

duration_sec_label = ttk.Label(input_frame, text="Duration (seconds):")
duration_sec_label.grid(row=2, column=0, padx=20, pady=20, sticky="e")
duration_sec_entry = ttk.Entry(input_frame, width=10)
duration_sec_entry.grid(row=2, column=1, padx=20, pady=20)

# Buttons Container
button_frame = tk.Frame(app, bg="#1c1c1e")
button_frame.pack(pady=30)

start_button = ttk.Button(button_frame, text="Start Recording", command=start_recording_from_gui)
start_button.grid(row=0, column=0, padx=20, pady=10)

stop_button = ttk.Button(button_frame, text="Stop Recording", command=stop_recording_from_gui, state=tk.DISABLED)
stop_button.grid(row=0, column=1, padx=20, pady=10)

# Fetch File Content Button
fetch_button = ttk.Button(button_frame, text="Fetch File Content", command=fetch_file_content)
fetch_button.grid(row=0, column=2, padx=20, pady=10)

# Progress Label
progress_label = ttk.Label(app, text="")
progress_label.pack(pady=10)

# Display Text Area for File Content
display_text = scrolledtext.ScrolledText(app, width=80, height=20, font=("Segoe UI", 14))
display_text.pack(pady=20)

# Top-Level Frame for Custom Control Buttons
control_frame = tk.Frame(app, bg="#1c1c1e")
control_frame.pack(side=tk.TOP, anchor="ne", pady=5, padx=5)

# Minimize Button
def minimize_app():
    app.iconify()

minimize_button = tk.Button(control_frame, text="_", font=("Segoe UI", 12), command=minimize_app, bg="#2c2c2e", fg="white", bd=0)
minimize_button.pack(side=tk.LEFT, padx=5)

# Maximize/Restore Button
def toggle_maximize():
    if app.state() == "zoomed":
        app.state("normal")
    else:
        app.state("zoomed")

maximize_button = tk.Button(control_frame, text="❐", font=("Segoe UI", 12), command=toggle_maximize, bg="#2c2c2e", fg="white", bd=0)
maximize_button.pack(side=tk.LEFT, padx=5)

# Close Button
def close_app():
    if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
        app.quit()  # Properly quit the Tkinter main loop
        app.destroy()  # Ensure the window is destroyed without re-executing

close_button = tk.Button(control_frame, text="✖", font=("Segoe UI", 12), command=close_app, bg="#E74C3C", fg="white", bd=0)
close_button.pack(side=tk.LEFT, padx=5)

# Install required packages before starting the app
install_requirements()

# Run the GUI application
app.mainloop()
