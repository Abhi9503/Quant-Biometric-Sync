import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
import sync_data as sd

class MachineConfig:
    def __init__(self):
        # Initialize with an empty configuration
        self.config_data = {}
        self.load_config()

    def get_config_value(self, machine, key):
        return self.config_data.get(machine, {}).get(key, "")

    def set_config_value(self, machine, key, value):
        if machine not in self.config_data:
            self.config_data[machine] = {}
        self.config_data[machine][key] = value
        self.save_config()

    def save_config(self):
        with open("config.json", "w") as file:
            json.dump(self.config_data, file)

    def load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as file:
                self.config_data = json.load(file)


class MachineConfigFrame(ttk.Frame):
    def __init__(self, master, machine_id):
        super().__init__(master)
        self.machine_id = machine_id

        # Create a MachineConfig instance for this frame
        self.machine_config = MachineConfig()

        # Configure column and row weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Title Label
        title_label = ttk.Label(self, text=f"Machine No - {machine_id}", font=("Helvetica", 14, "bold"))
        title_label.grid(row=(machine_id - 1) * 7, column=0, columnspan=2, pady=(10, 15))

        # Entry Fields and Labels
        labels = ["IP Address", "Port Number", "Device ID", "URL", "API Key", "Secret Key"]
        entry_fields = {}
        for row, label in enumerate(labels, start=1):
            label_widget = ttk.Label(self, text=label, font=("Helvetica", 10, "bold"))
            label_widget.grid(row=(machine_id - 1) * 7 + row, column=0, pady=5, padx=(10, 5), sticky="e")

            entry_value = tk.StringVar()

            # Use a password-like entry for API Key and API Secret Key
            if "API Key" in label or "Secret Key" in label:
                entry = ttk.Entry(self, textvariable=entry_value, show="*", font=("Helvetica", 10))
            else:
                entry = ttk.Entry(self, textvariable=entry_value, font=("Helvetica", 10))

            entry.grid(row=(machine_id - 1) * 7 + row, column=1, pady=5, padx=(5, 10), sticky="w")

            # Set initial value if available
            initial_value = self.machine_config.get_config_value(f"machine_{machine_id}", label.lower().replace(" ", "_"))
            entry_value.set(initial_value)

            # Add placeholder text as a label inside the entry
            # entry.insert(0, label)
            entry.bind("<FocusIn>", lambda event, entry=entry, label=label: self.on_entry_click(event, entry, label))

            entry_fields[label] = entry_value

        # Set Button
        set_button = ttk.Button(self, text="Set Configuration", command=lambda: self.set_configuration(entry_fields), style="TButton")
        set_button.grid(row=(machine_id - 1) * 7 + len(labels) + 1, column=1, columnspan=2, pady=15, ipadx=10, ipady=5)

    def on_entry_click(self, event, entry, label):
        """Function to handle placeholder text inside the entry."""
        if entry.get() == label:
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def set_configuration(self, entry_fields):
        machine = f"machine_{self.machine_id}"

        # Set values in the configuration
        for label, entry_value in entry_fields.items():
            field_value = entry_value.get()
            self.machine_config.set_config_value(machine, label.lower().replace(" ", "_"), field_value)

        # Display a message
        messagebox.showinfo("Configuration Set", f"Machine {self.machine_id} configuration has been set.")
        
  
def sync_data():
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()
    formatted_start_date = start_date.strftime("%Y-%m-%d")
    formatted_end_date = end_date.strftime("%Y-%m-%d")
    messagebox.showinfo("Sync Data", "Your Biometric Attendance Data is Syncing Please Wait...")
    
    with open("config.json", "r") as file:
        config_data = json.load(file)

    for machine, params in config_data.items():
        ip_address=""
        port_number=""
        device_id=""
        url=""
        secret_key=""
        api_key=""
        for key, value in params.items():
            if(key=="ip_address"):
                ip_address=value
            elif(key=="port_number"):
                port_number=value
            elif(key=="device_id"):
                device_id=value
            elif(key=="url"):
                url=value
            elif(key=="secret_key"):
                secret_key=value
            elif(key=="api_key"):
                api_key=value
       
        api_token=f"token {api_key}:{secret_key}"
        if(ip_address!=""and  port_number!="" and api_key!="" and device_id!="" and secret_key!="" and url!=""):
            attendance_data=sd.get_attendance_data(formatted_start_date,formatted_end_date,ip_address,device_id,port_number)
            sd.send_to_erpnext(url,api_token,attendance_data)
    app.destroy()



# Create the main application window
app = tk.Tk()
app.title("Quantbit Bio Metric Sync")

# Set the window size
app.geometry("700x500")  # Increased window size for better visibility

# Set a consistent theme
style = ttk.Style()
style.theme_use("clam")

# Create a notebook (tabbed interface)
notebook = ttk.Notebook(app)
notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # Added padx and pady

# Create a frame for the "Sync Data" tab
sync_data_frame = ttk.Frame(notebook)
notebook.add(sync_data_frame, text="Sync Data")

# Create and place widgets in the "Sync Data" tab
start_date_label = ttk.Label(sync_data_frame, text="Start Date:", font=("Helvetica", 12))
start_date_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

start_date_entry = DateEntry(sync_data_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
start_date_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

end_date_label = ttk.Label(sync_data_frame, text="End Date:", font=("Helvetica", 12))
end_date_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")

end_date_entry = DateEntry(sync_data_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
end_date_entry.grid(row=0, column=3, padx=5, pady=10, sticky="w")

sync_button = ttk.Button(sync_data_frame, text="Sync Data", command=sync_data, style="TButton")
sync_button.grid(row=1, column=0, columnspan=4, pady=10, ipadx=20, ipady=5)

# Center the widgets within the frame
sync_data_frame.columnconfigure((0, 1, 2, 3), weight=1)  # Center horizontally
sync_data_frame.rowconfigure((0, 1), weight=1)  # Center vertically




# Create a frame for the "Machine Configuration" tab
machine_config_frame = ttk.Frame(notebook)
notebook.add(machine_config_frame, text="Machine Configuration")

# Create a frame for Machine 1 configuration
machine_config_frame_1 = MachineConfigFrame(machine_config_frame, 1)
machine_config_frame_1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Create a frame for Machine 2 configuration
machine_config_frame_2 = MachineConfigFrame(machine_config_frame, 2)
machine_config_frame_2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Add padding after the notebook
notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")






# Configure notebook to expand with the window
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)


# Start the main event loop
app.mainloop()