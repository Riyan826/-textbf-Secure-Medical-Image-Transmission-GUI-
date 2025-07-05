# secure_image_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os
import zipfile
import math
from collections import Counter

class SecureImageGUI:
    def __init__(self, root):
        self.root = root
        root.title("Secure Medical Image Transmission")
        self.secret_path = ""
        self.cover_path = ""
        self.embedded_path = "embedded.png"
        self.key_data_path = "key_data.npz"
        self.package_path = "secure_package.zip"
        self.create_widgets()

    def create_widgets(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Select Secret Image", command=self.select_secret).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Select Cover Image", command=self.select_cover).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Embed and Encrypt (Sender)", command=self.embed_and_encrypt).grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="Extract and Decrypt (Receiver)", command=self.extract_and_decrypt).grid(row=0, column=3, padx=10)

        tk.Button(btn_frame, text="Load Stego Image", command=self.load_stego_image).grid(row=1, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Load Key Data", command=self.load_key_data).grid(row=1, column=2, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Export Secure ZIP", command=self.export_secure_package).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="View Metrics", command=self.view_metrics).grid(row=2, column=2, columnspan=2, pady=10)

    def select_secret(self):
        self.secret_path = filedialog.askopenfilename(title="Select Secret Image", filetypes=[("Image Files", "*.png *.jpg *.bmp")])

    def select_cover(self):
        self.cover_path = filedialog.askopenfilename(title="Select Cover Image", filetypes=[("Image Files", "*.png *.jpg *.bmp")])

    def load_stego_image(self):
        self.embedded_path = filedialog.askopenfilename(title="Select Stego Image", filetypes=[("PNG Files", "*.png")])

    def load_key_data(self):
        self.key_data_path = filedialog.askopenfilename(title="Select Key Data File", filetypes=[("NPZ Files", "*.npz")])

    def embed_and_encrypt(self):
        if not self.secret_path or not self.cover_path:
            messagebox.showerror("Error", "Please select both secret and cover images.")
            return

        with open(self.secret_path, "rb") as file:
            data = file.read()
        key = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        secret_img = Image.open(self.secret_path)
        cover_img = Image.open(self.cover_path).resize(secret_img.size)

        self.cover_image_np = np.array(cover_img, dtype=np.uint8)  # for metrics later

        cover_data = self.cover_image_np.copy()
        data_bits = np.unpackbits(np.frombuffer(ciphertext, dtype=np.uint8))
        idx = 0
        for i in range(cover_data.shape[0]):
            for j in range(cover_data.shape[1]):
                for k in range(3):
                    if idx < len(data_bits):
                        cover_data[i, j, k] = np.uint8((int(cover_data[i, j, k]) & ~1) | int(data_bits[idx]))
                        idx += 1

        stego_img = Image.fromarray(cover_data)
        stego_img.save(self.embedded_path)

        np.savez(self.key_data_path, key=key, nonce=cipher.nonce, tag=tag, shape=secret_img.size[::-1], bitlen=len(data_bits))
        messagebox.showinfo("Success", "Stego image and key data saved successfully.")

    def export_secure_package(self):
        if not os.path.exists(self.embedded_path) or not os.path.exists(self.key_data_path):
            messagebox.showerror("Error", "Stego image or key data not found.")
            return
        with zipfile.ZipFile(self.package_path, 'w') as zipf:
            zipf.write(self.embedded_path)
            zipf.write(self.key_data_path)
        messagebox.showinfo("Export Complete", f"Secure package exported as '{self.package_path}'.")

    def extract_and_decrypt(self):
        if not os.path.exists(self.embedded_path) or not os.path.exists(self.key_data_path):
            messagebox.showerror("Error", "Missing embedded image or key data.")
            return

        data = np.load(self.key_data_path)
        key, nonce, tag = data['key'].tobytes(), data['nonce'].tobytes(), data['tag'].tobytes()
        shape = tuple(data['shape'])
        bitlen = int(data['bitlen'])

        stego_img = Image.open(self.embedded_path)
        stego_data = np.array(stego_img)

        bits = []
        idx = 0
        for i in range(stego_data.shape[0]):
            for j in range(stego_data.shape[1]):
                for k in range(3):
                    if idx < bitlen:
                        bit = stego_data[i, j, k] & 1
                        bits.append(bit)
                        idx += 1

        ciphertext = np.packbits(bits).tobytes()
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        try:
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            with open("recovered_secret.png", "wb") as f:
                f.write(decrypted)
            messagebox.showinfo("Success", "Secret image extracted and saved as 'recovered_secret.png'.")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {e}")

    def view_metrics(self):
        if not os.path.exists(self.embedded_path) or not hasattr(self, 'cover_image_np'):
            messagebox.showerror("Error", "Metrics unavailable. Run embedding first.")
            return

        stego_data = np.array(Image.open(self.embedded_path))
        mse = np.mean((self.cover_image_np.astype(np.float32) - stego_data.astype(np.float32)) ** 2)
        psnr = 10 * math.log10(255 * 255 / mse) if mse != 0 else float('inf')

        gray = np.array(Image.open(self.embedded_path).convert('L'))
        hist = Counter(gray.flatten())
        total = gray.size
        entropy = -sum((count/total) * math.log2(count/total) for count in hist.values())

        messagebox.showinfo("Image Metrics", f"MSE: {mse:.2f}\nPSNR: {psnr:.2f} dB\nEntropy: {entropy:.4f}")

if __name__ == '__main__':
    root = tk.Tk()
    app = SecureImageGUI(root)
    root.mainloop()