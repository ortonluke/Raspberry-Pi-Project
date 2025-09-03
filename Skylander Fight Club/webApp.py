from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import users


app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions
socketio = SocketIO(app)
games = {"quiplash": {"running": False}}

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
    
    data = users.load_users()
    username = session["username"]
    user_data = data[username]
    
    return render_template(
        "welcome.html", 
        username=username,
        skylander=user_data.get("skylander"),
        games=games
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


#Game Functions
@app.route("/start_game/<game_type>")
def start_game(game_type):
    if game_type not in games:
        return "Game not found", 404
    games[game_type]["running"] = True
    
    #notify all clients that the game started
    socketio.emit("game_update", {"game": game_type, "running": True})
    return f"{game_type} started!"

@app.route("/lobby/<game_name>")
def lobby(game_name):
    # check if this game exists
    if game_name not in games:
        return "Game not found", 404
    game_running = games[game_name]["running"]
    return render_template("lobby.html", game_name=game_name, game_running=game_running)

@app.route("/join_game/<int:game_id>")
def join_game(game_id):
    game = games.get(game_id)
    if not game:
        return "Game not found", 404
    # For now just add a fake player
    game["players"].append(f"Player{len(game['players'])+1}")
    return redirect(url_for("lobby", game_id=game_id))

if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=5000)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
