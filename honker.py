import argparse
import librosa
import numpy as np
import csv
import os
from scipy.signal import find_peaks

# === Normalization Functions ===

def normalize_loudness(y):
    """Normalize audio to consistent RMS level."""
    rms = np.sqrt(np.mean(y**2))
    return y / (rms + 1e-9)

def spectral_whitening(y, sr, n_fft=2048):
    """Flatten spectral envelope to remove recording bias."""
    stft = librosa.stft(y, n_fft=n_fft)
    magnitudes = np.abs(stft)
    spectral_mean = np.mean(magnitudes, axis=1, keepdims=True)
    whitened = magnitudes / (spectral_mean + 1e-9)
    return librosa.istft(whitened * np.exp(1j * np.angle(stft)))

# === Feature Computation Functions ===

def compute_attack_time(y, sr):
    """Simple onset-based attack time estimation."""
    envelope = librosa.onset.onset_strength(y=y, sr=sr)
    peak_idx = np.argmax(envelope > (0.5 * np.max(envelope)))
    return peak_idx / sr  # Convert to seconds

def estimate_formant_peaks(y, sr, n_peaks=5):
    """
    Estimate prominent spectral peaks (formants) from an audio signal.
    This is a rough proxy, not actual LPC formants.
    """
    spectrum = np.abs(librosa.stft(y, n_fft=2048)).mean(axis=1)
    freqs = librosa.fft_frequencies(sr=sr)

    peaks, _ = find_peaks(spectrum, prominence=0.05)

    # Get the top `n_peaks` peaks sorted by magnitude (most prominent first)
    peak_freqs = freqs[peaks]
    sorted_peaks = sorted(peak_freqs, key=lambda f: -spectrum[peaks][np.where(peak_freqs == f)[0][0]])

    return sorted_peaks[:n_peaks]

def compute_features_with_bandpass(y, sr, low_freq=0, high_freq=None):
    """Compute spectral features with optional band-limiting after STFT."""
    stft = np.abs(librosa.stft(y))

    # Band-limit the STFT if desired
    freqs = librosa.fft_frequencies(sr=sr)
    if low_freq > 0 or high_freq is not None:
        if high_freq is None:
            high_freq = freqs[-1]
        low_bin = np.where(freqs >= low_freq)[0][0]
        high_bin = np.where(freqs <= high_freq)[0][-1]
        stft = stft[low_bin:high_bin, :]

    centroid = librosa.feature.spectral_centroid(S=stft, sr=sr).mean()
    flatness = librosa.feature.spectral_flatness(S=stft).mean()

    return {
        'mean_centroid': centroid,
        'mean_flatness': flatness,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze concertina audio and extract timbre features.")
    parser.add_argument("file", help="Audio file to analyze.")
    parser.add_argument("--bandpass", nargs=2, type=float, metavar=('LOW', 'HIGH'),
                        help="Optional bandpass filter (low and high cutoff frequencies in Hz).")
    parser.add_argument("--normalize-loudness", action="store_true",
                        help="Apply RMS loudness normalization before analysis.")
    parser.add_argument("--spectral-whitening", action="store_true",
                        help="Apply spectral whitening before analysis.")

    args = parser.parse_args()

    y, sr = librosa.load(args.file, sr=None)

    # Apply optional normalizations
    if args.normalize_loudness:
        y = normalize_loudness(y)
        print("Applied loudness normalization.")

    if args.spectral_whitening:
        y = spectral_whitening(y, sr)
        print("Applied spectral whitening.")

    # Bandpass processing
    low_freq, high_freq = 0, None
    if args.bandpass:
        low_freq, high_freq = args.bandpass

    features = compute_features_with_bandpass(y, sr, low_freq, high_freq)
    features['attack_time'] = compute_attack_time(y, sr)
    features['formant_peaks'] = estimate_formant_peaks(y, sr)

    print(f"\nExtracted features (bandpass {low_freq}-{high_freq} Hz):")
    for k, v in features.items():
        if isinstance(v, list):
            print(f"{k}: {', '.join(f'{x:.1f}' for x in v)}")
        else:
            print(f"{k}: {v:.2f}")

    os.makedirs("fingerprints", exist_ok=True)
    basename = os.path.basename(args.file).replace('.mp3', '.fingerprint')
    fingerprint_file = os.path.join("fingerprints", basename)

    with open(fingerprint_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['feature', 'value'])
        for key, value in features.items():
            if isinstance(value, list):
                value = ';'.join(map(str, value))  # formants as "x;y;z"
            writer.writerow([key, value])

    print(f"\nFingerprint saved to {fingerprint_file}")
