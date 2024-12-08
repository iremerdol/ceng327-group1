import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
from tkinter import ttk
import threading
import os

def show_progress_bar():
    loading_bar.pack()  # Make it visible 
    loading_bar.start()

def hide_progress_bar():
    loading_bar.stop()
    loading_bar.pack_forget()  # Hide


def disable_controls():
    # Disable buttons and sliders
    for slider in sliders:
        slider.config(state="disabled")
    process_button.config(state="disabled")
    browse_input_button.config(state="disabled")
    browse_output_button.config(state="disabled")
    sample_button.config(state="disabled")

def enable_controls():
    # Enable buttons and sliders
    for slider in sliders:
        slider.config(state="normal")
    process_button.config(state="normal")
    browse_input_button.config(state="normal")
    browse_output_button.config(state="normal")
    sample_button.config(state="normal")

def process_audio_with_progress():
    disable_controls()  # Disable controls during process
    show_progress_bar()  # Show the loading bar

    def process_audio_thread():
        try:
            process_audio()  
        except Exception as e:
            hide_progress_bar() # Hide previous progress bar
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            hide_progress_bar()  # Hide the loading bar
            enable_controls()  # Re-enable controls after processing

    threading.Thread(target=process_audio_thread, daemon=True).start()

def browse_input_file():
    file_path = filedialog.askopenfilename(
        title="Select Input Audio File",
        filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg")]
    )
    if file_path:
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, file_path)
        enable_controls()  # Enable sliders and process button after file selection

def browse_output_file():
    file_path = filedialog.asksaveasfilename(
        title="Select Output File Location",
        defaultextension=".mp3",
        filetypes=[("MP3 Files", "*.mp3")]
    )
    if file_path:
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, file_path)

# Get list of audio files in src folder
def get_sample_files():
    sample_files = [f for f in os.listdir("src") if f.endswith(('.mp3', '.wav', '.flac', '.ogg'))]
    return sample_files

def get_sample_sound():
    global current_sample_index  

    if not sample_files:
        messagebox.showerror("Error", "No sample files found.")
        return

    try:
        # Get current file
        current_sample_file = sample_files[current_sample_index]

        # Add file path to 'input_file_entry'
        file_path = os.path.join(sample_dir, current_sample_file)
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"Sample file {current_sample_file} not found.")
            return
        
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, file_path)

        # Save output file to 'Outputs' folder
        output_file_name = f"sampleSound{current_sample_index + 1}Output.mp3"
        output_file_path = os.path.join(output_dir, output_file_name)
        
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, output_file_path)

        current_sample_index = (current_sample_index + 1) % len(sample_files)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def process_audio():

    # Get input and output files from user
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    gains = [sliders[i].get() for i in range(10)]

    if not input_file or not output_file:
        hide_progress_bar() # Hide progress bar and show error message
        messagebox.showerror("Error", "Please select both input and output files.")
        return

    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_file)
        
        # Define frequency ranges for the 10 bands
        freq_ranges = [
            (20, 60), (60, 125), (125, 250), (250, 500),
            (500, 1000), (1000, 2000), (2000, 4000),
            (4000, 8000), (8000, 16000), (16000, 20000)
        ]

        # Apply gains to each band
        for i, (low, high) in enumerate(freq_ranges):
            band = audio.low_pass_filter(high).high_pass_filter(low)
            audio = audio.overlay(band.apply_gain(gains[i]))
        
        # Export the modified audio
        audio.export(output_file, format="mp3")
        hide_progress_bar() # Hide progress bar and show success message

        messagebox.showinfo("Success", f"Audio saved to {output_file}")

    except Exception as e:
        hide_progress_bar() # Hide progress bar and show error message in case of error
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main application window
root = tk.Tk()
root.title("Group 1 Audio Equalizer")

# Getting file names in 'SampleSounds' and 'Outputs' folders
sample_dir = os.path.join("src", "SampleSounds")  
output_dir = os.path.join("src", "Outputs") 

# If there are folders, list the files
if not os.path.exists(sample_dir):
    os.makedirs(sample_dir)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

sample_files = [f for f in os.listdir(sample_dir) if f.endswith(('.mp3', '.wav', '.flac', '.ogg'))]  
current_sample_index = 0 


# Input File Selector
input_file_label = tk.Label(root, text="Input File:")
input_file_label.pack(pady=5)

input_file_entry = tk.Entry(root, width=50)
input_file_entry.pack(pady=5)

# Create a frame to place buttons in a row
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

browse_input_button = tk.Button(button_frame, text="Browse", command=browse_input_file)
browse_input_button.pack(side=tk.LEFT, padx=5)

or_label = tk.Label(button_frame, text="or")
or_label.pack(side=tk.LEFT, padx=5)

# Get sample sound from src file
sample_button = tk.Button(button_frame, text="Get Sample Sound", command=get_sample_sound)
sample_button.pack(side=tk.LEFT, padx=5)

# Equalizer Sliders
slider_frame = tk.Frame(root)
slider_frame.pack(pady=10)

labels = [
    "32 Hz", "64 Hz", "125 Hz", "250 Hz", "500 Hz",
    "1 kHz", "2 kHz", "4 kHz", "8 kHz", "16 kHz"
]

sliders = []
for i, label in enumerate(labels):
    tk.Label(slider_frame, text=label).grid(row=0, column=i, padx=5)
    slider = tk.Scale(slider_frame, from_=10, to=-10, orient=tk.VERTICAL)
    slider.set(0)
    slider.grid(row=1, column=i, padx=5)
    sliders.append(slider)

# Output File Selector
output_file_label = tk.Label(root, text="Output File:")
output_file_label.pack(pady=5)

output_file_entry = tk.Entry(root, width=50)
output_file_entry.pack(pady=5)

browse_output_button = tk.Button(root, text="Browse", command=browse_output_file)
browse_output_button.pack(pady=5)

# Process and Save Button
process_button = tk.Button(root, text="Save", command=process_audio_with_progress)
process_button.pack(pady=20)

# Create a fixed frame for progress bar 
progress_frame = tk.Frame(root)
progress_frame.pack(fill=tk.X, pady=5)  # Pin it just below the save button

loading_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=250)
loading_bar.pack(pady=5)  # Stays fixed in the frame
loading_bar.pack_forget()  # Invisible at first

# Start the main event loop
root.mainloop()
