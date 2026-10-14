#!/usr/bin/env python3
"""Back-test the low-risk (~5x) slip rules on past EuroLeague games.

For every played game in the chosen rounds, it builds the low-risk slip
using ONLY official box scores from games played before that round, then
scores it against the real result. Odds are not available historically,
so each leg gets a model price: implied probability from the player's
recent numbers (normal approximation) with a 7% bookmaker margin. Treat the
"x" totals as approximate.

Usage:
  backtest.py [--rounds 4,5] [--focus OLY,PAN] [--config NAME] [--grid]
              [--cache DIR] [--season E2026] [-v]

  --grid     try every rule variant, tuned on the first round in --rounds
             and validated on the rest; prints a ranking
  --config   run one named variant from CONFIGS and print every slip
"""
import argparse
import importlib.util
import itertools
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("el_stats", os.path.join(HERE, "el_stats.py"))
el = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(el)

MARGIN = 0.93  # bookmaker keeps ~7%


def load_games(season, max_round, cache):
    os.makedirs(cache, exist_ok=True)
    out = []
    for g in el.schedule(season):
        if g["played"] != "true" or g["gameday"] > max_round:
            continue
        path = os.path.join(cache, f"{season}_{g['code']}.json")
        if os.path.exists(path):
            with open(path) as f:
                b = json.load(f)
        else:
            b = el.box(season, g["code"])
            with open(path, "w") as f:
                json.dump(b, f)
        teams = {}
        for s in b["Stats"]:
            for p in s["PlayersStats"]:
                code = p["Team"]
                teams.setdefault(code, []).append({
                    "name": p["Player"].strip(),
                    "min": el.minutes(p["Minutes"]),
                    "pts": p["Points"], "reb": p["TotalRebounds"], "ast": p["Assistances"],
                    "starter": p["IsStarter"],
                })
        score = {}
        for q, code in zip(b["ByQuarter"], [g["homecode"], g["awaycode"]]):
            score[code] = sum(v for k, v in q.items() if k != "Team" and isinstance(v, int))
        out.append({"round": g["gameday"], "code": g["code"], "home": g["homecode"],
                    "away": g["awaycode"], "players": teams, "score": score})
    return out


def team_history(games, team, before_round):
    hist = [g for g in games if g["round"] < before_round and team in (g["home"], g["away"])]
    hist.sort(key=lambda g: g["round"])
    return hist


def net_rating(hist, team):
    if not hist:
        return 0.0
    diffs = []
    for g in hist:
        opp = g["away"] if g["home"] == team else g["home"]
        diffs.append(g["score"][team] - g["score"][opp])
    return sum(diffs) / len(diffs)


def stat_value(row, stat):
    if stat == "pra":
        return row["pts"] + row["reb"] + row["ast"]
    if stat == "ra":
        return row["reb"] + row["ast"]
    return row[stat]


SD = {"pts": (0.40, 2.5), "reb": (0.40, 1.3), "ast": (0.45, 1.2), "pra": (0.30, 3.5), "ra": (0.38, 1.6)}


def p_market(mean, stat, k):
    """How a bookmaker would price 'k+': normal around the player's average
    with a typical spread for that stat."""
    a, b = SD[stat]
    sd = a * mean + b
    z = (k - 0.5 - mean) / sd
    return 1 - 0.5 * (1 + math.erf(z / math.sqrt(2)))


CONFIGS = {
    # the rules as they were in the skill before this back-test
    "current": dict(minmin=18, mindrop=0.75, factor=1.0, stats=("reb", "ast", "pra", "pts"),
                    team=True, team_p=0.65, blowout_pts=12, per_player=1),
    # safest slip (~2.5x): only cheap legs, at the last-3 minimum
    "safe": dict(minmin=18, mindrop=0.75, factor=1.0, stats=("reb", "ast", "pra", "pts"),
                 team=True, team_p=0.7, blowout_pts=99, per_player=1, max_legs=6, max_odds=1.24),
    # best variant from the R4-R5 grid search (14/10/2026): about 1 slip in 4 wins
    "tuned": dict(minmin=15, mindrop=0.75, factor=1.0, stats=("reb", "ast", "pra", "pts"),
                  team=True, team_p=0.7, blowout_pts=99, per_player=2, max_legs=8),
}


