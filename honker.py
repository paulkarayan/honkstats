import argparse
import librosa
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
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
    """Estimate prominent spectral peaks (formants) from average spectrum."""
    spectrum = np.abs(librosa.stft(y, n_fft=2048)).mean(axis=1)
    freqs = librosa.fft_frequencies(sr=sr)

    peaks, _ = find_peaks(spectrum, prominence=0.05)

    peak_freqs = freqs[peaks]
    sorted_peaks = sorted(peak_freqs, key=lambda f: -spectrum[peaks][np.where(peak_freqs == f)[0][0]])

    return sorted_peaks[:n_peaks]

def compute_features_with_bandpass(y, sr, low_freq=0, high_freq=None):
    """Compute spectral features with optional band-limiting after STFT."""
    stft = np.abs(librosa.stft(y))

    # Band-limit the STFT if requested
    freqs = librosa.fft_frequencies(sr=sr)
    if low_freq > 0 or high_freq is not None:
        if high_freq is None:
            high_freq = freqs[-1]
        low_bin = np.where(freqs >= low_freq)[0][0]
        high_bin = np.where(freqs <= high_freq)[0][-1]
        stft = stft[low_bin:high_bin, :]

    # Compute spectral features
    centroid = librosa.feature.spectral_centroid(S=stft, sr=sr)
    flatness = librosa.feature.spectral_flatness(S=stft).mean()

    # Return per-frame centroid + summary values
    return {
        'centroid_curve': centroid.squeeze(),
        'mean_centroid': centroid.mean(),
        'mean_flatness': flatness,
    }

def plot_and_save_centroid_curve(centroid_curve, sr, file_path):
    """Save spectral centroid curve as an image."""
    times = librosa.times_like(centroid_curve, sr=sr)
    plt.figure(figsize=(10, 4))
    plt.plot(times, centroid_curve, label="Spectral Centroid", color="darkorange")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Frequency (Hz)")
    plt.title("Spectral Centroid Curve")
    plt.grid(True)
    plt.legend()

    plt.savefig(file_path, dpi=300)
    plt.close()

# === Main Processing ===

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

    # Bandpass filter
    low_freq, high_freq = 0, None
    if args.bandpass:
        low_freq, high_freq = args.bandpass

    # Compute features
    features = compute_features_with_bandpass(y, sr, low_freq, high_freq)
    features['attack_time'] = compute_attack_time(y, sr)
    features['formant_peaks'] = estimate_formant_peaks(y, sr)

    # Ensure fingerprints directory exists
    os.makedirs("fingerprints", exist_ok=True)

    # Prepare file paths
    base_name = os.path.basename(args.file).replace('.mp3', '')
    fingerprint_file = os.path.join("fingerprints", f"{base_name}.fingerprint")
    centroid_plot_file = os.path.join("fingerprints", f"{base_name}_centroid_curve.png")

    # Save spectral centroid curve plot
    plot_and_save_centroid_curve(features['centroid_curve'], sr, centroid_plot_file)

    print(f"Saved spectral centroid curve plot to {centroid_plot_file}")

    # Print extracted features (summary only)
    print(f"\nExtracted features (bandpass {low_freq}-{high_freq} Hz):")
    for k, v in features.items():
        if k == "centroid_curve":
            continue
        elif isinstance(v, list):
            print(f"{k}: {', '.join(f'{x:.1f}' for x in v)}")
        else:
            print(f"{k}: {v:.2f}")

    # Save features to .fingerprint file
    with open(fingerprint_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['feature', 'value'])
        for key, value in features.items():
            if key == "centroid_curve":
                continue  # Don't save full curve to CSV
            elif isinstance(value, list):
                value = ';'.join(map(str, value))
            writer.writerow([key, value])

    print(f"\nFingerprint saved to {fingerprint_file}")
