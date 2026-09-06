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

## The phone pairing tool

    python buildpairings.py     # writes ../kava-pairings.html

The tool runs the night: check people in, pair each round, enter results, then
either copy the results for Discord or publish the whole site from the phone. It
carries the same page template as `buildsite.py`, so the ladder it publishes is
the identical page, plus the roster, seeds and history it needs to pair and to
replay ratings offline. People in `hidden.json` are left out of both.

It was built by hand until now, which is how it drifted. Rebuild it whenever the
roster changes; `buildpairings.py` and `buildsite.py` are then guaranteed to
agree, which is checked by comparing all 91 players' ratings from the two
builds.

Two things the hand-building hid. The tool paired on the roster file's hand-kept
numbers, up to sixty points behind the replayed ones, so it now pairs on the
replayed rating. And Brad, Jenny and Vinny had no entry in `seeds.json`: the site
build falls back to 1000 for a missing seed, the phone build fell back to
whatever the roster file carried, so the ladder came out a few points different
depending on which one built it. They are now seeded at 1000 explicitly, which
is the number the site had been using all along, so nothing published moved.

### Season prizes

The prizes are gift cards Harold hands out, so eligibility is money rather than
a scoreboard argument. It is **half the season's nights, rounded up** -
`seasonMinNights()` in the pairing template. Cade finished top of U1400 on two
nights of six while Omar Cruz played all six; without the rule the card went to
Cade.

Everybody who played still appears on the season card and in the write-up,
marked with their night count. Not winning a card is no reason to be left off
the season. The rule is stated in the Discord post rather than left for somebody
to discover when they do not get one.

### Dialogs

The tool draws its own (`ask()` / `say()`), and must. `window.confirm()` returns
false instantly without drawing anything in the browser this runs in, so every
action behind it was a silent no-op - Delete round, Re-pair and Clear scores all
looked broken when in fact nothing could get past the guard. `alert()` failed the
same way in reverse: warnings nobody ever saw. There are none of either left.

### Submitting a night

**Submit the night** is the one button the evening ends on, and it does the
whole thing:

1. saves the night to the club record,
2. publishes the website,
3. posts to Discord,
4. clears the board.

That order is the only one that works, and getting it wrong is what made Submit
and the old Finish button contradict each other. The site is built from
`HISTORY`, so tonight has to be filed before it is built or the site goes out
without it. The Discord post is built from `rounds`, so the board can only be
cleared once the post is away.

If publishing fails the night is unfiled, nothing is sent, and the board is
exactly as it was. If posting fails after publishing worked, the night stays
saved, the site stays live, and the board is deliberately **not** cleared so the
post can be retried from Other options.

The confirmation shows the date, the rounds, who played, a red warning for any
board with no result, the full standings to check against the actual board, and
those four steps with the real URL and which of the three posts it will send.

The standings screen has three buttons and no more: Submit, Save file, Load
file. Publish-only, post-only, copy-as-text, save-the-page and
save-without-publishing are gone - each was a fallback for a step Submit already
does, and nine ways to do one thing is worse than one.

The one thing they usefully covered was retrying a post after Discord refused.
`submitStage` holds that instead: press Submit again and it sends the post
alone, without refiling the night or republishing a live site.

Nothing waits forever. `withTimeout()` caps publishing and posting at sixty
seconds each, because a phone that loses signal mid-upload leaves fetch hanging
until the tab is closed, which looks exactly like the app having frozen. The
status line carries a spinner while it works and the error names what failed and
what is still true: whether the night was saved, whether the site went up, and
whether the board was cleared.

### One button, three posts

`postAuto()` works out which post the night calls for and the button says which
before it is pressed.

* **Tonight's results** on a normal night.
* **The halfway update** once the season reaches `seasonShape().mid` nights -
  floor of the expected length, because rounding up put it on night four of six.
  It fires once per season and remembers that on the phone, so a reload does not
  offer it again.
* **The season finale** when the next night due would land in the following
  season, which is knowable on the night rather than after waiting to see if
  anybody turns up.

