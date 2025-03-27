from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
import user_management as dbHandler

import bleach
import re 

import hashlib

import html

from flask_wtf.csrf import CSRFProtect

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import hmac

import time

csrf = CSRFProtect()

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)



@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if request.method == "GET" and request.args.get("url"):

        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        # Input Sanitization + XSS Prevention
        feedback = bleach.clean(html.escape(request.form["feedback"].strip()))
        # Input Validation
        # Side-channel attacks
        valid_feedback = True
        for char in feedback:
            if not re.match(r"^[a-zA-Z0-9 .,!?]*$", char): 
                valid_feedback = False
        # Error Handling
        if not valid_feedback:
            time.sleep(0.1)
            return f"An error occurred.", 400
        try:
            dbHandler.insertFeedback(feedback)
        except Exception as e:
            time.sleep(0.1)
            return f"An error occurred.", 400 
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        # Hashing
        password = hashlib.sha256(password.encode()).hexdigest()
        dbHandler.insertUser(username, password, DoB)
        return render_template("/index.html")
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            dbHandler.listFeedback()
            return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")
    else:
        return render_template("/index.html")


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)
