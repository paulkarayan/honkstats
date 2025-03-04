import os
import csv
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def load_fingerprint(file_path):
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

# I DONT USE === Z-Score Normalization ===
def zscore_normalize(fingerprints):
    df = pd.DataFrame(fingerprints).T
    numerical_cols = ['mean_centroid', 'mean_flatness', 'attack_time']
    df[numerical_cols] = (df[numerical_cols] - df[numerical_cols].mean()) / df[numerical_cols].std()
    return df.to_dict(orient='index')


def plot_fingerprints(fingerprints, title, save_path, normalization_steps=None):
    names, honkiness, brightness, attack_sizes, warmth_scores = [], [], [], [], []

    for name, data in fingerprints.items():
        names.append(name)
        honkiness.append(data['mean_flatness'])
        brightness.append(data['mean_centroid'])
        warmth_scores.append(sum(1 for f in data['formant_peaks'] if f < 1500))


        if 'attack_time' in data:
            attack_sizes.append(500 * (1 / (1 + data['attack_time'])))
        else:
            attack_sizes.append(100)  # Default size if attack_time is missing


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
    
    full_title = title
    if normalization_steps:
        full_title += f" [{', '.join(normalization_steps)}]"
    plt.title(full_title)

    plt.grid(True)
    plt.savefig(save_path, dpi=300)
    plt.show()


def analyze_fingerprints(folder, zscore):
    fingerprints = {}

    for filename in os.listdir(folder):
        if filename.endswith(".fingerprint"):
            name = filename.replace(".fingerprint", "")
            fingerprints[name] = load_fingerprint(os.path.join(folder, filename))

    # Separate regular concertinas and add oboe/englishhorn only in the second plot
    concertinas_only = {k: v for k, v in fingerprints.items() if k not in ["oboe", "englishhorn"]}
    all_instruments = fingerprints.copy()

    normalization_steps = []
    if zscore:
        normalization_steps.append("Z-score")

    # === First Plot: Concertinas Only ===
    if zscore:
        concertinas_only = zscore_normalize(concertinas_only)
    plot_fingerprints(
        concertinas_only,
        "Concertina Timbre Comparison (No Oboe/English Horn)",
        "comparison_without_oboe.png",
        normalization_steps
    )

    # === Second Plot: Concertinas + Oboe + English Horn ===
    if "oboe" in fingerprints and "englishhorn" in fingerprints:
        if zscore:
            all_instruments = zscore_normalize(all_instruments)
        plot_fingerprints(
            all_instruments,
            "Concertina vs Oboe & English Horn Comparison",
            "comparison_with_oboe.png",
            normalization_steps
        )
    else:
        print("Skipping 'with oboe' plot — oboe and/or englishhorn fingerprints not found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze and plot concertina fingerprints from a folder.")
    parser.add_argument("--folder", default="fingerprints", help="Folder containing .fingerprint files.")
    parser.add_argument("--zscore", action="store_true", help="Apply Z-score normalization to fingerprints.")
    args = parser.parse_args()

    analyze_fingerprints(args.folder, zscore=args.zscore)