The expected length of a season is its window over the club's usual gap between
nights, so none of it is typed in.

The halfway post is the one that changes behaviour: it names, per bracket,
exactly who is short of the nights a gift card needs and how many are left.

### Posting to Discord

No bot. A Discord incoming webhook is a URL for one channel: POST to it and the
message appears. Nothing to host, no token to keep alive, no process that has to
be running when the club is not, and Discord allows the request from a browser,
so the phone posts directly. Server Settings -> Integrations -> Webhooks -> New
Webhook, point it at the channel, Copy Webhook URL, paste it into the tool's
settings.

That URL is a password in URL form - anyone holding it can post into the channel
- so it is kept the way the GitHub token is: typed in on the phone, in
`localStorage` under `kava.discord`, never in anything published.

The post leads with a picture: `nightCanvas()` draws the night's leaderboard on
a canvas - one section per bracket, medals on the top three, the club's colours
and the logo - and it goes up as a PNG attachment, which is multipart rather
than JSON. A phone cannot screenshot a page from inside it, and a
DOM-rasterising library would mean fetching a script from a CDN, which would
break the one thing the tool has to do: work on a phone with no signal.

If the drawing or the upload fails, the same standings go out as embeds instead,
one panel per bracket. A picture is nicer; a missing result is not acceptable.

The round by round boards follow as plain text. Discord stops at 2000
characters, so that is split on round boundaries, each piece inside a code fence
so the columns survive Discord's proportional font. A 429 is honoured with the
`retry_after` Discord gives. The site link goes last, if the website is set up.

### Known rough edges

A night in progress is saved to `localStorage` **with its own copy of the
roster**, so that the list cannot shift under you mid-pairing. The effect is
that a saved night keeps showing the roster as it was until that night is
cleared. That is the right trade, but it is why a rebuild can look like it did
nothing.

The PIN gate is a speed bump, not a lock: it is client-side, and the file is
served from the same public site as the ladder. Nothing can be published from it
without the GitHub token, which Harold types in and which lives only in his
phone's storage.

## Seasons and the vault

A season is three months, anchored in `buildsite.py` on season 9 opening
1 June 2026. Everything else counts off that in three-month steps, so the club
rolls into season 10 on its own the first night anybody plays in September.

The ladder is one season. The vault is every night before it. Ratings are built
from **both** - Glicko needs the whole run to know what anybody is worth, and a
six-night season could never settle a rating on its own - but the games, records,
trophies and achievements on the board are the season's. A player who missed the
season keeps their rating and their page and is not on the board.

Two places have to remember the vault exists or they quietly lose 813 games: the
All time table, which adds seasons 1-7 to the vault to the season, and the club
history page, which draws all three eras off the same per-night rows and so needs
`D.vault.tl`. Both are covered; the totals on the history page are the check
worth watching, since they should always say 3,166 games over 88 nights until
somebody plays again.

## Where the games come from

Three importers, all writing `history.json`:

`extract.py` reads the club workbook, which is where most nights come from.
`reimport.py` re-reads the 2026 tournament pages, because the workbook import
had dropped every game played against a one-off visitor. `gap2025.py` reads
every tournament link the club has for December 2024 to October 2025 and is the
authority for those nights: it adds the ones nobody had imported and rewrites
the ones already on record, which only ever changes a spelling because the game
count has to match first or it stops.

Its `LINKS` table holds the date for each tournament rather than trusting the
title, because the club names them by hand and gets it wrong: two are titled
"1/19/24" and "2/2/24" but land on the club's fortnightly Sundays in 2025, and
neither of those days in 2024 was a Sunday. 24 November 2024 is in `ARCHIVED`
and deliberately left out - it is the last night of seasons 1-7 and already
counted there.

Byes are half a point on the night, so a missing bye moves a placing. The
workbook carries none, which means the nights that came only from it still have
none; the tournament pages do. Anything imported from a tournament page is
checked against that tournament's own standings, player by player, before it
goes in.

## People who have left

