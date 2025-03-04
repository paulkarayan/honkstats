# honker



## usage
```
python honker.py "recordings/Thomas - hornpipes.mp3"
```
## stuff

Metric	What It Tells You
Spectral Centroid	Brightness of the sound over time. Higher = brighter/honkier, lower = warmer.
Spectral Flatness	How noise-like vs pure the sound is. Higher = more noise-like/honky.
Attack Time	Time between initial onset and peak — shorter is more responsive.
Formant Frequencies	Areas with lots of energy (can indicate timbre tendencies like honkiness or woodiness).


Output Example
```
Spectral Centroid (average): 1420.56 Hz
Spectral Flatness (average): 0.274
Estimated Attack Time: 0.045 seconds
Formant-like peaks (Hz): [ 450.  910. 1400.]
```

This might indicate:
Centroid around 1400 Hz — somewhat bright.
Flatness ~0.27 — moderately pure.
Attack time ~45 milliseconds — pretty fast (snappy reed).
Formants around 450 Hz and 910 Hz, which is close to that English Horn lower-mid warmth zone.

## What You Could Do Next
- Analyze a set of samples from different concertinas.
- Plot Spectral Centroid vs Flatness on a scatter plot to map your "honky" vs "smooth" spectrum.
- Use Formant position vs Centroid to find instruments that live closer to your ideal "English Horn" tone.
- Build a database of your instruments with these timbre fingerprints!


###

python honker.py "recordings/Thomas - hornpipes.mp3"
python honker.py "recordings/marymac.mp3" # not sure what kind this is but its beautiful
python honker.py "recordings/carroll-noelhill.mp3" 

for file in recordings/*.mp3; do
    python honker.py "$file"
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


### finger.py

X-axis	Mean Flatness (Honkiness) — higher values = honkier.
Y-axis	Mean Centroid (Brightness) — higher values = brighter.
Point Size	Attack Speed — faster attack = smaller dots.
Point Color	Warmth Score — how many formants live under 1500 Hz (lower-mid warmth).
