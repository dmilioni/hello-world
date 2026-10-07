# hello-world
This is a test repository


My name is Dimitris. I leave in Greece.

## Snapshot Rescue (photo enhancer)

`photo-enhancer/index.html` is a self-contained photo enhancer for low-quality pictures.
Open it in any modern browser; nothing is uploaded, all processing happens locally in a Web Worker.

It diagnoses the photo (noise, softness, color cast, exposure, contrast, size) and picks automatic fixes:

- **Denoise**: edge-preserving guided filter on brightness, plus heavier chroma smoothing along brightness edges
- **Auto levels and color cast removal**: percentile stretch per channel and midtone gray balancing
- **Exposure, shadow lift and clarity** (local contrast)
- **Vibrance and warmth**
- **Upscale** 2× or 4× (Catmull-Rom), followed by a noise-aware unsharp mask

Presets cover old prints, low-light shots and blurry images. A split before/after view and a brightness histogram show the result, and the full-size image saves as JPEG or PNG.
