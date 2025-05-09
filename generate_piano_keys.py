import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import os
import soundfile as sf

# Constants
SAMPLE_RATE = 44100
DURATION = 1.5  # seconds
FADE_OUT_PCT = 0.7
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']


def note_to_freq(midi_note):
    return 440.0 * 2 ** ((midi_note - 69) / 12)


def generate_waveform(freq, t, waveform):
    if waveform == "sine":
        return np.sin(2 * np.pi * freq * t)
    elif waveform == "square":
        return np.sign(np.sin(2 * np.pi * freq * t))
    elif waveform == "triangle":
        return 2 * np.abs(2 * ((t * freq) % 1) - 1) - 1
    elif waveform == "sawtooth":
        return 2 * ((t * freq) % 1) - 1
    else:
        return np.zeros_like(t)


def apply_fade_out(wave, fade_pct):
    length = len(wave)
    fade_samples = int(length * fade_pct)
    envelope = np.ones(length)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    return wave * envelope


def apply_reverb(wave, decay=0.4, delay=0.03):
    delay_samples = int(SAMPLE_RATE * delay)
    echo_wave = np.zeros(len(wave) + delay_samples)
    echo_wave[:len(wave)] += wave
    echo_wave[delay_samples:] += wave * decay
    return echo_wave[:len(wave)]


def generate_notes(waveforms, fade_out_enabled, reverb_enabled, base_output_dir):
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    for midi in range(21, 109):  # A0 to B7 (8 octaves)
        freq = note_to_freq(midi)
        note = NOTE_NAMES[midi % 12].replace('#', 'b')
        octave = (midi // 12) - 1
        note_name = f"{note}{octave}.wav"

        for waveform in waveforms:
            wave = generate_waveform(freq, t, waveform).astype(np.float32)

            if fade_out_enabled:
                wave = apply_fade_out(wave, FADE_OUT_PCT)

            if reverb_enabled:
                wave = apply_reverb(wave)

            wave = wave / np.max(np.abs(wave))  # Normalize

            folder = os.path.join(base_output_dir, waveform)
            os.makedirs(folder, exist_ok=True)

            filepath = os.path.join(folder, note_name)
            sf.write(filepath, wave, SAMPLE_RATE, subtype='PCM_16')

    messagebox.showinfo("Done", "✅ Notes generated successfully!")


# --- GUI ---
root = tk.Tk()
root.title("Instrument Note Generator")

waveform_vars = {
    "sine": tk.BooleanVar(value=True),
    "square": tk.BooleanVar(),
    "triangle": tk.BooleanVar(),
    "sawtooth": tk.BooleanVar(),
}

fade_out_var = tk.BooleanVar(value=True)
reverb_var = tk.BooleanVar(value=False)
output_folder = tk.StringVar()
output_folder.set("generated_notes_gui")

tk.Label(root, text="Select Instruments (Waveforms):").pack()
for name, var in waveform_vars.items():
    tk.Checkbutton(root, text=name.title(), variable=var).pack(anchor="w")

tk.Checkbutton(root, text="Apply Fade-Out", variable=fade_out_var).pack(anchor="w")
tk.Checkbutton(root, text="Apply Reverb", variable=reverb_var).pack(anchor="w")

# Folder selector
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder.set(folder)

tk.Label(root, text="Output Folder:").pack(pady=(10, 0))
tk.Entry(root, textvariable=output_folder, width=40).pack()
tk.Button(root, text="Select Folder", command=select_folder).pack(pady=5)

def on_generate():
    selected = [name for name, var in waveform_vars.items() if var.get()]
    if not selected:
        messagebox.showerror("Error", "Please select at least one waveform.")
        return

    generate_notes(
        waveforms=selected,
        fade_out_enabled=fade_out_var.get(),
        reverb_enabled=reverb_var.get(),
        base_output_dir=output_folder.get()
    )

tk.Button(root, text="🎵 Generate Notes", command=on_generate,
          bg="green", fg="white", font=("Arial", 12, "bold")).pack(pady=15)

root.mainloop()
