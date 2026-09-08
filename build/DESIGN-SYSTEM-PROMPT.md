# KAVA Social Chess Club — visual system

Paste this whole file into a new chat before asking for any page, component or
graphic. It is the design system the club ladder already uses
(ladder.kavasocialchessclub.com), written out so a second site matches it.

---

## What this club looks like

Dark, warm, a little bit fight-night. The ground is near-black, the text is
cream rather than white, and there is exactly one loud colour: a scarlet red.
The feel is a dim bar with a spotlight on the board — not a SaaS dashboard, not
a chess.com clone. Confident, physical, slightly theatrical.

The club is a **social community that happens to play chess.** Every design
decision should read as welcoming first and competitive second. If a layout
starts to feel like a rankings product, it has gone wrong.

---

## Palette — use these exact values

### Ground and surfaces

```
--void:      #0C0D0E   page ground (near-black, faintly blue)
--panel:     #161719   cards, boxes
--panel-2:   #1E2023   raised / hovered / neutral fill
--panel-3:   #262A2E   highest surface, chips
--rule:      #24282C   hairline dividers
--rule-2:    #343A40   visible borders, section underlines
```

**Elevation is surface steps, never shadows.** On a dark ground a drop shadow
is invisible; a lighter panel reads as closer. Go up the panel scale to lift
something. Shadows are only ever used as a coloured glow (see Scarlet).

### Ink

```
--cream:     #FFF6E8   primary text          18.2:1 on void
--ink-2:     #B3ABA0   secondary / body copy  8.6:1
--ink-3:     #8A8276   labels, captions       5.1:1
```

**Three levels, no more.** Cream, not white — pure white on near-black glares
and reads cold and clinical. The cream is warm enough to sit with the red.

### Accent

```
--scarlet:      #FE273A   the one loud colour     5.2:1 on void
--scarlet-dim:  #B01523   pressed / darker edge
--scarlet-wash: #1F0F12   tinted fill behind scarlet content
```

Scarlet is **identity only**: the logo glow, links, focus rings, the second
half of a section heading, the active state. It is never a data value and never
means "bad". Reserving it is what makes it work — the moment red also means
"loss", the brand colour stops signalling anything.

The logo carries a coloured glow rather than a shadow:
`box-shadow: 0 0 46px -8px rgba(254,39,58,.75), 0 0 0 1px rgba(255,246,232,.14)`

### Data meaning — the important rule

```
--gain:       #3BC79A   up, won, positive      9.1:1 on void
--gain-wash:  #0F211D
--loss:       #F0883E   down, lost, negative   7.7:1 on void
--loss-wash:  #231810
```

**Negative is orange, not red.** Two reasons, both load-bearing:

1. Scarlet is already the brand colour. If red also meant "you lost", every
   logo and link would read as a warning.
2. Red/green is the single worst pair for colourblind viewers — roughly 8% of
   men cannot separate them. Orange/green stays distinguishable across every
   common form of colour blindness.

Never encode meaning in colour alone. A number that is down gets the orange
**and** a ▼ and a minus sign.

### Metals — podium and awards only

```
gold:   #E8C047      silver: #C9CDD2      bronze: #C2793F
```

Desaturated on purpose so they sit behind the scarlet rather than competing
with it. Use for 1st/2nd/3rd markers and nothing else.

### Sequential scales

When you need a ramp (a heat map, an intensity), build it as **paired
background and foreground steps** so text stays legible at every stop — do not
fade one colour toward the background.

```
win   1→4   bg #132520 #153328 #18452F #1B5A3A
            fg #4FBE96 #5CD0A4 #72E2B6 #93F3CC
loss  1→4   bg #281B12 #33200F #43290F #573510
            fg #D0803F #E0904A #F0A25C #FFBA78
level       bg var(--panel-2)  fg var(--ink-2)
```

Every pair above clears 5.4:1. If you extend a ramp, check the new step.

### Contrast floor

Everything ships at **WCAG AA (4.5:1)** for body text. The values above are
measured, not estimated. `--ink-3` on `--panel-2` is 4.3:1 — that one is for
large text and non-essential labels only.

---

## Type

