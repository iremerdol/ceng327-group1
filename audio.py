import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
from pydub import AudioSegment
from tkinter import ttk
import threading
import os
from pydub import AudioSegment
from pydub.utils import which

# Global variables to store the original and processed audio
original_audio = None
processed_audio = None

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
    #browse_output_button.config(state="disabled")
    sample_button.config(state="disabled")
    save_button.config(state="disabled")

def enable_controls():
    # Enable buttons and sliders
    for slider in sliders:
        slider.config(state="normal")
    process_button.config(state="normal")
    browse_input_button.config(state="normal")
    #browse_output_button.config(state="normal")
    sample_button.config(state="normal")
    save_button.config(state="normal")


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
    global original_audio
    file_path = filedialog.askopenfilename(
        title="Select Input Audio File",
        filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg")]
    )
    if file_path:
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, file_path)
        try:
            # Save the original audio
            original_audio = AudioSegment.from_file(file_path)
            messagebox.showinfo("Success", "Audio file loaded successfully.")
            go_to_page2()
            enable_controls()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load audio: {str(e)}")

def browse_output_file():
    file_path = filedialog.asksaveasfilename(
        title="Select Output File Location",
        defaultextension=f"{file_format.get()}",
        filetypes=[(f"{file_format.get().upper()} Files", f"*{file_format.get()}")]
    )
    if file_path:
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, file_path)

# Get list of audio files in src folder
def get_sample_files():
    sample_files = [f for f in os.listdir("src") if f.endswith(f".{file_format.get()}")]
    return sample_files

def get_sample_sound():
    global current_sample_index,original_audio

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

        # Load the sample audio into the global original_audio variable
        original_audio = AudioSegment.from_file(file_path)

        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, file_path)

        # Get the base name of the input file (without the extension)
        input_filename_without_extension = os.path.splitext(current_sample_file)[0]

        # Save output file to 'Outputs' folder
        output_file_name = f"{input_filename_without_extension}_output{file_format.get()}" 
        output_file_path = os.path.join(output_dir, output_file_name)
        
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, output_file_path)

        current_sample_index = (current_sample_index + 1) % len(sample_files)

        go_to_page2()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

AudioSegment.converter = which("ffmpeg")
def process_audio():
    global original_audio, processed_audio

    if original_audio is None:
        hide_progress_bar()
        messagebox.showerror("Error", "No audio loaded. Please select an audio file first.")
        return

    disable_controls()

    # Obtain slider values
    gains = [sliders[i].get() for i in range(10)]

    try:
        # Create a copy of the original audio to process
        audio = original_audio
        
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

        # Store the processed audio
        processed_audio = audio

        hide_progress_bar() # Hide progress bar and show success message
        messagebox.showinfo("Success", f"Audio is processed successfully")
        enable_controls()

    except Exception as e:
        hide_progress_bar() # Hide progress bar and show error message in case of error
        messagebox.showerror("Error", f"An error occurred: {e}")

def export_audio():
    global processed_audio

    if processed_audio is None:
        messagebox.showerror("Error", "No processed audio to save. Please process the audio first.")
        return

    output_file = filedialog.asksaveasfilename(
        title="Select Output File Location",
        defaultextension=".mp3",
        filetypes=[("MP3 Files", "*.mp3"), ("WAV Files", "*.wav"), ("FLAC Files", "*.flac"), ("OGG Files", "*.ogg")]
    )

    # Check if the user cancelled the save dialog
    if not output_file:
        return

    try:
        # Export the modified audio
        processed_audio.export(output_file, format=os.path.splitext(output_file)[1][1:])
        hide_progress_bar()  # Hide progress bar and show success message
        messagebox.showinfo("Success", f"Audio saved to {output_file}")
    except Exception as e:
        hide_progress_bar()  # Hide progress bar and show error message
        messagebox.showerror("Error", f"Failed to export audio: {str(e)}")

def go_to_page2():
    page1.pack_forget() # hide page 1
    page2.pack(fill="both",expand=True) # show page 2

