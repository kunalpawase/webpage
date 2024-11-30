from flask import Flask, render_template, request
import os
import time
from PIL import Image
from colorthief import ColorThief
import qrcode

app = Flask(__name__)  # 

UPLOAD_FOLDER = "static/uploads/"

# 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_dominant_colors(image_path, num_colors=3):
    """Extracts dominant colors from the image."""
    color_thief = ColorThief(image_path)
    return color_thief.get_palette(color_count=num_colors)

def create_styled_qr(data, image_path, output_path="static/styled_qr.png"):
    """Generates a styled QR code."""
    colors = extract_dominant_colors(image_path)
    fill_color = colors[0]
    back_color = colors[1] if len(colors) > 1 else "white"
    logo_color = colors[2] if len(colors) > 2 else "black"

    qr = qrcode.QRCode(
        version=6,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    logo = Image.open(image_path).convert("RGBA")
    logo_size = qr_img.size[0] // 5
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

    outline_size = logo_size + 10
    logo_with_outline = Image.new("RGBA", (outline_size, outline_size), logo_color)
    logo_with_outline.paste(logo, ((outline_size - logo_size) // 2, (outline_size - logo_size) // 2), logo)

    pos = ((qr_img.size[0] - outline_size) // 2, (qr_img.size[1] - outline_size) // 2)
    qr_img.paste(logo_with_outline, pos, mask=logo_with_outline)

    qr_img.save(output_path)
    return output_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form["data"]
        image = request.files["image"]
        filename = image.filename
        unique_filename = os.path.join(UPLOAD_FOLDER, f"{int(time.time())}_{filename}")
        image.save(unique_filename)

        qr_path = create_styled_qr(data, unique_filename)
        return render_template("index.html", qr_path=qr_path)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
