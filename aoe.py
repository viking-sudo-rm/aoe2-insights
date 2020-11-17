import requests
import tqdm
from collections import defaultdict
from rich import print


request = "https://aoe2.net/api/player/matches?game=aoe2de&steam_id={player}&count={count}&start={start}"
str_request = "https://aoe2.net/api/strings"
will = 76561198044260107


class Stats:

    def __init__(self, wins, losses):
        self.wins = wins
        self.losses = losses

    @classmethod
    def create(cls, matches, name="YD.[skʷalos]"):
        # Ignore the cases with "None".
        won = [m for m in matches if sum(1 for p in m["players"] if p["name"] == name and p["won"])]
        lost = [m for m in matches if sum(1 for p in m["players"] if p["name"] == name and p["won"] == False)]
        return Stats(len(won), len(lost))

    @property
    def wr(self):
        if self.wins + self.losses > 0:
            return self.wins / (self.wins + self.losses)
        else:
            return 0.

    def __str__(self):
        return f"{self.wr:.2f} (={self.wins}/{self.wins + self.losses})"


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


def get_stats_by_civ(ranked):
    name = "YD.[skʷalos]"
    games = defaultdict(list)
    for match in ranked:
        for player in match["players"]:
            if player["name"] == name:
                games[player["civ"]].append(match)
    return [(Stats.create(games[idx]), civs[idx]) for idx in civs if len(games[idx]) > 0]


all_matches = get_matches(will)
ranked = [m for m in all_matches if m["ranked"]]

strings = requests.get(str_request).json()
civs = {civ["id"]: civ["string"] for civ in strings["civ"]}
maps = {m["id"]: m["string"] for m in strings["map_type"]}

games_by_map = defaultdict(list)
for game in ranked:
    map_name = maps[game["map_type"]]
    games_by_map[map_name].append(game)

while True:
    cmd = input("> ").strip().split()
    if cmd[0] == "bymap":
        print("\n== WR BY MAP ==")
        map_wrs = [(Stats.create(games), name) for name, games in games_by_map.items()]
        for stats, map_name in sorted(map_wrs, key=lambda x: -x[0].wr):
            print(f"{map_name}: {stats}")

    elif cmd[0] == "onmap":
        map_name = " ".join(cmd[1:])
        civ_wrs = get_stats_by_civ(games_by_map[map_name])
        print(f"\n== WR BY CIV ON {map_name} ==")
        for stats, name in sorted(civ_wrs, key=lambda civ: -civ[0].wr):
            print(f"{name}: {stats}")
    
    elif cmd[0] == "overall":
        print("\n== WR ==")
        print(f"Overall: {Stats.create(ranked)}")
        name = "OG.L3inad"
        with_danny = [m for m in ranked if name in (p["name"] for p in m["players"])]
        without_danny = [
            m for m in ranked if name not in (p["name"] for p in m["players"])
        ]
        print(f"With {name}: {Stats.create(with_danny)}")
        print(f"Without {name}: {Stats.create(without_danny)}")

    elif cmd[0] == "quit" or cmd[0] == "exit":
        break

    print("\n")