#!/usr/bin/python3
"""
Flask App that integrates with Rhino-Repo static HTML Template
"""
from flask import Flask, render_template, url_for
from flask_cors import CORS

# flask setup
app = Flask(__name__)
app.url_map.strict_slashes = False
port = 5001
host = '0.0.0.0'


@app.route('/index/')
def index():
    """
    handles request to custom template
    """
    return render_template('index.html')


@app.route('/credent/')
def credent():
    """
    handles request to custom template
    """
    return render_template('credent.html')


@app.route('/done/<repo>')
def done(repo):
    """
    handles request to custom template
    """
    return render_template('done.html', repo=repo)


@app.route('/404/')
def error_404():
    """
    handles request to custom template
    """
    return render_template('404.html')


if __name__ == "__main__":
    """
    MAIN Flask App"""
    app.run(host=host, port=port)