def go_to_page1():
    global original_audio,processed_audio
    original_audio,processed_audio = None,None # resets audio files
    page2.pack_forget() # hide page 2
    page1.pack(fill="both",expand=True) # show page 1


# Create the main application window
root = tk.Tk()
root.title("Group 1 Audio Equalizer")

# Create two pages to be shown later
page1 = tk.Frame(root)
page2 = tk.Frame(root)

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
input_file_label = tk.Label(page1, text="Input File:")
input_file_label.pack(pady=5)

input_file_entry = tk.Entry(page1, width=50)
input_file_entry.pack(pady=5)

# Create two frames to place buttons in a row
button_frame_for_page1 = tk.Frame(page1)
button_frame_for_page2 = tk.Frame(page2)
button_frame_for_page1.pack(pady=10)
#button_frame_for_page2.pack(pady=10)

browse_input_button = tk.Button(button_frame_for_page1, text="Browse", command=browse_input_file)
browse_input_button.pack(side=tk.LEFT, padx=5)

or_label = tk.Label(button_frame_for_page1, text="or")
or_label.pack(side=tk.LEFT, padx=5)

# Get sample sound from src file
sample_button = tk.Button(button_frame_for_page1, text="Get Sample Sound", command=get_sample_sound)
sample_button.pack(side=tk.LEFT, padx=5)

# Equalizer Sliders
slider_frame = tk.Frame(page2)
#slider_frame.pack(pady=10)

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

#output_buttons_frame = tk.Frame(page2)

#output_file_label = tk.Label(button_frame_for_page2, text="Output File:")
#output_file_label.pack(pady=5)

output_file_entry = tk.Entry(button_frame_for_page2, width=50)
#output_file_entry.pack(pady=5)

#browse_output_button = tk.Button(output_buttons_frame, text="Browse", command=browse_output_file)
#browse_output_button.pack(side="left",padx=30)

# A variable for file formats
file_format = tk.StringVar()
file_format.set(".mp3")  # Default format

# Function to update the output file extension
def update_output_extension(*args):
    current_extension = file_format.get()  # Get the selected file format
    output_file = output_file_entry.get()  # Get the current output file path

    # Update the output file extension if it exists
    if output_file:
        output_file_base = os.path.splitext(output_file)[0]
        new_output_file = f"{output_file_base}{current_extension}"
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, new_output_file)

# Attach trace to file_format variable
file_format.trace_add("write", update_output_extension)

# Save As Label
#save_as_label = tk.Label(output_buttons_frame, text="Save As:")
#save_as_label.pack(side="left",padx=5)

# Dropdown menu 
#format_menu = tk.OptionMenu(output_buttons_frame, file_format, ".mp3", ".wav", ".flac", ".ogg")
#format_menu.pack(side="left",padx=5)

# Process Button
process_button = tk.Button(button_frame_for_page2, text="Process", command=process_audio_with_progress)
#process_button.pack(pady=20)

# Save Button
save_button = tk.Button(page2, text="Save", command=export_audio)
#save_button.pack(pady=10)

# Back Button
button_image = PhotoImage(file='back_button.png')
back_button = tk.Button(page2,text="back",command=go_to_page1,image=button_image)

# Pack all elements for page 2 (to reorder buttons correctly)
slider_frame.pack(pady=10)
button_frame_for_page2.pack(pady=10)
process_button.pack(pady=10)
#output_file_label.pack(pady=10)
#output_file_entry.pack(pady=10)
#output_buttons_frame.pack(pady=10)
save_button.pack(pady=10)
back_button.pack(side="right",padx = 5)
# Create a fixed frame for progress bar
progress_frame = tk.Frame(page2)
progress_frame.pack(fill=tk.X, pady=5)  # Pin it just below the save button

loading_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=250)
loading_bar.pack(pady=5)  # Stays fixed in the frame
loading_bar.pack_forget()  # Invisible at first

# Show page 1 initially
page1.pack(fill="both", expand=True)

# Start the main event loop
root.mainloop()
