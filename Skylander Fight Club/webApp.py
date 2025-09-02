from flask import Flask, render_template, request, redirect, url_for, session
import users

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        if users.validate_user(username, pin):
            session["username"] = username
            return redirect(url_for("welcome"))
        else:
            error = "Incorrect username or PIN."
    return render_template("login.html", error=error)

@app.route("/welcome")
def welcome():
    if "username" not in session:
        return redirect(url_for("login"))
    
    data = users.load_users()
    username = session["username"]
    user_data = data[username]
    
    return render_template(
        "welcome.html", 
        username=username,
        skylander=user_data.get("skylander")
    )

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        skylander = request.form["skylander"]
        if users.add_user(username, pin, skylander):
            return redirect(url_for("login"))
        else:
            return render_template("add_user.html", error="Username already exists")
    return render_template("add_user.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
