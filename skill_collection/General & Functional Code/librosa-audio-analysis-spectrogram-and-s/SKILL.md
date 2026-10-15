---
name: librosa-audio-analysis-spectrogram-and-s
description: 'Guide for librosa: STFT, amplitude_to_db, specshow, SPL calculation, soundfile integration.'
---

# librosa — Audio Analysis and Feature Extraction

librosa operates on NumPy arrays. Audio is typically loaded with `librosa.load()` (resamples to 22050 Hz, mixes to mono) or read with `soundfile.read()` (preserves native sample rate and channel layout).

## Core Workflow

```python
import librosa
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt

# Load preserving original sample rate
data, sr = sf.read('audio.wav')    # data: (n_samples,) mono or (n_samples, ch) stereo

# Spectral analysis
D = librosa.stft(data)             # complex STFT, shape (1+n_fft/2, n_frames)
D_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)  # dB scale, same shape

# Display — modifies the current matplotlib figure
librosa.display.specshow(D_db, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
fig = plt.gcf()   # retrieve figure after specshow + colorbar calls
```

`librosa.display.specshow` draws into the **current** plt figure (similar to `plt.imshow`). Call `plt.gcf()` after specshow and colorbar to obtain the figure object. Use `plt.colorbar()`, not `fig.colorbar()`.

## Sound Pressure Level (SPL) Calculation

SPL in dB: `20 * log10(sqrt(mean(data^2)))`:

```python
spl = 20 * np.log10(np.sqrt(np.mean(data ** 2)))
```

`np.mean(data ** 2)` averages over all samples and channels regardless of shape — works for both mono (1D) and stereo (2D) arrays.

## Normalising a Matrix to SPL

A common pattern: build a 2D matrix from a flat list, then scale it relative to the SPL of an audio file:

```python
M, N = 4, 5
matrix = np.array(values).reshape(M, N).astype(float)
matrix = matrix / np.max(matrix) * spl
```

## API Quick Reference

```
librosa.load(path)                          → (y, sr): float32 1D array, int sample rate
librosa.load(path, sr=None)                 → original sample rate, no resampling
librosa.stft(y)                             → complex (1+n_fft/2, n_frames)
librosa.istft(D)                            → real 1D reconstructed signal
librosa.amplitude_to_db(S, ref=np.max)      → dB ndarray, same shape as S
librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N) → (N, n_frames)
librosa.feature.melspectrogram(y=y, sr=sr)  → (n_mels, n_frames)
librosa.display.specshow(D, sr, ...)        → AxesImage (side-effect on current figure)
plt.gcf()                                   → Figure containing the specshow
```
