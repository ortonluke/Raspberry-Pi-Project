from flask import Flask, render_template, request, redirect, url_for, session
import users


app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        if users.valid_user(username):
            session["username"] = username
            return redirect(url_for("welcome"))
        else:
            return render_template("login.html", error="Invalid username")
    return render_template("login.html")


@app.route("/welcome")
def welcome():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("welcome.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
