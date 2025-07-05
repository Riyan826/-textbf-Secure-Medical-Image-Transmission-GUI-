
# Secure Medical Image Transmission GUI

A Python-based GUI application for securely transmitting medical images using AES encryption and LSB steganography. This tool provides both embedding (sender) and extraction (receiver) functionality along with image quality metrics such as MSE, PSNR, and Entropy.

## 🛡️ Features

- 🔒 **AES Encryption**: Ensures confidentiality of the secret image.
- 🖼️ **LSB Steganography**: Hides the encrypted data within a cover image.
- 📦 **Secure Packaging**: Export encrypted image and keys as a ZIP archive.
- 📊 **Quality Metrics**: Calculates MSE, PSNR, and Entropy of the stego image.
- 🧠 **User-Friendly GUI**: Intuitive interface built using Tkinter.

## 📸 How It Works

### Sender Side (Embed & Encrypt):
1. Select a secret image and a cover image.
2. The secret image is AES-encrypted.
3. The encrypted bytes are embedded into the LSB of the cover image.
4. A stego image (`embedded.png`) is generated along with key data (`key_data.npz`).
5. Optionally, both can be packaged into a `secure_package.zip`.

### Receiver Side (Extract & Decrypt):
1. Load the stego image and key data.
2. Extract encrypted bits from the image.
3. Decrypt using AES to recover the original secret image.

## 🚀 Installation

### Requirements

- Python 3.x
- Required libraries:
  ```bash
  pip install pillow pycryptodome numpy
  ```

### Run the App

```bash
python new_gui1.py
```

## 📂 File Structure

```
📦 SecureMedicalImageGUI
 ┣ 📜 new_gui1.py
 ┣ 📁 outputs/
 ┃ ┣ embedded.png
 ┃ ┣ key_data.npz
 ┃ ┗ recovered_secret.png
 ┗ 📦 secure_package.zip
```

## 🧪 Example Use Cases

- Secure telemedicine transmission.
- Confidential image sharing.
- Research on steganographic techniques.

## 📊 Metrics Explained

- **MSE (Mean Squared Error)**: Measures distortion between original and stego image.
- **PSNR (Peak Signal-to-Noise Ratio)**: Indicates quality of the stego image.
- **Entropy**: Reflects the randomness of pixel intensity for security analysis.

## 📘 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

Made with ❤️ by [Mohd Riyan](mailto:riyanmohammed826@gmail.com)
