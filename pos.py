
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('pos.html')


if __name__ == '__main__':
    app.run(debug=True)