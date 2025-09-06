import random

# Example prompt list
def load_prompts(filename="quip_prompts.txt"):
    with open(filename, "r") as f:
        # strip removes trailing newlines/whitespace
        prompts = [line.strip() for line in f if line.strip()]
    return prompts

games = {
    "quiplash": {
        "running": True,
        "players": {},  # username -> {score, answers, votes}
        "pairings": [], # stores (player1, player2, prompt)
        "round": 1
    }
}

def generate_pairings(players, max_prompts=2):
    """Generate randomized pairings with max 2 per player."""
    PROMPTS=load_prompts()
    player_list = list(players.keys())
    random.shuffle(player_list)
    
    pairings = []
    PROMPTS = load_prompts()
    prompt_pool = PROMPTS.copy()
    random.shuffle(prompt_pool)

    usage_count = {p: 0 for p in player_list}

    while len(prompt_pool) > 0:
        p1, p2 = random.sample(player_list, 2)
        if usage_count[p1] >= max_prompts or usage_count[p2] >= max_prompts:
            continue  # skip if either already maxed
        prompt = prompt_pool.pop()
        pairings.append({
            "players": [p1, p2],
            "prompt": prompt,
            "answers": {},   # filled in later
            "votes": {}      # filled in later
        })
        usage_count[p1] += 1
        usage_count[p2] += 1

    return pairings
