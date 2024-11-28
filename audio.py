import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment

def browse_input_file():
    file_path = filedialog.askopenfilename(
        title="Select Input Audio File",
        filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg")]
    )
    if file_path:
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, file_path)

def browse_output_file():
    file_path = filedialog.asksaveasfilename(
        title="Select Output File Location",
        defaultextension=".mp3",
        filetypes=[("MP3 Files", "*.mp3")]
    )
    if file_path:
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, file_path)

def process_audio():
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    gains = [sliders[i].get() for i in range(10)]

    if not input_file or not output_file:
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
        messagebox.showinfo("Success", f"Audio saved to {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main application window
root = tk.Tk()
root.title("Group 1 Audio Equalizer")

# Input File Selector
input_file_label = tk.Label(root, text="Input File:")
input_file_label.pack(pady=5)

input_file_entry = tk.Entry(root, width=50)
input_file_entry.pack(pady=5)

browse_input_button = tk.Button(root, text="Browse", command=browse_input_file)
browse_input_button.pack(pady=5)

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
process_button = tk.Button(root, text="Save", command=process_audio)
process_button.pack(pady=20)

# Start the main event loop
root.mainloop()