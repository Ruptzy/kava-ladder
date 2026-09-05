# Adding player photos

Two ways. Harold crops by hand with the tool; Opus uses the script.

## The crop tool (Harold, this PC only)

    python build/photoserver.py
    open http://localhost:8765/build/photos.html

Pick the player, paste (Ctrl+V) or drop the picture, drag it, zoom with the wheel, Save.
**Pasting straight from the clipboard works** — this is the way in for a picture that
only exists in a chat or a browser tab, with no file on disk.

"Publish all saved photos" commits `photos/` and pushes. The tool only works on this
PC with that server running; the public site has no cropping anywhere.

## The script (Opus)

Harold posts one picture at a time and says whose it is. For each one:

1. Save the picture to a temp path (any format; phone photos with EXIF rotation are fine).
2. From the repo root:

       python build/addphoto.py "Player Name" C:/path/to/picture.jpg

   The name must match `build/roster.json` exactly (case doesn't matter). If it doesn't,
   the script prints the closest names; pick the obvious one, ask only if it's ambiguous.
   Face not centred? Add `--focus 0.55,0.25` (x,y as fractions; y small = face near top).
   Face small in a wide shot? Add `--zoom 0.5` (crop side as a fraction of the shorter side).
   Look at the result (`photos/<slug>.jpg`) before pushing; redo with different numbers if needed.
   Leave `--zoom` off (or 1) unless the face is tiny: the default keeps the whole frame,
   which is how Harold wants them — board in shot, not a tight head crop. Only a file
   path works here; an image pasted into the chat never reaches the disk, so hand those
   to the crop tool instead.

**Two people share a first name** on the roster (Brian / Brian O). Ask which one rather
than guessing; a wrong face on a real person's profile is public and obvious.
3. Commit and push just the photo:

       git add photos && git commit -m "Photo: Player Name" && git push

No rebuild needed. The page requests `photos/<slug>.jpg` by name and shows the
initial until a file exists. Slug = lower-case, non-letters become `-`
("Sam (mama Smurf)" → `sam-mama-smurf.jpg`, "Beltran, Lyon" → `beltran-lyon.jpg`).

Replace a photo: run the same command again. Remove one: delete the file, commit.
Check after about a minute: https://ruptzy.github.io/kava-ladder/photos/<slug>.jpg

Where photos appear: profile header (large), podium, ladder rows, compare bar.
The repo clone on this PC is `D:\Desktop_Moved\Chess\kava-ladder` — `git pull` first.
