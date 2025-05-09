import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# Parameters
sample_rate = 44100
duration = 2.0  # seconds
frequency = 440  # Hz (A4)
fade_out_pct = 0.75  # fade over the last 50%

# Time axis
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Generate sine wave
wave = np.sin(2 * np.pi * frequency * t).astype(np.float32)

# Apply fade-out envelope
def apply_envelope(signal, fade_out_pct=0.5):
    total_samples = len(signal)
    decay_samples = int(total_samples * fade_out_pct)
    envelope = np.ones(total_samples)
    fade_curve = np.linspace(1.0, 0.0, decay_samples)
    envelope[-decay_samples:] = fade_curve
    return signal * envelope

wave_faded = apply_envelope(wave, fade_out_pct=fade_out_pct)

# Save as 16-bit PCM WAV
sf.write("fade_out_test.wav", wave_faded, sample_rate, subtype='PCM_16')

# Optional: plot the last part of waveform to visualize fade-out
plt.plot(wave_faded[-2000:])
plt.title("Last part of waveform (Fade-Out)")
plt.xlabel("Sample")
plt.ylabel("Amplitude")
plt.show()
