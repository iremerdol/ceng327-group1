in order to run the code:

    pip install tkinter numpy scipy matplotlib pydub pygame
    
for pydub to work need to install ffmpeg:

Windows:
1) Download FFmpeg from https://ffmpeg.org/download.html
2) Extract the FFmpeg files and note the location of the bin folder (e.g., C:\ffmpeg\bin).
3) Add the bin folder to your system's PATH:
  --Open "System Properties" → "Advanced" → "Environment Variables."
  --Find the Path variable, click "Edit," and add the path to the bin folder.
4) Test FFmpeg installation by running ffmpeg -version in the command prompt.

run the code:

    python audio.py

browse for the input file (.mp3, .wav, .flac, .ogg)

also browse for the output file for when the output is created
