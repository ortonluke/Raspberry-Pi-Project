import random

# Load prompts from file
def load_prompts(filename="quip_prompts.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]
    return prompts

games = {
    "quiplash": {
        "running": True,
        "players": {},   # username -> {score, answers, votes}
        "pairings": [],  # stores (player1, player2, prompt)
        "round": 1
    }
}

def generate_pairings(players, prompts_per_player=2):
    """Generate randomized pairings with a limit per player."""
    all_prompts = load_prompts()
    random.shuffle(all_prompts)

    player_list = list(players.keys())
    random.shuffle(player_list)

    # Max total pairings = (#players * prompts_per_player) // 2
    max_pairs = (len(player_list) * prompts_per_player) // 2

    pairings = []
    usage_count = {p: 0 for p in player_list}

    # Go through prompts and assign until we hit the cap
    for prompt in all_prompts:
        # Stop once we’ve made enough pairings
        if len(pairings) >= max_pairs:
            break

        # Pick two players who aren’t maxed out
        available = [p for p in player_list if usage_count[p] < prompts_per_player]
        if len(available) < 2:
            break  # not enough players left to pair

        p1, p2 = random.sample(available, 2)
        pairings.append({
            "players": [p1, p2],
            "prompt": prompt,
            "answers": {},
            "votes": {}
        })
        usage_count[p1] += 1
        usage_count[p2] += 1

    return pairings
