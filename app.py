import os
from flask import Flask, render_template, request, send_file
import pandas as pd
from weasyprint import HTML
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_invoice():
    try:
        file = request.files.get("csv_file")
        if not file:
            return "No CSV uploaded", 400

        df = pd.read_csv(file)

        selected_column = request.form.get("duration_column")
        if selected_column not in df.columns:
            return f"Column '{selected_column}' not found in CSV.", 400

        # Convert selected duration column to numeric
        df["Hours"] = pd.to_numeric(df[selected_column], errors="coerce")
        df["Hours"] = df["Hours"].fillna(0)
        total_hours = round(df["Hours"].sum(), 2)

        html = render_template("invoice_template.html",
                               entries=df.to_dict(orient="records"),
                               total_hours=total_hours)

        pdf_path = os.path.join(UPLOAD_FOLDER, "invoice_preview.pdf")
        HTML(string=html, base_url='.').write_pdf(pdf_path)
        return send_file(pdf_path, mimetype="application/pdf")

    except Exception as e:
        return f"Error generating invoice: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
