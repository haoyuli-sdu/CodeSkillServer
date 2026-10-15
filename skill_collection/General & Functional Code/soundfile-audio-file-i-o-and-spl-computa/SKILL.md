---
name: soundfile-audio-file-i-o-and-spl-computa
description: 'Guide for soundfile: read/write audio, SPL formula, librosa integration, return types.'
---

# soundfile — Audio File I/O

soundfile reads and writes audio files (WAV, FLAC, OGG, AIFF, and others) without resampling or channel mixing, preserving the file's native format.

## Reading Audio

```python
import soundfile as sf

data, samplerate = sf.read('recording.wav')
# data: float64 ndarray
#   mono   → shape (n_samples,)
#   stereo → shape (n_samples, 2)
# samplerate: int, e.g. 44100
```

## Writing Audio

```python
sf.write('output.wav', data, samplerate)                     # format inferred from extension
sf.write('output.wav', data, samplerate, subtype='PCM_16')   # explicit 16-bit PCM
```

`data` must be a NumPy array. For WAV with float subtypes, values should be in [-1.0, 1.0].

## Computing SPL from Audio

Sound Pressure Level in dB: `20 * log10(sqrt(mean(data^2)))`:

```python
import numpy as np

data, sr = sf.read('audio.wav')
spl = 20 * np.log10(np.sqrt(np.mean(data ** 2)))
```

`np.mean(data ** 2)` averages over all elements — works for both mono (1D) and stereo (2D).

## Common Workflow with librosa

soundfile supplies the raw signal; librosa handles spectral processing:

```python
import soundfile as sf
import librosa
import numpy as np
import matplotlib.pyplot as plt

data, sr = sf.read('audio.wav')
spl = 20 * np.log10(np.sqrt(np.mean(data ** 2)))

# Build and normalise a matrix to SPL
matrix = np.array(values).reshape(M, N).astype(float)
matrix = matrix / np.max(matrix) * spl

# Spectrogram
D = librosa.amplitude_to_db(np.abs(librosa.stft(matrix)), ref=np.max)
librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
fig = plt.gcf()   # Figure, not Axes — specshow uses current plt figure
```

## Return Types

`librosa.display.specshow()` returns an `AxesImage` and draws into the current matplotlib figure as a side effect. Use `plt.gcf()` to get the `Figure`; use `plt.colorbar()` (not `fig.colorbar()`).

## Subtype Reference

| Subtype  | Description          |
|----------|----------------------|
| `PCM_16` | 16-bit integer PCM   |
| `PCM_24` | 24-bit integer PCM   |
| `PCM_32` | 32-bit integer PCM   |
| `FLOAT`  | 32-bit float         |
| `DOUBLE` | 64-bit float         |
