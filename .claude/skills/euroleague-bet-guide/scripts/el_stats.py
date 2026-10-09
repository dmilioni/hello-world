#!/usr/bin/env python3
"""Official EuroLeague stats for the Euroleague_Bet_Guide skill.

Reads EuroLeague's own data service (the same data behind
euroleaguebasketball.net), which is the skill's ground truth.

Usage:
  el_stats.py schedule [--season E2026] [--teams OLY,PAN] [--from-round N] [--to-round N]
  el_stats.py team TEAM [--season E2026] [--last N]
  el_stats.py h2h TEAM_A TEAM_B [--season E2025]
  el_stats.py check TEAM "PLAYER:STAT>=N" ["PLAYER:STAT<=N" ...] [--last 3] [--season E2026]

check: hit rate of each pick over the team's last N played EuroLeague games.
  PLAYER is any part of the name (e.g. SARIC, MILLER). STAT is one of
  pts reb ast 3pm 2pm stl blk pra pr pa ra. Use >= for "N+" and "Over N-0.5",
  <= for "Under N+0.5" (Under 4.5 rebounds -> reb<=4). Games the player did
  not play count as misses. Flags: LOW-MIN (a game under 18 minutes),
  MIN-DROP (last game's minutes under 75% of the earlier ones), THIN-MARGIN
  (points line above 65% of the player's average).
  --before R  back-tests: uses the last N games before round R.
  --game G    post-game review: scores the picks against game code G (WON/LOST).

Team codes: OLY Olympiacos, PAN Panathinaikos, IST Anadolu Efes, ULK Fenerbahce,
MAD Real Madrid, BAR Barcelona, RED Crvena Zvezda, PAR Partizan, ZAL Zalgiris,
BAS Baskonia, VIR Virtus, MIL Milano, MUN Bayern, PRS Paris, ASV ASVEL,
TEL Maccabi, MCO Monaco, PAM Valencia, DUB Dubai, HTA Hapoel Tel Aviv.
The schedule command prints every code in use, so check codes there.

Hosts used: api-live.euroleague.net (schedule) and live.euroleague.net
(box scores, play-by-play). Both must be in the environment's allowed domains.
Schedule times are Central European Time; Greek time is +1 hour.
"""
import argparse
import json
import ssl
import sys
import urllib.request
import xml.etree.ElementTree as ET

SCHEDULE_URL = "https://api-live.euroleague.net/v1/schedules?seasonCode={season}"
BOX_URL = "https://live.euroleague.net/api/Boxscore?gamecode={game}&seasoncode={season}"
PBP_URL = "https://live.euroleague.net/api/PlayByPlay?gamecode={game}&seasoncode={season}"
SCORING = {"2FGM", "3FGM", "FTM"}
REBOUNDS = {"D", "O"}


def _ssl_context():
    for path in ("/root/.ccr/ca-bundle.crt", None):
        try:
            return ssl.create_default_context(cafile=path) if path else ssl.create_default_context()
        except (FileNotFoundError, ssl.SSLError):
            continue
    return ssl.create_default_context()


CTX = _ssl_context()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
        return resp.read()


def schedule(season):
    root = ET.fromstring(fetch(SCHEDULE_URL.format(season=season)))
    games = []
    for item in root.findall("item"):
        d = {c.tag: (c.text or "").strip() for c in item}
        d["gameday"] = int(d["gameday"])
        d["code"] = int(d["gamecode"].split("_")[-1])
        games.append(d)
    return games


def minutes(m):
    if not m or m == "DNP":
        return 0.0
    a, b = m.split(":")
    return int(a) + int(b) / 60


def box(season, game):
    return json.loads(fetch(BOX_URL.format(season=season, game=game)))


