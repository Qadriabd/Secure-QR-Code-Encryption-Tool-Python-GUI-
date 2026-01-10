import customtkinter as ctk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
import qrcode
from PIL import Image
import cv2
import os

ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue")  

class SecureQRVault(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SecureQR Vault")
        self.geometry("1000x700")
        self.resizable(True, True)

        self.key = None
        self.encrypted_text = None
        self.generated_qr_image = None
        self.imported_qr_image = None

        self.build_ui()
        self.add_copyright()

    def build_ui(self):
        title = ctk.CTkLabel(
            self,
            text="SecureQR Vault",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#ff3399"  # Pink accent
        )
        title.pack(pady=15)

        container = ctk.CTkFrame(self, corner_radius=20)
        container.pack(padx=20, pady=10, fill="both", expand=True)

        left = ctk.CTkFrame(container, corner_radius=20)
        left.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        right = ctk.CTkFrame(container, corner_radius=20)
        right.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        # --- Encryption Section ---
        ctk.CTkLabel(left, text="Encrypt Text", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        self.plain_input = ctk.CTkTextbox(left, height=100)
        self.plain_input.pack(padx=10, pady=10, fill="x")

        self.encrypt_btn = ctk.CTkButton(left, text="Encrypt & Generate QR", fg_color="#ff3399",
                                         hover_color="#ff66aa", command=self.encrypt_text)
        self.encrypt_btn.pack(pady=10)

        self.key_output = ctk.CTkEntry(left, placeholder_text="Encryption Key")
        self.key_output.pack(padx=10, pady=10, fill="x")

        self.qr_label_generated = ctk.CTkLabel(left, text="")
        self.qr_label_generated.pack(pady=10)

        self.save_qr_btn = ctk.CTkButton(left, text="Save QR Code", fg_color="#ff3399",
                                         hover_color="#ff66aa", command=self.save_generated_qr)
        self.save_qr_btn.pack(pady=5)

        # --- Decryption Section ---
        ctk.CTkLabel(right, text="Decrypt from QR", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.select_qr_btn = ctk.CTkButton(right, text="Import QR Image", fg_color="#ff3399",
                                          hover_color="#ff66aa", command=self.load_qr)
        self.select_qr_btn.pack(pady=10)

        self.encrypted_output = ctk.CTkTextbox(right, height=80)
        self.encrypted_output.pack(padx=10, pady=10, fill="x")

        self.decrypt_key_input = ctk.CTkEntry(right, placeholder_text="Paste Encryption Key")
        self.decrypt_key_input.pack(padx=10, pady=10, fill="x")

        self.decrypt_btn = ctk.CTkButton(right, text="Decrypt", fg_color="#ff3399",
                                         hover_color="#ff66aa", command=self.decrypt_text)
        self.decrypt_btn.pack(pady=10)

        self.result_output = ctk.CTkTextbox(right, height=100)
        self.result_output.pack(padx=10, pady=10, fill="x")

        self.qr_label_imported = ctk.CTkLabel(right, text="")
        self.qr_label_imported.pack(pady=10)

    # --- Encryption ---
    def encrypt_text(self):
        text = self.plain_input.get("1.0", "end").strip()
        if not text:
            messagebox.showerror("Error", "Please enter text to encrypt.")
            return

        self.key = Fernet.generate_key()
        cipher = Fernet(self.key)
        self.encrypted_text = cipher.encrypt(text.encode()).decode()

        self.key_output.delete(0, "end")
        self.key_output.insert(0, self.key.decode())

        # Generate QR
        qr = qrcode.make(self.encrypted_text)
        qr_path = "generated_qr.png"
        qr.save(qr_path)
        self.generated_qr_image = Image.open(qr_path)

        # Display QR in UI
        img = ctk.CTkImage(self.generated_qr_image, size=(180, 180))
        self.qr_label_generated.configure(image=img)
        self.qr_label_generated.image = img

        messagebox.showinfo("Success", "QR Code generated successfully!")

    # --- Save Generated QR ---
    def save_generated_qr(self):
        if not self.generated_qr_image:
            messagebox.showerror("Error", "No QR code to save.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png")]
        )
        if path:
            self.generated_qr_image.save(path)
            messagebox.showinfo("Saved", f"QR Code saved at {path}")

    # --- Import QR ---
    def load_qr(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return

        # Decode QR using OpenCV
        detector = cv2.QRCodeDetector()
        image = cv2.imread(file_path)
        data, _, _ = detector.detectAndDecode(image)

        if not data:
            messagebox.showerror("Error", "No QR code detected in this image.")
            return

        self.imported_qr_image = Image.open(file_path)

        self.encrypted_output.delete("1.0", "end")
        self.encrypted_output.insert("1.0", data)

        # Show imported QR in UI
        img = ctk.CTkImage(self.imported_qr_image, size=(180, 180))
        self.qr_label_imported.configure(image=img)
        self.qr_label_imported.image = img

    # --- Decrypt ---
    def decrypt_text(self):
        encrypted = self.encrypted_output.get("1.0", "end").strip()
        key = self.decrypt_key_input.get().strip()

        if not encrypted or not key:
            messagebox.showerror("Error", "Encrypted text and key are required.")
            return

        try:
            cipher = Fernet(key.encode())
            decrypted = cipher.decrypt(encrypted.encode()).decode()

            self.result_output.delete("1.0", "end")
            self.result_output.insert("1.0", decrypted)

        except Exception:
            messagebox.showerror("Error", "Invalid key or corrupted data.")

    # --- Copyright ---
    def add_copyright(self):
        copyright_label = ctk.CTkLabel(
            self,
            text="© 2025 SecureQR Vault by Esraa Codes. All rights reserved.",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        copyright_label.pack(side="bottom", pady=5)


if __name__ == "__main__":
    app = SecureQRVault()
    app.mainloop()
