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

Bracket tabs are art: `tabs/all.png`, `tabs/over-1400.png`, `tabs/u1400.png`,
`tabs/u1000.png` (the file name is the bracket slugged). The wording is part of
the picture, so the button text is kept for screen readers and hidden on screen.
If any panel is missing the tabs fall back to plain text buttons.

Podium cards live in `podium/1.png`, `2.png`, `3.png`; the circle position for
each is set per card in the CSS, measured off the art.

Achievements: 71 of them, defined in `ladderbuild.js` (search `var ACH=`). Each
has a stable id which doubles as its icon file name, `achievements/<id>.png`;
see `achievements/README.md` for the full list. Missing icons fall back to an
emoji, so art can be added a few at a time. Most are about turning up, variety and effort rather than strength, and unearned
ones stay on the profile with their progress. Thresholds are deliberately steep:
a new player with one night earns one or two, a regular around a dozen, and the
club's busiest member 42.

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

## Easter eggs

Twenty of them, all hanging off things people already touch, none blocking a tap
meant for navigation. Search `easter eggs` in `ladderbuild.js`.

Tap: the club badge (knight hops), the seasons tag, the updated line, the word
"Ladder" in the heading (it renames itself), the wiggle-room symbol, a profile's
rating (counts up from the seed), its record (cycles to percentages), a trophy
(spins), the portrait (shows a spirit piece), the turnout blocks (ripple), and a
crosstable diagonal cell.

Type into search (58 words): `1337`, `backgammon`, `beginner`, `bishop`, `blitz`, `blunder`, `brilliant`, `bullet`, `castle`, `castling`, `cheat`, `checkers`, `checkmate`, `chess goblin`, `clock`, `d4`, `draw`, `e4`, `e5`, `elo`, `en passant`, `endgame`, `engine`, `enpassant`, `fork`, `gambit`, `glicko`, `goblin`, `goblin chess`, `hikaru`, `kava`, `king`, `knight`, `leet`, `lenny`, `magnus`, `newbie`, `opening`, `patch`, `pawn`, `pin`, `pony`, `positional`, `queen`, `r`, `record`, `records`, `resign`, `rook`, `sicilian`, `skewer`, `stalemate`, `theory`, `thursday`, `tilt`, `update`, `vibes`, `zugzwang`. The
Konami code works anywhere. Opening the fun-sort menu three times unlocks a
joke sort. On the day of a club night the header reads TONIGHT; a profile shows
a note on the player's club anniversary, at exactly 64 games, and at 1337.

On the way in: a one-liner on about one visit in six, and the chess goblin
shouting CHYEEEEEEECK on about one in twenty-five. The page is a static file with
no server, so there is no shared tally to increment; flat odds give the same
club-wide rate without anyone's browser phoning home.

Sixty-two of the eggs are huntable, listed in `EGG_IDS`. Finding one appends
"Easter egg N of 62" to its toast and records it in this browser, and the
Achievements section leads with an Egg hunter tile showing progress. It is the
only entry there that describes the viewer rather than the player, so it says so
and is styled apart. Passive ones (the goblin dropping in, a quip on the way
past) are not in the count: you cannot hunt something that hunts you.

The Konami code needs a keyboard, so phones get the same sequence as swipes.

A dim unlabelled dot at the very end of the footer gives one hint per visit,
always for an egg this browser has not found, phrased as a nudge. Hints live in
`HINTS`, one per id, and the build asserts every id has one.

**The club plays on Sundays** (76 of the 78 nights on record). Copy used to say
Thursday in five places; typing `thursday` now politely corrects you.

Club records live at `#/records`, linked from the footer.

## Rules the data follows

- **Visitors count.** A one-off visitor never joins the ladder, but the games
  regulars play against them do count. Dropping them at import once deleted 39
  real games. `reimport.py` keeps every game; `buildsite.py` flags anyone not on
  the roster with `"gh":1` and the page hides them from every board while still
  counting their games, their ratings and the night's standings.
- **A bye is half a point** on the night, the way the club's own Swiss standings
  score it.
- **Two Omars.** Plain "Omar" is Omar Cruz, except on a night where Cruz is
  already written out in full ("Omar og"), when the bare name is Omar Azab.
  17 May 2026 is the only night both played.
- Verified: all 131 tournament player-scores match the site's own running
  points, and all 169 workbook player-scores match the spreadsheet.

Refreshing data: `extract.py` reads the Chess Ranking Assistant workbook on D:,
`tourneys.py` scrapes SwissOnlineTournament, `roster2.py` rebuilds roster.json.
