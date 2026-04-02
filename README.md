---
title: Data Matrix Scanner
emoji: 🔲
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "6.10.0"
app_file: app.py
pinned: false
license: mit
---

# Data Matrix Barcode Scanner

Scan Data Matrix barcodes directly from your webcam or by uploading an image.

## Usage

1. Allow camera access when prompted (or upload an image)
2. Point at a Data Matrix barcode and capture
3. The decoded text and scan metrics appear instantly
4. Capture again to scan another barcode

## Metrics shown

- Decoded text content
- Barcode format & content type
- Corner positions (TL / TR / BR / BL)
- Orientation angle
- Error correction level (EC level)
- Validity and any error messages
