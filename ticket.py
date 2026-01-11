from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generate_ticket(details, total):
    filename = f"ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join("tickets", filename)

    os.makedirs("tickets", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=A6)
    width, height = A6

    y = height - 20

    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, y, "LE MOULIN DES K'PUCINS")
    y -= 15

    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, y, "Boulangerie artisanale - Angers")
    y -= 20

    c.drawString(10, y, f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 15

    c.drawString(10, y, "Détails :")
    y -= 10

    for line in details.split(","):
        c.drawString(15, y, f"- {line.strip()}")
        y -= 10

    y -= 10
    c.setFont("Helvetica-Bold", 9)
    c.drawString(10, y, f"TOTAL : {total:.2f} €")

    y -= 20
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2, y, "Merci et à bientôt ! 🥖")

    c.showPage()
    c.save()

    return filepath
