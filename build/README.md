# Building the ladder page

`index.html` at the repo root is generated. Rebuild it from here:

    cd build
    python buildsite.py      # writes ../build/index.html -> copy to the repo root

Inputs: `history.json` (every game by club night), `seeds.json` (starting ratings),
`roster.json` (bracket tags), `archive.json` (seasons 1-7). The page template is the
`ladderTemplate()` function in `ladderbuild.js`; the same file is spliced into the
phone pairing tool so both builds produce the identical site.

Page JS inside the template must use string concatenation, never `${}`, and no
backslashes except the closing `<\/script>`.

Refreshing data: `extract.py` reads the Chess Ranking Assistant workbook on D:,
`tourneys.py` scrapes SwissOnlineTournament, `roster2.py` rebuilds roster.json.
