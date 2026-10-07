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
- **Deblur**: Richardson-Lucy deconvolution (accelerated) for out-of-focus blur or camera shake. Blur size, shake length and shake direction are measured from the photo; the number of iterations adapts to its noise so grain is not amplified
- **Upscale** 2×, 3× or 4×: Lanczos interpolation plus iterative back-projection ("Recover detail"), followed by a noise-aware unsharp mask

Presets cover old prints, low-light shots, out-of-focus and shaky photos. A split before/after view and a brightness histogram show the result.

Add several photos at once (pick, drop or paste them). Each one is diagnosed separately and keeps its own settings in the photo strip. Save the current photo at full size as JPEG or PNG, or save all of them in one `.zip`.
