from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import users
import quiplash


app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions
socketio = SocketIO(app)
games = {"quiplash": {"running": False}}

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
    return render_template("add_user.html")


#Game Functions
@app.route("/start_game/<game_type>")
def start_game(game_type):
    # check if game already running
    if games.get(game_type, {}).get("running"):
        return redirect(url_for("lobby", game_name=game_type))

    # otherwise start it
    games[game_type] = {"running": True, "players": []}
    socketio.emit("game_update", {"game": game_type, "running": True})
    start_quiplash()
    return redirect(url_for("lobby", game_name=game_type))

def start_quiplash():
    players = users.load_users()  # from users.json
    games["quiplash"]["players"] = {u: {"score": 0} for u in players}
    games["quiplash"]["pairings"] = quiplash.generate_pairings(players)
    games["quiplash"]["phase"] = "answering"
    
    print(games["quiplash"]["pairings"])

@app.route("/start_voting/<game_type>")
def start_voting(game_type):
    game = games.get(game_type)
    if game and game.get("running"):
        game["phase"] = "voting"
    return redirect(url_for("lobby", game_name=game_type))

##@app.route("/vote/<game_type>", methods=["GET", "POST"])
"""
def vote(game_type):
    username = session.get("username")
    game = games.get(game_type)

    if not game or game.get("phase") != "voting":
        return redirect(url_for("lobby", game_name=game_type))

    # Find the next pairing the user needs to vote on
    for i, pairing in enumerate(game["pairings"]):
        if username not in pairing["players"]:  # can't vote on your own
            if username not in pairing["votes"]:
                if request.method == "POST":
                    choice = request.form["choice"]
                    pairing["votes"][username] = choice
                    return redirect(url_for("vote", game_type=game_type))
                return render_template("vote.html", pairing=pairing, prompt_id=i)

    # If no more votes left
    return render_template("done_voting.html")
"""


@app.route("/lobby/<game_name>")
def lobby(game_name):
    username = session.get("username")
    game = games.get(game_name)

    current_prompt = None
    if username and game:
        if has_answered_all(game, username):
            render_template("lobby.html", game=game_name, current_prompt=current_prompt)
            
        # find the first pairing this user is in that they haven't answered yet
        for i, pairing in enumerate(game["pairings"]):
            if username in pairing["players"] and username not in pairing["answers"]:
                current_prompt = pairing.copy()
                current_prompt["id"] = i  # add index so we can reference later
                break
    #return render_template("lobby.html", game=game_name, current_prompt=current_prompt)        
    return render_template("lobby.html", game=game, current_prompt=current_prompt)

def has_answered_all(game, username):
    for pairing in game["pairings"]:
        if username in pairing["players"] and username not in pairing["answers"]:
            return False
    return True

@app.route("/join_game/<int:game_id>")
def join_game(game_id):
    game = games.get(game_id)
    if not game:
        return "Game not found", 404
    
    username = session.get("username")
    if username and username not in games[game_id]["players"]:
        games[game_id]["players"].append(username)
        
    return redirect(url_for("lobby", game_id=game_id))

@app.route("/leave_game/<game_type>")
def leave_game(game_type):
    username = session.get("username")
    
    if username and game_type in games:
        if username in games[game_type]["players"]:
            games[game_type]["players"].pop(username, None)
    return redirect(url_for("welcome"))


@app.route("/stop_game/<game_type>")
def stop_game(game_type):
    if game_type in games:
        games[game_type]["running"] = False
        # Don't delete the "players" key, just keep it
        # Optional: clear players if you want
        games[game_type]["players"] = []
        
        if game_type == "quiplash":
            game = games.get("quiplash")
            game["pairings"] = []
            game["round"] = 1
        
        # Notify all clients
        socketio.emit("game_update", {"game": game_type, "running": False})
    return redirect(url_for("welcome"))


@app.route("/submit_answer/<game_type>", methods=["POST"])
def submit_answer(game_type):
    username = session.get("username")
    game = games.get(game_type)
    prompt_id = int(request.form["prompt_id"])
    answer = request.form["answer"]

    if username and game:
        pairing = game["pairings"][prompt_id]
        pairing["answers"][username] = answer  # save their answer

    return redirect(url_for("lobby", game_name=game_type))

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
