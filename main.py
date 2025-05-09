import os
import numpy as np
import scipy.io.wavfile as wav
import soundfile as sf
from scipy.signal import sawtooth, square
import matplotlib.pyplot as plt
import soundfile as sf


input_folder = "D:\\workb\\PythonPiano\\assets\\notes"
output_folder = "D:\\workb\\PythonPiano\\assets\\output_wav"

os.makedirs(output_folder, exist_ok=True)

waveform_type = "square"  # Change to "sine", "square", "triangle" as needed

def rms(signal):
    return np.sqrt(np.mean(signal**2))

def apply_envelope(signal, fade_out_pct=0.2):
    total_samples = len(signal)
    decay_samples = int(total_samples * fade_out_pct)

    envelope = np.ones(total_samples)
    fade_curve = np.linspace(1, 0, decay_samples)
    envelope[-decay_samples:] = fade_curve

    return signal * envelope


def synthesize_wave(freq, duration, sample_rate, waveform):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    if waveform == "sine":
        wave = np.sin(2 * np.pi * freq * t)
    elif waveform == "square":
        wave = square(2 * np.pi * freq * t)
    elif waveform == "sawtooth":
        wave = sawtooth(2 * np.pi * freq * t)
    elif waveform == "triangle":
        wave = sawtooth(2 * np.pi * freq * t, width=0.5)
    else:
        raise ValueError("Unknown waveform type")
    return wave

def estimate_pitch(samples, sample_rate):
    fft = np.fft.fft(samples)
    freqs = np.fft.fftfreq(len(fft), 1 / sample_rate)
    magnitude = np.abs(fft[:len(fft)//2])
    peak_idx = np.argmax(magnitude)
    return abs(freqs[peak_idx])

for file in os.listdir(input_folder):
    if file.lower().endswith(".wav"):
        filepath = os.path.join(input_folder, file)
        sample_rate, samples = wav.read(filepath)
        if samples.ndim > 1:
            samples = samples.mean(axis=1)
        samples = samples.astype(np.float32)
        duration = len(samples) / sample_rate

        freq = estimate_pitch(samples, sample_rate)
        print(f"Processing {file}: {freq:.1f} Hz")

        # Synthesize waveform
        new_wave = synthesize_wave(freq, duration, sample_rate, waveform_type)

        # Apply fade-out envelope (last 20% of signal)
        new_wave = apply_envelope(new_wave, fade_out_pct=0.9)

        
        """ plt.plot(new_wave[-2000:])  # Show last samples to visualize fade
        plt.title("Last part of waveform with fade-out")
        plt.show()
        """
        # Normalize to original RMS
        original_rms = rms(samples)
        new_rms = rms(new_wave)
        if new_rms > 0:
            new_wave = new_wave * (original_rms / new_rms)

        # Save output
        output_path = os.path.join(output_folder, file)
        sf.write(output_path, new_wave, sample_rate, subtype='PCM_16')

