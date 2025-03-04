import numpy as np
import sounddevice as sd
from scipy.signal import butter, filtfilt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
import sys

# === Sound Generation Function ===

def generate_synthetic_tone(duration=2.0, sr=44100, brightness=0.5, warmth=0.5):
    """
    Generate synthetic sound representing brightness & warmth.
    Brightness = upper harmonic content.
    Warmth = low-mid formant strength.
    """
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Fundamental frequency (A3)
    base_freq = 220
    base_wave = np.sin(2 * np.pi * base_freq * t)

    # Brightness: add harmonics
    harmonic_wave = np.zeros_like(base_wave)
    max_harmonics = 10
    for i in range(2, max_harmonics):
        harmonic_wave += np.sin(2 * np.pi * base_freq * i * t) * (brightness ** (i / max_harmonics))

    signal = base_wave + harmonic_wave

    # Warmth: bandpass filter centered in the low-mid range
    if warmth < 0.5:
        low_freq, high_freq = 100, 800
    else:
        low_freq, high_freq = 300, 1500

    formant_shift = (1 - warmth) * 500
    low_freq = max(50, low_freq - formant_shift)
    high_freq = min(2000, high_freq - formant_shift)

    b, a = butter(4, [low_freq / (sr / 2), high_freq / (sr / 2)], btype='band')
    warm_signal = filtfilt(b, a, signal)

    # Blend bright and warm signals
    combined_signal = warmth * warm_signal + (1 - warmth) * signal

    # Normalize
    combined_signal /= np.max(np.abs(combined_signal))

    return combined_signal

# === Main PyQt Application ===

class ToneSynthApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Brightness & Warmth Synth')

        # Layout
        layout = QVBoxLayout()

        # Brightness Slider
        self.brightness_label = QLabel("Brightness: 0.50")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.valueChanged.connect(self.update_brightness)

        # Warmth Slider
        self.warmth_label = QLabel("Warmth: 0.50")
        self.warmth_slider = QSlider(Qt.Orientation.Horizontal)
        self.warmth_slider.setMinimum(0)
        self.warmth_slider.setMaximum(100)
        self.warmth_slider.setValue(50)
        self.warmth_slider.valueChanged.connect(self.update_warmth)

        # Play Button
        self.play_button = QPushButton("Play Sound")
        self.play_button.clicked.connect(self.play_tone)

        # Arrange in layout
        layout.addWidget(self.brightness_label)
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.warmth_label)
        layout.addWidget(self.warmth_slider)
        layout.addWidget(self.play_button)

        self.setLayout(layout)

        # Internal state
        self.brightness = 0.5
        self.warmth = 0.5

    def update_brightness(self, value):
        self.brightness = value / 100.0
        self.brightness_label.setText(f"Brightness: {self.brightness:.2f}")

    def update_warmth(self, value):
        self.warmth = value / 100.0
        self.warmth_label.setText(f"Warmth: {self.warmth:.2f}")

    def play_tone(self):
        tone = generate_synthetic_tone(brightness=self.brightness, warmth=self.warmth)
        sd.play(tone, samplerate=44100)

# === Main Function ===

def main():
    app = QApplication(sys.argv)
    window = ToneSynthApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