def candidate_legs(games, game, team, cfg):
    hist = team_history(games, team, game["round"])[-3:]
    if len(hist) < 3:
        return []
    legs = []
    names = {r["name"] for g in hist for r in g["players"].get(team, [])}
    for name in names:
        rows = []
        for g in hist:
            row = next((r for r in g["players"][team] if r["name"] == name), None)
            rows.append(row)
        if any(r is None or r["min"] == 0 for r in rows):
            continue
        mins = [r["min"] for r in rows]
        if min(mins) < cfg["minmin"]:
            continue
        if mins[-1] < cfg["mindrop"] * (sum(mins[:-1]) / 2):
            continue
        for stat in cfg["stats"]:
            vals = [stat_value(r, stat) for r in rows]
            k = math.floor(min(vals) * cfg["factor"])
            if k < (2 if stat in ("reb", "ast") else 4):
                continue
            mean = sum(vals) / 3
            p = p_market(mean, stat, k)
            odds = max(1.10, MARGIN / max(p, 0.05))
            if odds > cfg.get("max_odds", 99):
                continue
            cushion = (min(vals) - k + 1) / max(mean, 1)
            legs.append({"kind": "player", "team": team, "name": name, "stat": stat, "k": k,
                         "p": p, "odds": odds, "vals": vals, "cushion": cushion})
    return legs


def team_leg(games, game, cfg):
    h, a = game["home"], game["away"]
    nh = net_rating(team_history(games, h, game["round"]), h)
    na = net_rating(team_history(games, a, game["round"]), a)
    diff = (nh - na) / 2 + 3
    p_home = 1 / (1 + math.exp(-diff / 6))
    fav, p = (h, p_home) if p_home >= 0.5 else (a, 1 - p_home)
    margin = abs(diff)
    return {"kind": "team", "team": fav, "name": f"{fav} to win", "p": p,
            "odds": max(1.05, MARGIN / p), "margin": margin}


def build_slip(games, game, cfg):
    legs = candidate_legs(games, game, game["home"], cfg) + candidate_legs(games, game, game["away"], cfg)
    tl = team_leg(games, game, cfg)
    blowout = tl["margin"] >= cfg["blowout_pts"]
    if blowout:
        legs = [l for l in legs if l["stat"] in ("reb",) and l["team"] != tl["team"]]
    legs.sort(key=lambda l: (-l["cushion"], -l["odds"]))
    slip, total, used = [], 1.0, {}
    if cfg["team"] and tl["p"] >= cfg["team_p"]:
        slip.append(tl)
        total *= tl["odds"]
    for l in legs:
        if total >= cfg.get("target", 5.0) * 0.96 or len(slip) >= cfg.get("max_legs", 99):
            break
        if used.get(l["name"], 0) >= cfg["per_player"]:
            continue
        slip.append(l)
        used[l["name"]] = used.get(l["name"], 0) + 1
        total *= l["odds"]
    return slip, total


def actual(game, leg):
    if leg["kind"] == "team":
        opp = game["away"] if leg["team"] == game["home"] else game["home"]
        return game["score"][leg["team"]] > game["score"][opp], f"{game['score'][leg['team']]}-{game['score'][opp]}"
    row = next((r for r in game["players"].get(leg["team"], []) if r["name"] == leg["name"]), None)
    if row is None or row["min"] == 0:
        return False, "DNP"
    v = stat_value(row, leg["stat"])
    return v >= leg["k"], f"{v} ({round(row['min'])}')"