`hidden.json` lists anyone who has left the club and is not to be listed.
`hide.py "Name"` adds someone and clears them out of the roster and the old-era
table in one go; `hide.py --show "Name"` reverses it; `hide.py` on its own says
who is hidden. Rebuild afterwards. Their
games stay in `history.json` and in the rating replay, so nobody else's rating,
record or game count moves; what changes is that `buildsite.py` swaps the name
for a neutral label before writing the page, so the name is not in `index.html`
at all - not in the ladder, not in an opponent list, not in the bracket
snapshots, not in the seasons 1-7 table, and not in the data blob for anyone
reading the source. Their seeds stay in `seeds.json`, because the replay still
needs them and nothing in that file reaches the page.

The page prints them as "Visitor". The number in the label only exists to keep
them apart as data, and `anon()` strips it everywhere a name is shown; a profile
that met more than one of them shows a single Visitors line rather than a column
of identical rows. Taking a name back out of `hidden.json` and rebuilding undoes
all of it.

A name is only merged when the club's own records merge it, and `SPLIT` in
`gap2025.py` keeps two people apart where a first name is shared: the Anthony on
the winter 2024 nights went 2-10 and lost to Maddie, Taylor and Amanda, while
the Anthony who joined in April 2026 is the third strongest player in the club.
Everyone else who appears on both sides of the gap scores within a few points of
their usual rate, which is the check worth running before merging a name at all.
24 November 2024 is the one night held by both the old records and a link, so
the two naming systems can be lined up by the games themselves; that is what
settles plain "Sam" as the Sam who is still playing. "Bejamin" is Benji
and plain "Omar" is Omar Cruz before January 2026, but "Ben (new)", "Codi" and
"Shawn" stay as written: the club has always used a "(new)" suffix for a second
person with the same first name, and the old workbook keeps Codi, Cody and Cody
(she) apart. Anyone with no appearance in either era stays a visitor, which the
build handles by their absence from `roster.json`: their games count, and they
never join the ladder.

Bracket tabs are art: `tabs/all.png`, `tabs/over-1400.png`, `tabs/u1400.png`,
`tabs/u1000.png` (the file name is the bracket slugged). The wording is part of
the picture, so the button text is kept for screen readers and hidden on screen.
If any panel is missing the tabs fall back to plain text buttons.

Podium cards live in `podium/1.png`, `2.png`, `3.png`; the circle position for
each is set per card in the CSS, measured off the art.

Achievements: 71 of them, defined in `ladderbuild.js` (search `var ACH=`).

Each one carries the night it was earned (`achWhen`), and a profile leads with a
feed of the last three nights' worth. `playerAsOf()` rebuilds only what the tests
read and winds the career totals back by whatever the season did after that
night, which is what makes a career achievement land on the right night instead
of the first one. Anything already true before the season shows as earned
earlier rather than dated; that night is in the vault.

The dated milestones panel is gone. Seventy-one achievements with progress cover
everything it listed and a good deal it did not, and two panels saying
overlapping things was one too many.

**They count a career, not a season.** Scoping the ladder to one season killed 44
of them outright - six nights caps everybody at six nights and about thirty
games, so "turn up to ten nights" and "play fifty games" were unreachable by
arithmetic. `career_stats()` in `buildsite.py` counts every night the club has a
record of, seasons 1-7 included, mapped through the same link the All time table
uses; `achCtx()` reads those for anything that accumulates. Form stays seasonal -
trophies, promotion, the climb, how much of the current field is left - because
form is seasonal, and those thresholds are sized for six nights rather than
thirty-three. Each
has a stable id which doubles as its icon file name, `achievements/<id>.png`;
see `achievements/README.md` for the full list. Missing icons fall back to an
emoji, so art can be added a few at a time. Most are about turning up, variety and effort rather than strength, and unearned
ones stay on the profile with their progress. Thresholds are deliberately steep:
a new player with one night earns one or two, a regular around a dozen, and the
club's busiest member 53. Five are still unearned by anyone: they are the
long-haul ones (150 and 200 games, 100 wins, forty different opponents, two
years between first game and last).

