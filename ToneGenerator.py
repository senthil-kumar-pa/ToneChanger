import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
import soundfile as sf
import sounddevice as sd
from scipy.signal import sawtooth, square

# === Sound Generation ===
SAMPLE_RATE = 44100

NOTE_FREQS = {
    name + str(oct): 440.0 * 2 ** ((i + (oct - 4) * 12) / 12)
    for oct in range(0, 8)
    for i, name in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])
}

def generate_waveform(frequency, duration, waveform):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    if waveform == 'sine':
        return np.sin(2 * np.pi * frequency * t)
    elif waveform == 'square':
        return square(2 * np.pi * frequency * t)
    elif waveform == 'sawtooth':
        return sawtooth(2 * np.pi * frequency * t)
    elif waveform == 'triangle':
        return 2 * np.abs(sawtooth(2 * np.pi * frequency * t, 0.5)) - 1
    return np.zeros_like(t)

def apply_adsr(wave, attack, decay, sustain, release):
    total_len = len(wave)
    attack_len = int(SAMPLE_RATE * attack)
    decay_len = int(SAMPLE_RATE * decay)
    release_len = int(SAMPLE_RATE * release)
    sustain_len = total_len - (attack_len + decay_len + release_len)
    sustain_len = max(0, sustain_len)

    envelope = np.concatenate([
        np.linspace(0, 1, attack_len, False),
        np.linspace(1, sustain, decay_len, False),
        np.full(sustain_len, sustain),
        np.linspace(sustain, 0, release_len, False)
    ])
    envelope = np.pad(envelope, (0, max(0, total_len - len(envelope))), mode='constant')
    return wave * envelope

def apply_reverb(wave, decay=0.3):
    delay_samples = int(0.02 * SAMPLE_RATE)
    result = np.copy(wave)
    for i in range(delay_samples, len(wave)):
        result[i] += decay * result[i - delay_samples]
    return result

# === GUI Application ===
class ToneGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tone Generator")
        self.output_dir = os.getcwd()

        # Waveform and tone
        self.waveform = tk.StringVar(value="sine")
        self.note = tk.StringVar(value="A4")
        self.reverb_enabled = tk.BooleanVar(value=False)

        # ADSR Sliders
        self.attack = tk.DoubleVar(value=0.01)
        self.decay = tk.DoubleVar(value=0.1)
        self.sustain = tk.DoubleVar(value=0.7)
        self.release = tk.DoubleVar(value=0.2)

        # UI layout
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Waveform:").grid(row=0, column=0)
        ttk.Combobox(frame, textvariable=self.waveform, values=['sine', 'square', 'sawtooth', 'triangle']).grid(row=0, column=1)

        ttk.Label(frame, text="Note:").grid(row=1, column=0)
        ttk.Combobox(frame, textvariable=self.note, values=sorted(NOTE_FREQS.keys())).grid(row=1, column=1)

        ttk.Checkbutton(frame, text="Reverb", variable=self.reverb_enabled).grid(row=2, column=0, columnspan=2)

        # Sliders
        self.add_slider(frame, "Attack", self.attack, 0.0, 1.0, 3)
        self.add_slider(frame, "Decay", self.decay, 0.0, 1.0, 4)
        self.add_slider(frame, "Sustain", self.sustain, 0.0, 1.0, 5)
        self.add_slider(frame, "Release", self.release, 0.0, 1.0, 6)

        # Buttons
        ttk.Button(frame, text="Select Output Folder", command=self.select_output).grid(row=7, column=0)
        ttk.Button(frame, text="Preview", command=self.preview_sound).grid(row=7, column=1)
        ttk.Button(frame, text="Generate WAV", command=self.generate_wav).grid(row=8, column=0, columnspan=2)

    def add_slider(self, parent, label, variable, min_, max_, row):
        ttk.Label(parent, text=label).grid(row=row, column=0)
        ttk.Scale(parent, variable=variable, from_=min_, to=max_, orient='horizontal').grid(row=row, column=1)

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder

    def generate_tone(self, note, duration=2.0):
        freq = NOTE_FREQS[note]
        wave = generate_waveform(freq, duration, self.waveform.get())
        wave = apply_adsr(wave, self.attack.get(), self.decay.get(), self.sustain.get(), self.release.get())
        if self.reverb_enabled.get():
            wave = apply_reverb(wave)
        wave = wave * 0.5  # Normalize amplitude
        return wave.astype(np.float32)

    def preview_sound(self):
        wave = self.generate_tone(self.note.get())
        sd.play(wave, samplerate=SAMPLE_RATE)
        sd.wait()

    def generate_wav(self):
        wave = self.generate_tone(self.note.get())
        output_path = os.path.join(self.output_dir, f"{self.note.get()}_{self.waveform.get()}.wav")
        sf.write(output_path, wave, SAMPLE_RATE)
        print(f"Saved to {output_path}")

# === Run Application ===
if __name__ == "__main__":
    root = tk.Tk()
    app = ToneGeneratorApp(root)
    root.mainloop()
