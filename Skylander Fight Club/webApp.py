from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import users


app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions
socketio = SocketIO(app)
games = {"quiplash": {"running": False}}

print("HELLO WORLD")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]

        if users.valid_user(username, pin):
            session["username"] = username
            return redirect(url_for("welcome"))
        else:
            return render_template("login.html", error="Invalid username or pin")
    return render_template("login.html")


@app.route("/welcome")
def welcome():
    if "username" not in session:
        return redirect(url_for("login"))
    
    data = users.load_users()
    username = session["username"]
    user_data = data[username]
    skylander = user_data.get("skylander")
    
    # get quiplash state
    is_quiplash_running = games.get("quiplash", {}).get("running", False)
    
    return render_template(
        "welcome.html", 
        username=username,
        skylander=skylander,
        games=games,
        is_quiplash_running=is_quiplash_running
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
    return render_template("login.html")


#Game Functions
@app.route("/start_game/<game_type>")
def start_game(game_type):
    # check if game already running
    if games.get(game_type, {}).get("running"):
        return redirect(url_for("lobby", game_name=game_type))

    # otherwise start it
    games[game_type] = {"running": True, "players": []}
    socketio.emit("game_update", {"game": game_type, "running": True})
    return redirect(url_for("lobby", game_name=game_type))


@app.route("/lobby/<game_name>")
def lobby(game_name):
    return render_template("lobby.html", game=game_name)

@app.route("/join_game/<int:game_id>")
def join_game(game_id):
    game = games.get(game_id)
    if not game:
        return "Game not found", 404
    # For now just add a fake player
    game["players"].append(f"Player{len(game['players'])+1}")
    return redirect(url_for("lobby", game_id=game_id))

@app.route("/stop_game/<game_type>")
def stop_game(game_type):
    if game_type not in ["quiplash", "trivia"]:
        return "Game not found", 404
    
    # mark it as stopped
    games[game_type] = {"running": False}

    # notify all clients
    socketio.emit("game_update", {"game": game_type, "running": False})
    
    
    return redirect(url_for("welcome"))

#debugging:
@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on("game_update")
def handle_game_update(data):
    print(f"Received game_update: {data}")



if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=5000)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
