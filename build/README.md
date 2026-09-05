# Building the ladder page

`index.html` at the repo root is generated. Rebuild it from here:

    cd build
    python buildsite.py      # writes ../index.html directly

Inputs: `history.json` (every game by club night), `seeds.json` (starting ratings),
`roster.json` (bracket tags, plus `"away": true` to retire someone by hand and
`"active": true` to keep them on the board past the 90-day rule), and
`archive.json` (seasons 1-7, including a per-night timeline built by
`arc_timeline.py` from `archive_raw.json`). The build also lists `../photos/`
so the page only requests a portrait that exists.

Trophies live in `trophies/1.png`, `2.png`, `3.png` (transparent PNGs, 240px).
Counts are worked out in the page: each club night, players who played at least
three games are ranked against the rest of their bracket, and a top-three finish
becomes a trophy. Ties share the place. The bracket is the one the player's
rating put them in **going into that night**, read off the bracket names ("over
1400", "U1400", "U1000"), so cups won on the way up stay with the division they
were won in. The header shows the strongest division a player has won in and
lists anything below it underneath. The page template is the
`ladderTemplate()` function in `ladderbuild.js`; the same file is spliced into the
phone pairing tool so both builds produce the identical site.

Page JS inside the template must use string concatenation, never `${}`, and no
backslashes except the closing `<\/script>`.

Refreshing data: `extract.py` reads the Chess Ranking Assistant workbook on D:,
`tourneys.py` scrapes SwissOnlineTournament, `roster2.py` rebuilds roster.json.