def firsts(season, game):
    """First scorer and first rebounder of the game, from play-by-play."""
    pbp = json.loads(fetch(PBP_URL.format(season=season, game=game)))
    scorer = rebounder = None
    for ev in pbp.get("FirstQuarter") or []:
        kind = (ev.get("PLAYTYPE") or "").strip()
        who = (ev.get("PLAYER") or "").strip()
        team = (ev.get("CODETEAM") or "").strip()
        if not who:
            continue
        if scorer is None and kind in SCORING:
            scorer = f"{who} ({team})"
        if rebounder is None and kind in REBOUNDS:
            rebounder = f"{who} ({team})"
        if scorer and rebounder:
            break
    return scorer, rebounder


def final_score(b):
    tot = []
    for q in b["ByQuarter"]:
        tot.append(sum(v for k, v in q.items() if k != "Team" and isinstance(v, int)))
    return tot


def cmd_schedule(args):
    teams = set(args.teams.split(",")) if args.teams else None
    for g in schedule(args.season):
        if g["gameday"] < args.from_round or g["gameday"] > args.to_round:
            continue
        if teams and not ({g["homecode"], g["awaycode"]} & teams):
            continue
        print(f"R{g['gameday']:>2} {g['date']} {g['startime']} CET  {g['homecode']} {g['hometeam']} - "
              f"{g['awaycode']} {g['awayteam']}  @ {g['arenaname']}  game={g['code']} played={g['played']}")


def player_table(team, season, games):
    rows, avgs = {}, {}
    for g in games:
        b = box(season, g["code"])
        names = [s["Team"] for s in b["Stats"]]
        sc = final_score(b)
        fs, fr = firsts(season, g["code"])
        print(f"R{g['gameday']} {g['date']}: {names[0]} {sc[0]} - {sc[1]} {names[1]} | "
              f"first score: {fs} | first rebound: {fr}")
        for s in b["Stats"]:
            for p in s["PlayersStats"]:
                if p["Team"] != team:
                    continue
                name = p["Player"].strip()
                line = (round(minutes(p["Minutes"])), p["Points"], p["TotalRebounds"],
                        p["Assistances"], p["FieldGoalsMade3"], p["FieldGoalsMade2"], p["IsStarter"])
                rows.setdefault(name, []).append(line)
    print(f"\n{team} per game: min'/pts/reb/ast/3pm/2pm (* = starter)")
    for name, ls in sorted(rows.items(), key=lambda kv: -sum(x[1] for x in kv[1])):
        played = [x for x in ls if x[0] > 0]
        n = max(len(played), 1)
        avg = "/".join(f"{sum(x[i] for x in played) / n:.1f}" for i in range(1, 5))
        cells = " | ".join(f"{m}'/{pt}/{r}/{a}/{t}/{two}{'*' if st else ''}" for m, pt, r, a, t, two, st in ls)
        print(f"{name:26s} {cells}   avg pts/reb/ast/3pm {avg}")


def cmd_team(args):
    played = [g for g in schedule(args.season)
              if g["played"] == "true" and args.team in (g["homecode"], g["awaycode"])]
    played.sort(key=lambda g: g["gameday"])
    player_table(args.team, args.season, played[-args.last:] if args.last else played)


STATS = {
    "pts": lambda p: p["Points"],
    "reb": lambda p: p["TotalRebounds"],
    "ast": lambda p: p["Assistances"],
    "3pm": lambda p: p["FieldGoalsMade3"],
    "2pm": lambda p: p["FieldGoalsMade2"],
    "stl": lambda p: p["Steals"],
    "blk": lambda p: p["BlocksFavour"],
    "pra": lambda p: p["Points"] + p["TotalRebounds"] + p["Assistances"],
    "pr": lambda p: p["Points"] + p["TotalRebounds"],
    "pa": lambda p: p["Points"] + p["Assistances"],
    "ra": lambda p: p["TotalRebounds"] + p["Assistances"],
}


def parse_pick(spec):
    name, rest = spec.split(":", 1)
    op = ">=" if ">=" in rest else "<="
    stat, line = rest.split(op)
    stat = stat.strip().lower()
    if stat not in STATS:
        sys.exit(f"Unknown stat '{stat}' in {spec}. Use one of: {' '.join(STATS)}")
    return name.strip().upper(), stat, op, float(line)


