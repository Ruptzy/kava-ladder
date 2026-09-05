# Adding player photos

Harold posts one picture at a time and says whose it is. For each one:

1. Save the picture to a temp path (any format; phone photos with EXIF rotation are fine).
2. From the repo root:

       python build/addphoto.py "Player Name" C:/path/to/picture.jpg

   The name must match `build/roster.json` exactly (case doesn't matter). If it doesn't,
   the script prints the closest names; pick the obvious one, ask only if it's ambiguous.
   Face not centred? Add `--focus 0.5,0.25` (x,y as fractions; y small = face near top).
3. Commit and push just the photo:

       git add photos && git commit -m "Photo: Player Name" && git push

No rebuild needed. The page requests `photos/<slug>.jpg` by name and shows the
initial until a file exists. Slug = lower-case, non-letters become `-`
("Sam (mama Smurf)" → `sam-mama-smurf.jpg`, "Beltran, Lyon" → `beltran-lyon.jpg`).

Replace a photo: run the same command again. Remove one: delete the file, commit.
Check after about a minute: https://ruptzy.github.io/kava-ladder/photos/<slug>.jpg

Where photos appear: profile header (large), podium, ladder rows, compare bar.
The repo clone on this PC is `D:\Desktop_Moved\Chess\kava-ladder` — `git pull` first.
