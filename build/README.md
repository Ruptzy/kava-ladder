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
three games are ranked against the rest of their own bracket, and a top-three
finish becomes a trophy. Ties share the place. A player's bracket is the one
they are in now, since the old workbook never recorded bracket by night. The page template is the
`ladderTemplate()` function in `ladderbuild.js`; the same file is spliced into the
phone pairing tool so both builds produce the identical site.

Page JS inside the template must use string concatenation, never `${}`, and no
backslashes except the closing `<\/script>`.

Refreshing data: `extract.py` reads the Chess Ranking Assistant workbook on D:,
`tourneys.py` scrapes SwissOnlineTournament, `roster2.py` rebuilds roster.json.
