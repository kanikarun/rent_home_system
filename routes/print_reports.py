from flask import Flask, render_template
from datetime import datetime
from app import app

@app.get('/print-reports')
def print_reports():
    """
    Printable reports page.
    Data will be fetched dynamically via JS from your existing /api/reports/* endpoints.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # or just "%Y-%m-%d"
    return render_template('print-reports.html', now=now)
