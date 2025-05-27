from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import os

def save_offer_to_pdf(content: str) -> BytesIO:
    font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"  # macOS: Arial Unicode MS
    font_name = "ArialUnicode"

    if not os.path.exists(font_path):
        raise FileNotFoundError("Nie znaleziono czcionki obsługującej polskie znaki.")

    pdfmetrics.registerFont(TTFont(font_name, font_path))

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    textobject = c.beginText(40, height - 50)
    textobject.setFont(font_name, 12)

    for line in content.split('\n'):
        textobject.textLine(line)

    c.drawText(textobject)
    c.save()
    buffer.seek(0)
    return buffer