## Byes

They come from the **standings** page, not the pairings page, and each is stored
with what it was worth: `[name, points]`. The club's software writes two things
the same way. `=BYE` is a requested half-point bye and appears as a row on the
pairings page. `BYE` means simply "not paired", and does not appear there at all
- so it looks like a missing bye when it is usually somebody who had not arrived
yet or had gone home. A `BYE` only scores a point when there is real play on
both sides of it.

That rule reproduces the club's own standings for 282 of 283 player-scores. The
one exception is Gabe on 16 August, credited 4.0 where his four games account
for 3.0 and his only bye is a leading one; every other leading bye in the club's
history scored nothing. Worth asking Harold about rather than coding around.

## A bye is a whole point

From September 2026, a bye scores 1. That is Harold's ruling and what the
pairing tool has always done. Nights before `BYE_FULL_FROM` in `ladderbuild.js`
keep the half point they were played with: the club's own tournament pages
scored a bye at a half, and those nights were checked against them score by
score, so rewriting them would put the record out of step with the source it
came from. `gapcheck.py` follows the same rule.

Trophies live in `trophies/1.png`, `2.png`, `3.png` (transparent PNGs, 240px).
Counts are worked out in the page: each club night, players who played at least
three games are ranked against the rest of their bracket, and a top-three finish
becomes a trophy. Ties share the place. The bracket used is the one the club
had the player in on that night, read from the workbook snapshots in
`divhistory.json`, so cups won on the way up stay with the division they were
won in. The earliest snapshot is 30 November 2025; nights before it fall back to
the player's bracket today, which is worth remembering for the early 2025
nights, where a bracket can come down to one or two people.

The bracket is the rating band, worked out per night rather than kept by hand.
The numbers come out of the division names, so "over 1400" floors at 1400 and
renaming a bracket keeps working. `divhistory.json` is no longer read for
trophies: the hand-kept sheets drifted five months behind the ratings and were
putting U1400 cups on a rating of 927.

**Your bracket is fixed on your first night of a season and holds.** Break your
section's ceiling mid-season and you still play for its prize, then move up when
the next season starts - Harold's own practice, and the only version that does
not punish improving. Sonny is why: he entered Season 9 on 942, played every
night, climbed to 1045, and a mid-season move would have handed his cups to a
bracket where he finished third and won nothing.

Nothing moves inside a season, so nothing can be moved by losing on purpose
inside one. Across seasons the floor is **what you averaged last season**, not
what you peaked at (`window_level`, `SEASON_LOOKBACK`). An average rather than a
peak, deliberately: a peak promotes somebody on one good night and then holds
them there - Sonny touched 1024 once, finished the season on 942, and was being
kept out of the bracket he belonged in. An average is also the harder of the two
to fake. You can tank a finishing number in a fortnight; you cannot tank a
season's worth of them, so somebody who spends a season at 1300 and dumps the
last two nights still averages about 1250 and stays where they are.

`season_bands()` in `buildsite.py` works this out once and both pages read it.
The site used to derive it from the shipped ratings and the phone from the
roster, and they had already drifted - two implementations of one rule is the
failure this project keeps finding. Your bracket is the
highest band your rating has reached this season, so losing games on purpose at
the end of one cannot drop anybody into an easier bracket to collect its
rewards. It does not reset at the season boundary either, which is the whole point: the
ratchet alone only stopped the fast sandbag, losing on purpose in the last week
to take that season's rewards. The patient one - tank the end of a season so the
next opens in an easier bracket - needed the floor to look back a season too.
Falling out of a band now takes two full seasons of playing below it, six months
at three months a season, by which point nobody is sandbagging; they are just
that player now. A newcomer's seed sets no
floor: it is a number somebody typed, not a rating anybody has tested, so their
floor starts at their first real one. Vinny is why that clause exists - seeded
1000, plays like 695, and was being held in U1400 by the guess.

