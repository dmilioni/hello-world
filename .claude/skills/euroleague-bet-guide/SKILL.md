---
name: euroleague-bet-guide
description: Before each EuroLeague game of Olympiacos or Panathinaikos, research the game (calendar, player form in EuroLeague and the Greek league, news, injuries, travel and fatigue, last season's head-to-head) and propose three Stoiximan.gr Bet Builder slips — low risk about 5x, medium 20–25x, high 50–80x — built for the highest chance of winning at each payout. Use when the user asks for bets, a bet builder, προγνωστικά or a betting plan for an Olympiacos or Panathinaikos game, or sends Stoiximan screenshots for one.
---

# Euroleague_Bet_Guide — Olympiacos / Panathinaikos Bet Builder

Deliver, for **every upcoming EuroLeague game of Olympiacos (OLY) and Panathinaikos (PAO)**, three Stoiximan Bet Builder slips:

| Tier | Target total odds | Goal |
|---|---|---|
| Low risk | ≈ 5x (4.8–5.3) | Highest possible hit rate |
| Medium risk | 20x–25x | Best hit rate inside the band |
| High risk / max profit | 50x–80x | Best hit rate inside the band |

Every pick must be a Bet Builder (BB) market from the same game.

## Step 1 — Find the games

1. Work out today's date and look ahead about 7 days. Find OLY and PAO games in that window on the **official EuroLeague schedule** (`euroleaguebasketball.net/en/euroleague/game-center/`), which is the ground truth for dates, times and venues. Greek searches such as `Ολυμπιακός επόμενος αγώνας EuroLeague` can help you find the game, but if a date or time disagrees with the official site, use the official one. Note the round, date, Greek time, venue and opponent.
2. If neither team plays within about 48 hours, list the next game dates and stop. Bets are only made close to the game, because odds and line-ups change.
3. Treat each game separately. If both teams play, produce two full reports.

## Step 2 — Get the Stoiximan markets

**Stoiximan (`https://www.stoiximan.gr/`) is the only bookmaker for this skill.** All picks, odds, Bet Builder markets and offers come from Stoiximan. Never use other bookmakers' odds, or odds from tipster or aggregator sites, as a substitute; they may only be mentioned as context.

1. Open `https://www.stoiximan.gr/` and go to Μπάσκετ → EuroLeague → the game, with Bet Builder switched on. Also open the offers page (Προσφορές). Use one quick `curl` check.
   - **Tested 7/10/2026: the domain is allowed, but Stoiximan geo-blocks cloud sessions.** It returns 403 with the message "According to the local regulatory provisions, our services cannot be accessed from your location", because the sessions run outside Greece.
   - When you get that 403, don't retry and don't look for workarounds. Go straight to the next option.
   - **Best option: the user's own Chrome browser in Greece.** If Claude in Chrome tools (`mcp__claude-in-chrome__*`) are available, which happens when the skill runs on the user's computer through the Claude Desktop app or a local `claude` session with the Chrome extension, load the `chrome-browser` skill first. Then open the game on stoiximan.gr in a new tab with Bet Builder on, and read the markets and the offers page. **Read only:** never log in, click a bet, add to the slip, deposit, or change account settings. The user places the bets.
   - If no browser tools are available (for example in the cloud session or the daily scheduled run), use the screenshots step below.
2. **If you cannot read the odds, stop and ask the user for screenshots.** Do not guess the odds. Ask for these sections:
   - **Κύριες Αγορές:** winner, handicap and total.
   - **Player ladders and O/U lines:** Πόντοι, Ριμπάουντ, Ασίστ, Εύστοχα Τρίποντα, Εύστοχα Δίποντα, Π+Ρ+Α, Π+Α, Ρ+Α, Double-Double, Επιθετικά/Αμυντικά Ριμπάουντ.
   - **Team specials (Ειδικά ομάδων):** total threes, team rebounds, team with the most threes/rebounds.
   - **The offers page (Προσφορές / Bet Boost / Ενισχυμένες αποδόσεις, Bet Builder boosts, profit boosts, insurance):** any offer valid for this game.
3. Only use markets that carry the **BB** badge. Write down every odd exactly as shown, with the time of the screenshot.
4. If the screenshots are for a different game than expected, say so and analyse the game they actually show.

## Step 3 — Research (do this before choosing any pick)

Search in English and Greek.

### Ground truth: the official EuroLeague site

**`https://www.euroleaguebasketball.net/en/` is the ground truth for every EuroLeague fact.** That covers the schedule, venue and tip-off time, final scores, box scores, player and team stats, and the official injury report. Check it first, every time:
- the schedule and results (`/en/euroleague/game-center/`);
- full box scores per game (minutes, points, rebounds, assists, 3PM, PIR);
- player and team stats (`/en/euroleague/stats/`);
- the per-round injury report (search "Injury report: Round N");
- "Game Facts" and "Game Notes" previews for each game.

**Get the official data with the helper script first.** It reads EuroLeague's own data service (`api-live.euroleague.net` and `live.euroleague.net`, the data behind the official site), which is the most reliable way in:

```bash
S=.claude/skills/euroleague-bet-guide/scripts/el_stats.py
python3 -I $S schedule --teams OLY,PAN --from-round 4 --to-round 6   # dates (CET; Greek time = +1h), venues, game codes
python3 -I $S team OLY                       # every played game: score, first scorer, first rebound, per-player min/pts/reb/ast/3pm/2pm/starter, averages
python3 -I $S team IST --last 3              # opponent, last 3 games only
python3 -I $S h2h OLY IST --season E2025     # last season's head-to-head with full player lines
```

On Windows, if `python3` is not found, use `py` or `python` instead, with the same arguments.

Use it for the schedule, scores, box scores, season averages, starters, minutes load, and first scorer / first rebound history. The website itself (`euroleaguebasketball.net`) blocks automated browsers with a Vercel security check, so don't fetch it. For news that only the website has (the injury report, Game Facts), run WebSearch with `allowed_domains: ["euroleaguebasketball.net"]`, for example `injury report round 4`.

How to apply it:
- **If any other source disagrees with the official site, the official site wins.** Use its number and do not average or blend it with others.
- **If the official site hasn't published something yet** (for example the round's injury report or a box score), you may use other sources, but label the fact "unofficial" in the report. Re-check the official site before the final slips and correct anything that changed.
- **Greek league and other national-league games are not on the official EuroLeague site.** For those, esake.gr is the official source, and Gazzetta or BasketNews are next.
- In the output, mark each stat as (official) or (unofficial), and list the official EuroLeague links first in Sources.