```
--fd: "Archivo", system-ui, sans-serif           display / headings
--fb: system-ui, -apple-system, "Segoe UI",      body
      Roboto, sans-serif
--fm: "JetBrains Mono", ui-monospace, Menlo,     numbers, labels, data
      monospace
```

**Archivo is a variable font and the variation is the point.** Headings are
set uppercase and stretched wide:

```css
font-variation-settings: "wdth" 110, "wght" 800;   /* common heading */
font-variation-settings: "wdth" 118, "wght" 900;   /* section heading */
font-variation-settings: "wdth" 98,  "wght" 900;   /* tight, when space is short */
```

Width 98–118, weight 700–900. Wider reads as louder; narrow it rather than
shrink the size when space is tight.

**Every number lives in the mono font.** Ratings, scores, dates, counts,
table cells. Tabular data that is not monospaced will not align, and this club
is built on numbers lining up. Mono is also used for small uppercase labels at
`.6rem` with `letter-spacing: .11em`.

Body is 15px / 1.5 in the system sans. Fluid headings via clamp:

```css
font-size: clamp(2.1rem, 8vw, 4rem);      /* hero            */
font-size: clamp(1.15rem, 4.2vw, 2.5rem); /* page title      */
font-size: clamp(1.15rem, 3vw, 1.6rem);   /* section heading */
```

### Heading pattern

Headings are two-tone: plain cream, then the key word in scarlet.

```html
<h2>The <span>whole story</span></h2>   <!-- span is scarlet -->
```

Section heads sit on a `2px solid var(--rule-2)` bottom border with an optional
small mono caption pushed to the right (hidden below ~700px).

---

## Layout

- Content column `max-width: 1080px`, padding `clamp(.95rem, 3vw, 2rem)`.
- Prose measure `max-width: 64–66ch`. Never run body text the full width.
- Corners are nearly square: `border-radius: 3px` for boxes, `50%` for avatars.
  This is not a rounded, friendly-SaaS look.
- Wide content (tables, charts) scrolls inside its own `overflow-x: auto`.
  **The page body must never scroll sideways.**

### Background

A photograph sits behind everything, held down by a gradient so text keeps its
contrast:

```css
html { background: var(--void) url(bg.jpg) center top/cover no-repeat fixed; }
body { background: linear-gradient(rgba(12,13,14,.8), rgba(12,13,14,.89) 32%,
                                   rgba(12,13,14,.94) 62%, rgba(12,13,14,.97)); }
@media (max-width: 900px) {
  html { background-attachment: scroll; background-size: 180% auto; }
}
```

`fixed` attachment is dropped on mobile — it is janky and expensive there.

---

## Non-negotiables

**Phone first.** Check every layout at **375px and 320px**: no horizontal
overflow, no clipped text, tap targets 40px or larger. Most of this club reads
the site on a phone in a bar.

**Plain, short words.** No jargon, no marketing voice. "Play a night and you
are back", not "Resume participation to reactivate your profile". Short
sentences. Cut before shipping.

**Accessibility is part of the design, not a pass afterwards.**

```css
a { color: var(--scarlet); }
:focus-visible { outline: 2px solid var(--scarlet); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
```

Include a skip link, and give every icon-only control a real label.

---

## How to extend this

- **Need another colour?** First ask whether ink levels or a panel step would
  do. Adding a hue costs more than it looks like it does.
- **If you must add one:** keep it out of the red/orange/green space that is
  already spoken for, check it clears 4.5:1 on `--void` and on `--panel`, and
  give it a `-wash` partner at roughly 8–12% chroma for filled states.
- **Never** use scarlet for a data value, or red for a negative one.
- **Never** rely on colour alone — pair it with a glyph, a sign or a label.

---

## Voice, for anything with words in it

The club came together in 2021, after COVID, at Kava Social in downtown
Bradenton. Harold Gonzalez took it over when the original organizer stepped
away and grew it into cooperative learning, study nights, FIDE Master lectures
and simuls, and rated events for whoever wants them. **The league, the ladder
and the brackets all came later — they grew out of the club, not the other way
round.**

So: welcoming before competitive. Nobody is turned away for being new or rusty.
It has never been about who is best in the room.