A bracket of one still awards the cup. Harold's call, asked and answered: you
turned up and nobody in your bracket outscored you. Fifteen of the cups on the
board are won that way, five of them Omar Cruz's. Do not quietly add a minimum. The
header shows the strongest division a player has won in and lists anything below
it underneath. The page template is the
`ladderTemplate()` function in `ladderbuild.js`; the same file is spliced into the
phone pairing tool so both builds produce the identical site.

Page JS inside the template must use string concatenation, never `${}`, and no
backslashes except the closing `<\/script>`.

## Easter eggs

Seventy huntable ones, all hanging off things people already touch, none
blocking a tap meant for navigation. Search `easter eggs` in `ladderbuild.js`.

Tap: the club badge (knight hops), the seasons tag, the updated line, the word
"Ladder" in the heading (it renames itself), the wiggle-room symbol, a profile's
rating (counts up from the seed), its record (cycles to percentages), a trophy
(spins), the portrait (shows a spirit piece), the turnout blocks (ripple), and a
crosstable diagonal cell. Also the Last night heading, the search magnifier,
the EARNED label beside the achievements, and the footer itself.

Type into search (62 words, `but harold` among them): `1337`, `backgammon`, `beginner`, `bishop`, `blitz`, `blunder`, `brilliant`, `bullet`, `castle`, `castling`, `cheat`, `checkers`, `checkmate`, `chess goblin`, `clock`, `d4`, `draw`, `e4`, `e5`, `elo`, `en passant`, `endgame`, `engine`, `enpassant`, `fork`, `gambit`, `glicko`, `goblin`, `goblin chess`, `hikaru`, `kava`, `king`, `knight`, `leet`, `lenny`, `magnus`, `newbie`, `opening`, `patch`, `pawn`, `pin`, `pony`, `positional`, `queen`, `r`, `record`, `records`, `resign`, `rook`, `sicilian`, `skewer`, `stalemate`, `sunday`, `theory`, `thursday` (wrong day), `tilt`, `update`, `vibes`, `zugzwang`. The
Konami code works anywhere. Opening the fun-sort menu three times unlocks a
joke sort. On the day of a club night the header reads TONIGHT; a profile shows
a note on the player's club anniversary, at exactly 64 games, and at 1337.

On the way in: a one-liner on about one visit in six, and the chess goblin
shouting CHYEEEEEEECK on about one in twenty-five. The page is a static file with
no server, so there is no shared tally to increment; flat odds give the same
club-wide rate without anyone's browser phoning home.

The seventy huntable eggs are listed in `EGG_IDS`. Finding one appends
"Easter egg N of 70" to its toast and records it in this browser, and the
Achievements section leads with an Egg hunter tile showing progress. It is the
only entry there that describes the viewer rather than the player, so it says so
and is styled apart. Passive ones (the goblin dropping in, a quip on the way
past) are not in the count: you cannot hunt something that hunts you.

The Konami code needs a keyboard, so phones get the same sequence as swipes. It
is four steps, up-up-down-down, because nobody finishes ten.

**Hints.** The dim unlabelled dot at the end of the footer gives one hint per
visit, always for an egg this browser has not found, and it nudges rather than
tells. `HINTS` carries a line for every id in `EGG_IDS`; the build asserts none
is missing.

**Who you open.** `openingEggs()` fires at most one egg on a profile, chosen by
who that player is: the club's number one after a night they dropped a game, the
last ranked name on the board (warm, because a real person reads it), the newest
arrival, whoever has faced the most different people, and anyone sitting within
five points of somebody else. Each is behind a probability so it stays a find
rather than a fixture.

**But Harold.** The study-night catchphrase, in three places. Typing it gives the
objection, then the toast rewrites itself with the deeper motif. It also turns up
uninvited on about one visit in seventeen. The real one hangs off the data: any
profile with a night where they won more games than they lost and still lost
rating points carries a "But Harold..." under the nightly chart, and tapping it
explains that night with its own numbers, opponents' average rating included.
Fourteen players currently have such a night.

Opening the club's number one after a night they dropped a game gets "the bigger
they are"; opening anyone with a winning record occasionally gets a line about it.

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
