import os
import csv
import matplotlib.pyplot as plt

def load_fingerprint(file_path):
    """Load fingerprint data from a .fingerprint CSV file into a dict."""
    data = {}
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            if row[0] == "formant_peaks":
                data[row[0]] = [float(f) for f in row[1].split(';')]
            else:
                data[row[0]] = float(row[1])
    return data

def plot_fingerprints(fingerprints, title, save_path):
    """Generate a scatter plot comparing fingerprints."""
    names = []
    honkiness = []
    brightness = []
    attack_sizes = []
    warmth_scores = []  # Formant count < 1500 Hz (proxy for warmth)

    for name, data in fingerprints.items():
        names.append(name)
        honkiness.append(data['mean_flatness'])
        brightness.append(data['mean_centroid'])
        attack_sizes.append(500 * (1 / (1 + data['attack_time'])))  # Faster attack = smaller dot

        # Warmth proxy = formants under 1500 Hz
        warmth_scores.append(sum(1 for f in data['formant_peaks'] if f < 1500))

    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(
        honkiness, brightness,
        s=attack_sizes,
        c=warmth_scores,
        cmap='YlOrRd',
        edgecolor='k', alpha=0.8
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

def analyze_fingerprints(folder):
    """Load all fingerprints, plot two versions: without and with oboe/English horn."""
    fingerprints = {}
    
    # Load all fingerprints into a dict
    for filename in os.listdir(folder):
        if filename.endswith(".fingerprint"):
            name = filename.replace(".fingerprint", "")
            fingerprints[name] = load_fingerprint(os.path.join(folder, filename))
    
    # Separate concertinas and add "oboe" and "englishhorn" only in one plot
    concertinas_only = {k: v for k, v in fingerprints.items() if k not in ["oboe", "englishhorn"]}
    all_instruments = fingerprints.copy()

    # Plot just concertinas
    plot_fingerprints(concertinas_only, "Concertina Timbre Comparison (No Oboe/English Horn)", "comparison_without_oboe.png")

    # Plot concertinas + oboe and English horn
    if "oboe" in fingerprints and "englishhorn" in fingerprints:
        plot_fingerprints(all_instruments, "Concertina vs Oboe and English Horn Comparison", "comparison_with_oboe.png")

# Run the analysis on your folder
if __name__ == "__main__":
    analyze_fingerprints("fingerprints")