### Secondary sources: news, line-ups and context

**Gazzetta's EuroLeague section** (`https://www.gazzetta.gr/basketball/euroleague`): news, 12-man lists, the coach's press conference and live reports. Use `https://www.gazzetta.gr/basketball/stoiximan-gbl` for Greek league games. Fetch the pages directly; if fetching is blocked, run WebSearch with `allowed_domains: ["gazzetta.gr"]` and queries such as `Ολυμπιακός 12άδα Εφές` or `Παναθηναϊκός τραυματίες`.

**BasketNews** (`https://basketnews.com`). Use it for:
- the daily-updated EuroLeague injury report (search "EuroLeague Injury Report (updated daily)");
- team pages with roster, schedule and stats (for example `/teams/460-olympiacos-piraeus.html`, `/teams/583-anadolu-efes-istanbul.html`);
- player pages with game logs across EuroLeague and national leagues;
- transfer and signing news, and post-game coach quotes.

Fetch the pages directly; if fetching is blocked, run WebSearch with `allowed_domains: ["basketnews.com"]`, for example `Olympiacos injury` or `Vezenkov stats`.

Other useful sources: eurohoops.net (EN and EL), sofascore.com news, esake.gr (Greek league), sport24.gr, sportal.gr, sdna.gr, in.gr, and opponent-language press. Many of these sites are blocked from fetching, so use the search-result summaries. Cross-check numbers across two sources, and check them against the official EuroLeague site whenever it has them.

Collect:

1. **Last 7–10 days of games for both teams, all competitions** (EuroLeague plus the Greek league or the opponent's national league): score, and minutes, points, rebounds, assists and threes made for every player who has a Stoiximan prop.
2. **Season-to-date EuroLeague averages** per player, plus last season's averages as a prior when fewer than about 5 games have been played.
3. **Last season's head-to-head:** scores, totals and standout players.
4. **News, the day before and the day of the game:**
   - injuries, illness, suspensions, the coach's press conference, the 12-man list;
   - returning players (they reduce the minutes of others: for example a returning center cuts the other center's rebounds, and a returning guard cuts the starting PG's assists);
   - new signings.
5. **Fatigue and travel:**
   - games played in the last 7 days (double-round weeks, Greek league weekend games);
   - flight length of the last trip and of this one (for example Istanbul or Belgrade compared with Madrid or Tel Aviv);
   - back-to-back road games;
   - each player's minute load in the last 2 games. Over 30 minutes twice suggests a dip, and coaches rest players in Greek league games before big EuroLeague nights.
6. **Context:** home or away, the venue (OLY are playing at SUNEL Arena while the SEF is renovated), standings pressure, derby intensity, the referees if known, and the pace of both teams (points scored and allowed).

Write a short form table for each team, as in the example output below.

## Step 4 — Estimate a probability for every candidate pick

For each BB market you might use:

- **Implied probability** = 1 / odds.
- **Your probability:** blend recent form (last 3–5 games, about 50%), season average (about 30%) and last season or head-to-head (about 20%). Then adjust for:
  - minutes changes from injuries and returning players;
  - fatigue and travel;
  - opponent strength (rebounding rate, pace, three-point defence);
  - home or away (about +1 point for home scorers);
  - blowout risk (stars play fewer minutes in a blowout, which hurts "overs").
- **Edge** = your probability × odds. Above 1.00 is value; below 0.95, avoid.

Rules of thumb:

- Ladders ("X+") at low odds (1.20–1.50) on rebounds and assists of high-minute starters are the most reliable building blocks.
- Points props are more volatile than rebounds and assists. Threes props are the most volatile; use them only with strong evidence.
- Avoid props on players who are questionable, just back from injury, or in a minutes battle.
- The game-winner and the handicap are close to fair. Use them only when they fit the slip (for example a team-win pick with that team's scorers going "over").

## Step 4b — Check every pick against the last 3 games (mandatory)

Before any pick goes on a slip, check it against the player's **last 3 EuroLeague games** in the official box scores, using the helper script. Pass all the picks of one team in a single call:

```bash
S=.claude/skills/euroleague-bet-guide/scripts/el_stats.py
python3 -I $S check IST "SARIC:ra>=7" "STRAZEL:pts>=12" "FERNANDO:reb<=4"
python3 -I $S check OLY "MILLER:ast>=6" "VEZENKOV:reb>=5" "VEZENKOV:pra>=26"
```

How to write a pick:
- "N+" or "Over N−0.5" becomes `>=N`; "Under N+0.5" becomes `<=N`. For example, Under 4.5 rebounds is `reb<=4`.
- Combined markets: Π+Ρ+Α → `pra`, Π+Ρ → `pr`, Π+Α → `pa`, Ρ+Α → `ra`.
- Threes made → `3pm`, twos made → `2pm`.

The script prints **OK** (3/3), **WEAK** (2/3) or **FAIL** (1/3 or 0/3), with the three values.

**Rules:**

| Slip | Allowed picks |
|---|---|
| Low risk (≈5x) | **Only OK (3/3).** |
| Medium (20–25x) | OK, plus **at most one WEAK** (2/3). |
| High (50–80x) | OK and WEAK. **At most three WEAK.** |
| Any slip | **Never FAIL** (1/3 or 0/3). |

- **A FAIL pick is dropped.** Replace it with a market on the same player that passes, for example Šarić 7+ rebounds (FAIL: 5, 3, 10) → Šarić 7+ Ρ+Α (OK: 7, 7, 11). Or move the line one step towards safety.
- **The only exception** is a clear role change, for example the starter at that position is now out. Even then, never use the pick on the low slip, label it "role change, FAIL on last 3", and explain why.
- **Players with fewer than 3 EuroLeague games this season** (new signings, players back from injury, DNPs) are treated as unproven. Don't use their props, and flag them.
- **Team picks** (winner, handicap, team totals, team rebounds or threes, "most …" markets): check the team's last 3 results the same way, by hand, from the `team` command.
- **National-league games** (Greek league, Turkish league and so on) are not in the script. If the last game was a national-league game, mention it as unofficial context, but the pass/fail rule uses the 3 EuroLeague games.
- **After any swap,** re-run `check` on the final picks so every leg on every slip has a result.

## Step 5 — Build the three slips

**Key principle:** for a fixed total payout, win probability = Π(your p) = Π(edge) ÷ total odds. So, to maximise the chance of winning:

1. Use only legs with edge ≥ 1.00 (ideally ≥ 1.03).
2. Prefer **fewer legs with higher edge** over many legs. Every leg carries bookmaker margin.
3. Avoid legs that contradict each other (for example Francisco 5+ assists together with "Baldwin most assists in the game"). Positively correlated legs (a team win plus its PG's assists) are fine, but Stoiximan reprices those, so the app's total will be lower than the simple product.
4. Hit the target band by moving a leg one ladder step up or down, not by adding weak legs.
5. **Offers:** if a Bet Boost or Bet Builder boost applies, build the slip that qualifies for it (minimum legs, minimum odds, eligible markets) as long as the legs keep edge ≥ 1. A boost raises the edge of the whole slip. Note insurance or "money back if one leg fails" offers: they favour the slip with more, but safer, legs.

Typical shapes:

- **About 5x:** 4–6 legs from the 1.25–1.55 range.
- **20–25x:** 6–8 legs with 2–3 at 1.65–2.00.
- **50–80x:** 7–9 legs, or fewer legs with 2–3 at 1.90–2.70.

Compute the product of odds and the estimated hit probability (product of your probabilities, with a small correlation adjustment) for each slip.

## Step 6 — Output format (in the user's language; Greek market names are fine)

For each game:

1. **Header:** teams, round, date and Greek time, venue, main-market odds.
2. **Form table:** last 3–5 games for both teams with key player lines, plus points scored and allowed per game.
3. **News:** injuries, returns, fatigue and travel notes.
4. **Prediction:** score, total, win probability, first-scorer and first-rebound top 4–6 with probabilities.
5. **Top 5 most likely stats,** each with its odds, Stoiximan's implied probability and your probability.
6. **Three slips** as tables with columns pick — Stoiximan market name — odds — **last 3** (for example `3/3 [6, 6, 8]`), then the total odds and the estimated chance of winning. Every leg must show its last-3 result from Step 4b.
7. **Offers used,** and how the slip qualifies.
8. **Before you bet:** line-up checks with a specific swap for each (for example "if X is out, swap leg 4 for …"), and a note that the app's total may differ because of correlation repricing.
9. **Stake guidance:** a small fixed fraction of the balance (for example 10% on the 5x slip, 5% on the 20–25x slip, 2–3% on the 50–80x slip). Remind the user, once and briefly, that these are estimates and that every slip can lose.
10. **Sources** list with links.
11. **Save the report** as Markdown to `reports/YYYY-MM-DD_HOME-AWAY.md` in the repo folder (for example `reports/2026-10-09_OLY-IST.md`), using the game date, and tell the user the path. Terminal windows on Windows often cut wide tables, so the file is the readable copy. Do not commit it.
12. **Phone notification:** after the report is delivered, call the `PushNotification` tool (load it with ToolSearch `select:PushNotification` if needed). Send one line under 200 characters with the game and the three slips' total odds and estimated chance of winning, for example `OLY-EFS slips ready: 5.0x (24%) · 22x (5%) · 64x (1.6%). Open Claude to see the picks.`. When Remote Control is connected, this reaches the user's phone.

## Hard rules

- Never invent odds, stats or injury news. If a number is uncertain, say so.
- The official EuroLeague site (euroleaguebasketball.net) is the ground truth for every EuroLeague fact. When sources conflict, use the official figure and mention the conflict only briefly. Label anything not yet published there as unofficial.
- Never include a player whose availability is unconfirmed without giving a swap.
- Never promise or imply a guaranteed win, and never encourage chasing losses or increasing stakes after a loss.
- If the user's balance or behaviour suggests stress about money, say so gently and suggest pausing.

## Example output (shape only)

```
# Ολυμπιακός – Αναντολού Εφές · Round 4 · Fri 9/10 21:15 · SUNEL Arena
Main markets: OLY 1.40 / EFS 2.95 · −7.5 1.90 · O/U 161.5 1.87/1.90

Form (last 4, all competitions) ...
News: Montero (virus) doubtful; Milutinov back from tendonitis; Efes without M. James (Achilles), Papagiannis (knee) ...

Low risk ≈5.0x (est. hit 24%)
| Pick | Market | Odds |
| Vezenkov 12+ points | Πόντοι | 1.30 |
...
```
