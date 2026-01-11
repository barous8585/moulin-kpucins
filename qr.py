import qrcode

url = "http://localhost:8502"

img = qrcode.make(url)
img.save("menu_qr.png")

print("QR code généré : menu_qr.png")
