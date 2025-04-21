import os
from flask import Flask, render_template, request, send_file
import pandas as pd
from weasyprint import HTML
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_invoice():
    try:
        file = request.files["csv_file"]
        if not file:
            return "No CSV uploaded", 400

        df = pd.read_csv(file)

        duration_column = request.form.get("duration_column")
        date_column = request.form.get("date_column")
        bank_details = request.form.get("bank_details", "").replace("\r\n", "<br>").replace("\n", "<br>")

        if duration_column not in df.columns:
            return "Invalid duration column", 400
        if date_column not in df.columns:
            return "Invalid date column", 400

        df["Hours"] = pd.to_numeric(df[duration_column], errors="coerce")

        df["Day"] = pd.to_datetime(df[date_column], errors="coerce").dt.day

        hourly_rate = float(request.form.get("hourly_rate", 0))
        df["Amount"] = df["Hours"] * hourly_rate
        total_amount = df["Amount"].sum()
        date_str = datetime.today().strftime("%Y-%m-%d")

        business = request.form.get("business_name", "")
        invoice_number = request.form.get("invoice_number", "")

        logo_path = ""
        if "logo_file" in request.files and request.files["logo_file"].filename != "":
            logo = request.files["logo_file"]
            logo_filename = secure_filename(logo.filename)
            logo_path = os.path.join(UPLOAD_FOLDER, logo_filename)
            logo.save(logo_path)

        html = render_template("invoice_template.html",
                               business=business,
                               invoice_number=invoice_number,
                               date_str=date_str,
                               entries=df.to_dict(orient="records"),
                               total="{:.2f}".format(total_amount),
                               logo_path=logo_path,
                               bank_details=bank_details)

        pdf_path = os.path.join(UPLOAD_FOLDER, "invoice_preview.pdf")
        HTML(string=html).write_pdf(pdf_path)
        return send_file(pdf_path, mimetype="application/pdf")

    except Exception as e:
        return f"Error generating invoice: {e}", 500

@app.route("/download", methods=["POST"])
def download_invoice():
    return upload_invoice()

if __name__ == "__main__":
    app.run(debug=True)