def run(games, rounds, cfg, verbose=False, focus=None):
    res = []
    for g in games:
        if g["round"] not in rounds:
            continue
        if focus and not ({g["home"], g["away"]} & focus):
            continue
        slip, total = build_slip(games, g, cfg)
        if not slip or total < cfg.get("target", 5.0) * 0.9:
            res.append((g, None, total, []))
            continue
        outcomes = [(l, *actual(g, l)) for l in slip]
        won = all(o[1] for o in outcomes)
        res.append((g, won, total, outcomes))
        if verbose:
            print(f"R{g['round']} {g['home']}-{g['away']} {g['score'][g['home']]}-{g['score'][g['away']]}"
                  f"  slip {total:.2f}x  {'WON' if won else 'LOST'}")
            for l, ok, txt in outcomes:
                desc = l["name"] if l["kind"] == "team" else f"{l['name']} {l['stat']} {l['k']}+ {l['vals']}"
                print(f"   {'✔' if ok else '✘'} {desc}  p≈{l['p']:.2f} odds≈{l['odds']:.2f}  actual {txt}")
    return res


def summary(res):
    played = [r for r in res if r[1] is not None]
    won = sum(1 for r in played if r[1])
    legs = [o for r in played for o in r[3]]
    lw = sum(1 for o in legs if o[1])
    return won, len(played), lw, len(legs), len(res) - len(played)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", default="4,5")
    ap.add_argument("--focus")
    ap.add_argument("--config", default="current")
    ap.add_argument("--target", type=float, default=5.0, help="target total odds of the slip")
    ap.add_argument("--grid", action="store_true")
    ap.add_argument("--season", default="E2026")
    ap.add_argument("--cache", default=os.path.join(os.path.expanduser("~"), ".cache", "el_backtest"))
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    rounds = [int(x) for x in a.rounds.split(",")]
    games = load_games(a.season, max(rounds), a.cache)
    focus = set(a.focus.split(",")) if a.focus else None
    if a.grid:
        tune, test = {rounds[0]}, set(rounds[1:])
        grid = dict(minmin=[15, 18, 22, 25], mindrop=[0.75, 0.85], factor=[0.5, 0.6, 0.7, 0.8, 1.0],
                    stats=[("reb",), ("reb", "ast"), ("reb", "ast", "pra"), ("reb", "ast", "pra", "pts")],
                    team=[True, False], team_p=[0.6, 0.7], blowout_pts=[8, 99], per_player=[1],
                    max_legs=[5, 6, 8])
        keys = list(grid)
        rows = []
        for combo in itertools.product(*grid.values()):
            cfg = dict(zip(keys, combo), target=a.target)
            t = summary(run(games, tune, cfg))
            v = summary(run(games, test, cfg))
            f = summary(run(games, set(rounds), cfg, focus={"OLY", "PAN"}))
            rows.append((t[0] / max(t[1], 1), v[0] / max(v[1], 1), t, v, f, cfg))
        rows.sort(key=lambda r: (-(r[2][0] + r[3][0]) / max(r[2][1] + r[3][1], 1), -r[1], -(r[2][1] + r[3][1])))
        print("rank tune(won/slips legs) test(won/slips legs) OLY+PAN(won/slips)  config")
        for i, (_, _, t, v, f, cfg) in enumerate(rows[:15], 1):
            print(f"{i:2d}  {t[0]}/{t[1]} ({t[2]}/{t[3]})   {v[0]}/{v[1]} ({v[2]}/{v[3]})   {f[0]}/{f[1]}   {cfg}")
        return
    cfg = dict(CONFIGS[a.config], target=a.target)
    res = run(games, set(rounds), cfg, verbose=True, focus=focus)
    w, n, lw, ln, skipped = summary(res)
    print(f"\nSlips won {w}/{n} (skipped {skipped}), legs won {lw}/{ln}")


if __name__ == "__main__":
    main()
