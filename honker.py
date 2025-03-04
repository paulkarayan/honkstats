import os
import csv
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def load_fingerprint(file_path):
    """Load a .fingerprint CSV file into a dict."""
    data = {}
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            if row[0] == "formant_peaks":
                data[row[0]] = [float(f) for f in row[1].split(';')]
            else:
                data[row[0]] = float(row[1])
    return data

def zscore_normalize(fingerprints):
    """Apply Z-score normalization to all numeric columns in fingerprints."""
    df = pd.DataFrame(fingerprints).T
    numerical_cols = ['mean_centroid', 'mean_flatness', 'attack_time']

    # Apply Z-score normalization
    df[numerical_cols] = (df[numerical_cols] - df[numerical_cols].mean()) / df[numerical_cols].std()

    return df.to_dict(orient='index')

def plot_fingerprints(fingerprints, title, save_path):
    """Create scatter plot comparing honkiness, brightness, and warmth for all instruments."""
    names = []
    honkiness = []
    brightness = []
    attack_sizes = []
    warmth_scores = []  # Number of formants under 1500 Hz (proxy for warmth)

    for name, data in fingerprints.items():
        names.append(name)
        honkiness.append(data['mean_flatness'])
        brightness.append(data['mean_centroid'])
        attack_sizes.append(500 * (1 / (1 + data['attack_time'])))  # Faster attack = smaller dot

        # Warmth proxy = formant count < 1500 Hz
        warmth_scores.append(sum(1 for f in data['formant_peaks'] if f < 1500))

    plt.figure(figsize=(12, 8))

    scatter = plt.scatter(
        honkiness, brightness, 
        s=attack_sizes, 
        c=warmth_scores, 
        cmap='YlOrRd', 
        edgecolor='k', 
        alpha=0.85
    )

    plt.colorbar(scatter, label="Warmth Score (Formants < 1500 Hz)")

    for i, name in enumerate(names):
        plt.annotate(name, (honkiness[i], brightness[i]), fontsize=9, ha='right', va='bottom')

    plt.xlabel("Honkiness (Spectral Flatness)")
    plt.ylabel("Brightness (Spectral Centroid in Hz)")
    plt.title(title)
    plt.grid(True)

    plt.savefig(save_path, dpi=300)
    plt.show()

def analyze_fingerprints(folder, zscore):
    """Load all fingerprints from folder and produce comparison plot."""
    fingerprints = {}

    # Load all fingerprints into a dictionary
    for filename in os.listdir(folder):
        if filename.endswith(".fingerprint"):
            name = filename.replace(".fingerprint", "")
            fingerprints[name] = load_fingerprint(os.path.join(folder, filename))

    if zscore:
        fingerprints = zscore_normalize(fingerprints)
        plot_fingerprints(fingerprints, "Z-Score Normalized Concertina Timbre Comparison", "comparison_zscore.png")
    else:
        plot_fingerprints(fingerprints, "Raw Concertina Timbre Comparison", "comparison_raw.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze and plot concertina fingerprints from a folder.")
    parser.add_argument("folder", help="Folder containing .fingerprint files.")
    parser.add_argument("--zscore", action="store_true", help="Apply Z-score normalization to fingerprints.")

    args = parser.parse_args()

    analyze_fingerprints(args.folder, zscore=args.zscore)
