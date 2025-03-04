# honker

## stuff

from what i can derive online, here are a few ways we can do comparisons spectrally of instruments.

### Metric Definitions

| Metric              | What It Tells You                                                                                      |
|---------------------|-------------------------------------------------------------------------------------------------------|
| Spectral Centroid   | Brightness of the sound over time. Higher = brighter/honkier, lower = warmer.                         |
| Spectral Flatness   | How noise-like vs pure the sound is. Higher = more noise-like/honky.                                  |
| Attack Time         | Time between initial onset and peak — shorter is more responsive.                                      |
| Formant Frequencies | Areas with lots of energy (can indicate timbre tendencies like honkiness or woodiness).                |

---

### Example Output

| Metric                     | Value                              |
|----------------------------|------------------------------------|
| Spectral Centroid (average) | 1420.56 Hz                        |
| Spectral Flatness (average) | 0.274                             |
| Estimated Attack Time       | 0.045 seconds                     |
| Formant-like peaks (Hz)     | [450, 910, 1400]                  |

| Interpretation | Notes                                                                                                      |
|----------------|-----------------------------------------------------------------------------------------------------------|
| Brightness     | Centroid around 1400 Hz — somewhat bright.                                                                |
| Purity         | Flatness ~0.27 — moderately pure.                                                                         |
| Responsiveness | Attack time ~45 milliseconds — pretty fast (snappy reed).                                                 |
| Timbre Hints   | Formants around 450 Hz and 910 Hz, which is close to that English Horn lower-mid warmth zone.             |



### honker usage

```
python honker.py "recordings/Thomas - hornpipes.mp3"
python honker.py "recordings/marymac.mp3" # not sure what kind this is but its beautiful

for file in recordings/*.mp3; do
    python honker.py "$file" --bandpass 200 3000 --normalize-loudness --spectral-whitening
done


for file in recordings/*.mp3; do
    filename=$(basename -- "$file")
    fingerprint_file="fingerprints/${filename%.mp3}.fingerprint"

    if [ -f "$fingerprint_file" ]; then
        echo "Skipping $file — fingerprint already exists."
    else
        echo "Processing $file..."
        python analyze_concertina.py "$file"
    fi
done
```


### finger.py usage

python finger.py



### Inger.py Visualization Mapping

| Axis/Attribute   | Meaning                                                                                              |
|------------------|-----------------------------------------------------------------------------------------------------|
| X-axis           | Mean Flatness (Honkiness) — higher values = honkier.                                                |
| Y-axis           | Mean Centroid (Brightness) — higher values = brighter.                                              |
| Point Size       | Attack Speed — faster attack = smaller dots.                                                         |
| Point Color      | Warmth Score — how many formants live under 1500 Hz (lower-mid warmth).                             |
