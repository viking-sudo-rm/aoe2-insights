import requests
import tqdm
from collections import defaultdict
from rich import print


request = "https://aoe2.net/api/player/matches?game=aoe2de&steam_id={player}&count={count}&start={start}"
str_request = "https://aoe2.net/api/strings"
will = 76561198044260107


def get_matches(player, count=1000):
    start = 0
    results = []
    t = tqdm.tqdm()
    while True:
        new_results = requests.get(
            request.format(player=player, count=count, start=start)
        ).json()
        if not new_results:
            t.close()
            return results
        t.update(len(new_results))
        results.extend(new_results)
        start += count


def get_winrate(matches, name="YD.[skʷalos]"):
    # Ignore the cases with "None".
    won = [m for m in matches if sum(1 for p in m["players"] if p["name"] == name and p["won"])]
    lost = [m for m in matches if sum(1 for p in m["players"] if p["name"] == name and p["won"] == False)]
    return len(won) / (len(won) + len(lost))

all_matches = get_matches(will)
ranked = [m for m in all_matches if m["ranked"]]

print("\n== WR ==")
print(f"Overall: {get_winrate(ranked):.2f}")
name = "OG.L3inad"
with_danny = [m for m in ranked if name in (p["name"] for p in m["players"])]
without_danny = [
    m for m in ranked if name not in (p["name"] for p in m["players"])
]
print(f"With {name}: {get_winrate(with_danny):.2f}")
print(f"Without {name}: {get_winrate(without_danny):.2f}")


# Comptute strings for civilizations, etc.
strings = requests.get(str_request).json()
civs = {civ["id"]: civ["string"] for civ in strings["civ"]}

name = "OG.L3inad"  # "YD.[skʷalos]"
wins = defaultdict(int)
games = defaultdict(int)
for match in ranked:
    for player in match["players"]:
        if player["name"] == name:
            wins[player["civ"]] += 1 if player["won"] else 0
            games[player["civ"]] += 1 if player["won"] != None else 0

civ_wrs = [(wins[idx] / games[idx], idx) for idx in civs if games[idx] > 0]
print("\n== WR BY CIV ==")
for wr, idx in sorted(civ_wrs, key=lambda civ: -civ[0]):
    print(f"{civs[idx]}: {wr:.2f} (={wins[idx]}/{games[idx]})")
