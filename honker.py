import librosa
import numpy as np
import csv
import os
from scipy.signal import find_peaks
import argparse

def analyze_full_concertina_file(file_path, output_dir="fingerprints", frame_length=2048, hop_length=512):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load audio
    y, sr = librosa.load(file_path, sr=None)

    # Spectral features computed frame-by-frame
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=frame_length, hop_length=hop_length)[0]
    spectral_flatness = librosa.feature.spectral_flatness(y=y, n_fft=frame_length, hop_length=hop_length)[0]

    # Onset/attack detection
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

    # Attack time estimate (first onset to max onset strength within a short window)
    if len(onset_frames) > 0:
        peak_frame = np.argmax(onset_env)
        attack_time = (peak_frame - onset_frames[0]) / sr
    else:
        attack_time = np.nan

    # Aggregate stats across the file
    stats = {
        "mean_centroid": np.mean(spectral_centroid),
        "min_centroid": np.min(spectral_centroid),
        "max_centroid": np.max(spectral_centroid),
        "mean_flatness": np.mean(spectral_flatness),
        "min_flatness": np.min(spectral_flatness),
        "max_flatness": np.max(spectral_flatness),
        "attack_time": attack_time
    }

    # Spectral envelope and formants
    stft = np.abs(librosa.stft(y, n_fft=frame_length, hop_length=hop_length))
    avg_spectrum = np.mean(stft, axis=1)
    freqs = librosa.fft_frequencies(sr=sr)

    avg_spectrum_db = librosa.amplitude_to_db(avg_spectrum)
    peaks, _ = find_peaks(avg_spectrum_db, distance=5)
    formant_freqs = freqs[peaks]

    # Add formant peaks (join into string for CSV)
    stats["formant_peaks"] = ";".join([f"{freq:.2f}" for freq in formant_freqs])

    # Create output file path
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = os.path.join(output_dir, f"{base_name}.fingerprint")

    # Write fingerprint to CSV
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Feature", "Value"])
        for key, value in stats.items():
            writer.writerow([key, value])

    print(f"Fingerprint saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a concertina recording and produce a timbre fingerprint.")
    parser.add_argument("file_path", help="Path to the audio file (mp3, wav, etc.) to analyze.")
    parser.add_argument("--output-dir", default="fingerprints", help="Directory to save fingerprint file.")

    args = parser.parse_args()

    analyze_full_concertina_file(args.file_path, args.output_dir)
