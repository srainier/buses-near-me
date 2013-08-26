from flask import render_template

from app import app


@app.route('/')
def one_page_app():
    return render_template('index.html')
