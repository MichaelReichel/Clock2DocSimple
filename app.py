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

        # Get user-selected column names
        duration_column = request.form.get("duration_column")
        date_column = request.form.get("date_column")

        # Convert duration to hours
        df["Hours"] = pd.to_timedelta(df[duration_column], errors="coerce").dt.total_seconds() / 3600

        # Clean date - keep only day from date column
        df["Date"] = pd.to_datetime(df[date_column], errors="coerce").dt.day.astype("Int64")

        # Prepare total hours
        total_hours = df["Hours"].sum()

        html = render_template("invoice_template.html", entries=df.to_dict(orient="records"), total_hours=f"{total_hours:.2f}")
        pdf_path = os.path.join(UPLOAD_FOLDER, "invoice_preview.pdf")
        HTML(string=html).write_pdf(pdf_path)
        return send_file(pdf_path, mimetype="application/pdf")

    except Exception as e:
        return f"Error generating invoice: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
