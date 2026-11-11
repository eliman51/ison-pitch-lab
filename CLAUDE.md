# Ison Pitch Lab

Eli's own free real-time voice pitch app for learning to sing, built to replace the paid Pitch
app (Coda Labs) and to practice Orthodox chant. He plans to keep building it long term.

Eli is not a programmer. Explain changes in plain words, tell him what to try on his phone,
and walk him through any GitHub step one tap at a time. Never use em dashes in anything
written for him.

## Where the app lives

- **The real app is this repository's `index.html`, served by GitHub Pages** at
  https://eliman51.github.io/ison-pitch-lab . Eli saved that link to his phone's home screen.
  Pushing to `main` updates it (give Pages a minute or two). `sw.js` caches the app so it opens
  offline; bump `CACHE` in `sw.js` when a change must reach phones that are offline-first.
- **Claude artifact copy** (secondary): slug `655d6f80-fa5f-4f8c-a69d-50d7c5e337d4`
  (https://claude.ai/artifact/DWz83P6dcQQaiUpjZ8KrfM). Same page with the artifact's own
  `<head>`. `python3 tools/artifact.py` builds it into `dist/artifact/`; publish with the
  Artifact tools (`publish_files`, slug + base_version, files index.html and the three mp3s).
  An older copy, slug `fe7c326a-...` (Nov 2), is out of date; ignore it.
- This repository is **public** (GitHub Pages on a free account needs that). Nothing private
  goes in it: no keys, no personal data.

## Files

- `index.html` the whole app, one page (about 8,000 lines). Search it; do not read it whole.
- `psalm23.mp3`, `psalm23-tone4.mp3`, `chant-forever.mp3` recordings built into the app.
- `p23.bin`, `bzm.bin` data the page loads (`PRIV` in index.html).
- `sw.js` offline cache. `tools/check.py` must say OK before every push.

## What Eli wants from it (keep these in mind for every change)

- A beginner learning to sing. Gamified beginner lesson plan with timed sessions (2 to 30
  min); a roughly 6-month path from beginner to simple melodies. He works the first few stages
  for weeks before expanding.
- **Ears-only practice**: most practice happens in his loud shop with headphones, unable to
  look at the phone. Anything that needs eyes on the screen is useless there.
- Goal song: Psalm 23 "Mshiho Natareh L Idtokh" (Tone 3), sung with extreme precision within
  about a year, starting with the opening. Also Psalm 23 Tone 4 (mostly in Loop a part),
  Psalm 91/121 (Tone 7), especially its "hallelujah", sung exactly like the singer, and
  memorizing Psalm 118 octave by octave, later as a very long all-day song.
- He has the singer's permission to use the Psalm 23 recordings (Tone 3 and Tone 4). Keep them
  built in and unlocked, no passwords.
- His voice is lower than the Psalm 23 singer's: songs need a lower-key option.
- Sung words in English, ideally from published sheet music; any Eastern Orthodox English
  source is fine. Chants worked in Western notation; Byzantine scales are loved and practiced
  alongside the fundamentals, with real documented melodies for ears-only drills.
- **Chant Maker**: turns his recorded reading of a psalm into a chant on a chosen scale and
  melody, every word matched to its place, karaoke view, audio cleanup, save as song. Total
  quality; the aim is to help people who do not know how to turn psalms into songs.
- Look: the Sketchbook (notebook) design from his Shop Board.
- He has asked about putting it on the Apple App Store.

## Every change

1. Edit `index.html` (or the other files).
2. `python3 tools/check.py` must say OK.
3. Commit with a plain message and push to `main`. Tell Eli what changed and what to try.
4. Only if Eli wants the artifact copy current: `python3 tools/artifact.py` and publish it.