def cmd_check(args):
    played = [g for g in schedule(args.season)
              if g["played"] == "true" and args.team in (g["homecode"], g["awaycode"])]
    played.sort(key=lambda g: g["gameday"])
    if args.game:
        games = [g for g in played if g["code"] == args.game]
    elif args.before:
        games = [g for g in played if g["gameday"] < args.before][-args.last:]
    else:
        games = played[-args.last:]
    if not games:
        sys.exit("No matching played games.")
    boxes = [box(args.season, g["code"]) for g in games]
    rounds = ",".join(f"R{g['gameday']}" for g in games)
    title = "result of" if args.game else f"last {len(games)} EuroLeague games before R{args.before}:" if args.before else f"last {len(games)} EuroLeague games"
    print(f"{args.team} {title} ({rounds}), official box scores")
    for spec in args.picks:
        name, stat, op, line = parse_pick(spec)
        values, mins, label = [], [], name
        for b in boxes:
            found = None
            for s in b["Stats"]:
                for p in s["PlayersStats"]:
                    if p["Team"] == args.team and name in p["Player"].upper():
                        found = p
            m = minutes(found["Minutes"]) if found else 0
            mins.append(round(m))
            if found is None or m == 0:
                values.append(None)
            else:
                label = found["Player"].strip()
                values.append(STATS[stat](found))
        hits = sum(1 for v in values if v is not None and (v >= line if op == ">=" else v <= line))
        shown = ", ".join("DNP" if v is None else str(v) for v in values)
        n = len(values)
        if args.game:
            verdict = "WON" if hits == n else "LOST"
        else:
            verdict = "OK" if hits == n else ("WEAK" if hits == n - 1 else "FAIL")
        flags = []
        if not args.game:
            if any(m < 18 for m in mins):
                flags.append("LOW-MIN")
            if len(mins) >= 2 and mins[-1] < 0.75 * (sum(mins[:-1]) / len(mins[:-1])):
                flags.append("MIN-DROP")
            if op == ">=" and stat == "pts" and None not in values and line > 0.65 * (sum(values) / n):
                flags.append("THIN-MARGIN")
        flag_txt = ("  <" + ", ".join(flags) + ">") if flags else ""
        print(f"{verdict:4s} {hits}/{n}  {label}: {stat} {op} {line:g}   [{shown}]  min [{', '.join(map(str, mins))}]{flag_txt}")


def cmd_h2h(args):
    pair = {args.team_a, args.team_b}
    games = [g for g in schedule(args.season)
             if g["played"] == "true" and {g["homecode"], g["awaycode"]} == pair]
    if not games:
        print("No played games between these teams in", args.season)
        return
    for team in (args.team_a, args.team_b):
        player_table(team, args.season, games)
        print()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("schedule")
    s.add_argument("--season", default="E2026")
    s.add_argument("--teams")
    s.add_argument("--from-round", type=int, default=1)
    s.add_argument("--to-round", type=int, default=99)
    t = sub.add_parser("team")
    t.add_argument("team")
    t.add_argument("--season", default="E2026")
    t.add_argument("--last", type=int, default=0)
    h = sub.add_parser("h2h")
    h.add_argument("team_a")
    h.add_argument("team_b")
    h.add_argument("--season", default="E2025")
    c = sub.add_parser("check")
    c.add_argument("team")
    c.add_argument("picks", nargs="+")
    c.add_argument("--last", type=int, default=3)
    c.add_argument("--season", default="E2026")
    c.add_argument("--game", type=int, help="score picks against one played game (post-game review)")
    c.add_argument("--before", type=int, help="use the last N games before this round (back-testing)")
    args = ap.parse_args()
    {"schedule": cmd_schedule, "team": cmd_team, "h2h": cmd_h2h, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach EuroLeague data service: {e}. "
                 "Check that api-live.euroleague.net and live.euroleague.net are allowed domains.")
