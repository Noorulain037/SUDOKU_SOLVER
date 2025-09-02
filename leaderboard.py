# leaderboard.py
import os
import json

LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)
    return []

def save_score(name, level, time_taken, mistakes):
    score = max(0, 1000 - time_taken - (mistakes * 50))
    leaderboard = load_leaderboard()
    leaderboard.append({"name": name, "level": level, "time": time_taken, "mistakes": mistakes, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    leaderboard = leaderboard[:5]
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file)

def format_leaderboard_text(leaderboard, font):
    lines = []
    for i, entry in enumerate(leaderboard):
        text = f"{i+1}. {entry['name']} - {entry['level']} - {entry['score']} pts"
        lines.append(font.render(text, True, (0, 0, 0)))
    return lines
