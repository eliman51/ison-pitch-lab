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
- `guitar-steel.m4a`, `guitar-nylon.m4a` the two guitars of the Guitar lab (see that section); `guitar-steel.LICENSE.txt` must stay beside them.
  `tools/guitar.mjs` renders the guitar parts on this Mac with the page's own code; `tools/guitarpack.py` rebuilds the two guitar files.
- `tools/sing.py` sings a notes file from the app with a free voice on this Mac (see "The singer on this Mac").
- `tools/lexicon.mjs` rebuilds the syllable word list inside index.html (not needed for normal changes).
- `tools/scan.py` the deep scan of a recording (words, letters, notes, loud and soft); `tools/heart.py` turns a score
  written by hand into a sung stanza (see "Heart song" and "The Psalm 23 melody on Psalm 118").

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
- **Song Maker** (the Chant tab, was "Chant Maker"): paste any words, pick a melody, and every
  syllable is laid on its note. It plays at once as a tone with karaoke words; a voice (the
  Kokoro computer voice or his own recorded reading, re-tuned onto the notes) is optional.
  His real use: Psalm 118 (Orthodox Study Bible wording, which he has permission to use and is
  lightly changing), almost memorized, sung as one very long song while he works, mostly by
  looping parts. He likes the Arabian (Hijaz, Plagal Second) sound, a steady rhythm, real
  Orthodox melodies where possible, and being able to edit and fine tune. A melody's breath
  may fall in the middle of a sentence or even a word; he said that is fine. Total quality; the
  aim is to help people who do not know how to turn psalms into songs.
- Look: the Sketchbook (notebook) design from his Shop Board.
- He has asked about putting it on the Apple App Store.

## How the Song Maker works (search index.html for these names)

- `chText` / `sgWord`: words to syllables with accents. Spelling rules (`chWordSyl`,
  `chWordStress`) plus `SG_LEX`, the list of words the rules get wrong, built from the CMU
  Pronouncing Dictionary by `node tools/lexicon.mjs <data folder>` (see the top of that file).
  Run it again if the rules change. `SG_LITS` holds church-English overrides (bless-ed).
- `SG_MEL`: the melodies, in a small text notation explained above `sgParse`. "Byzantine,
  traditional" entries were read note by note from published scores (Neanes example scores and
  ilizol's neanes-examples, MIT); never add a "traditional" melody from memory. `sgGen` writes
  new melodies from a number.
- `sgAlign`: lays the syllables on the melody's seats (accents on strong seats, slurs, shared
  notes, upbeats, breaths). `sgPlan` turns that into notes and times; `sgTone` is the tone.
- A long song is loaded into the player a few minutes at a time (`sgWin`, `SG_PAGE`).
- A real singing voice comes from outside the app: `sgScore` + `sgMidi` write the song as a MIDI file with lyrics
  (whole word on its first note, `+` for the word's next syllable, `-` for a held syllable; OpenUtau and
  Synthesizer V both read this), and `sgSungIn` / `sgSungLoad` / `sgSungLay` bring the finished recording back as the
  voice (source `sung`, or `s:<id>` when saved with a chant), lined up by `sgSungAlign`.

## The singing voice (researched November 2026)

Eli finds the Kokoro voice bent onto the notes "distractingly bad". What was found:

- Exact notes and words, best sound: Synthesizer V Studio 2 Pro (about $99 once, Mac, voice ASTERIAN is a bass
  from a trained oktavist). No command line; one manual step per song. Its voice licences have no religious clause.
- Free: OpenUtau with a DiffSinger voice (TIGER is male, personal use only, no re-hosting). Many DiffSinger voices
  forbid religious use (Miyo, Laru Mine); read the terms of any voice before using it. No voice files may go in
  this public repository.
- SoulX-Singer (Apache 2.0) sings MIDI plus lyrics in a voice copied from a short recording, and runs on an Apple
  Silicon Mac. It could sing in Eli's own voice.
- Suno "Cover" sounds the most lifelike but only follows the melody roughly, so it is not for exact practice.
- Nothing good runs on the iPhone or inside a web page yet. A DiffSinger voice could in principle run in the page
  with onnxruntime-web (acoustic model plus vocoder, fed our own phonemes, timings and pitch), loaded from a file
  the user picks; expect it to be slow on a phone.

## The singer on this Mac (set up 13 November 2026)

Everything lives in `~/ison-singer`, outside this repository on purpose: a Python folder (`venv`), the TIGER
DiffSinger voice v106 (`voices/tiger/bank`, from github.com/spicytigermeat/tiger_diffsinger; personal,
non-commercial use, no re-hosting, no religious clause), and `out/` for results.

- `~/ison-singer/venv/bin/python -I tools/sing.py "<song> notes.mid"` writes `<song> sung.wav` and `.m4a`. About
  as long to make as the song lasts. Eli can double-click `~/ison-singer/Sing the newest notes file.command`, which
  sings the newest notes file in Downloads.
- It reads the words and notes from the MIDI, plus the exact church tuning the app hides in it (one private event,
  FF 7F, "ison1:" and the cents for each note), so the sung voice is on the app's own pitches, not piano pitches.
- Words become sounds through the CMU dictionary (`SAY` in the script holds church readings such as bless-id).
  Consonants are sung just before the next note and may take at most 40% of a note (`--cons`). The voice's own pitch
  model gives slides and vibrato, held within 0.3 semitone of the note (`--wobble`), then each note is centred on its
  exact pitch. `--mode` picks the voice colour (vinyl is the default; also fresh, disco, electric, glam, mystic, royal).
- Checked by measurement only (Claude cannot hear): notes average about 6 cents from target, and a speech recognizer
  wrote down nearly every word of the eight test verses. Eli judges the sound.
- The "Plain reading" melodies (`rd1`, `rd2`) are a reading on one note with small rises and dips, written for the
  app, not named traditional tones.

## Melodies taken from recordings (built 13 November 2026)

- `~/ison-singer/venv/bin/python -I tools/melody.py <recording> <words.txt> "<name>"` writes `<name>.melody.json`.
  It lines every letter of the sung words up with the audio (torchaudio MMS forced alignment), measures pitch
  (librosa pyin), cuts it into notes, and writes one seat per sung syllable with all its notes, the singer's own
  pitch ladder (`tun`), note lengths and breaths. The words must be typed exactly as sung; a speech recognizer
  (faster-whisper) gives a first draft that Eli corrects.
- In the app: "Bring in a melody file" (Chant tab, section 2) keeps it on the device (`ison-sg-recs`, ids `rec:...`).
  `p23t3` is the Psalm 23 Tone 3 recording done this way and built in (group "From a recording").
- Known limits: note lengths are rounded to quarter beats and the app sets breath lengths itself, so timing follows
  the singer closely but not to the second; a few stray short notes may remain; the Psalm 23 words used for the
  alignment were heard by the recognizer and lightly corrected by Claude, not yet confirmed by Eli.
- Psalm 118 (22 stanzas, Eli's wording) sits in the repo only as `n118.bin`, locked with `tools/lock.py`; the app's
  app opens it by itself with a key in the page (`NB_KEY`): Eli asked on 13 November 2026 for the passphrase prompt to be removed, so the files are only scrambled, not secret. The same holds for `s118/` (22 finished songs) and `r118/` (22 review stanzas). The plain text is at `~/ison-singer/notebook/`. Never commit it unlocked.

## Reading tones that follow the lines (13 November 2026)

- A melody with `follow` (see `sgFollow`) is built fresh for each text: every line of words is one phrase. `ob6` is
  Russian Common Chant Tone 6 (1869 Obikhod, from the OCA chanting tutorial by Drillock and Ealy: phrases A, B, C in
  turn, cadence from the last inner accent, a Final phrase on the last line). `mcim` is the Metropolitan Cantor
  Institute's minor psalm tone (Byzantine Catholic prostopinije; say so). `rd2` uses a simple formula written for the app.
- Sources: media.oca.org/chanting-tutorial (Tutorial-Common-Tone6-Explanation.pdf) and
  mci.archpitt.org/prostopinije/melodies/Psalm_tones.html. No pitched Byzantine (Greek) reading formula was found.
- Next, waiting on Eli choosing a tone by ear: sing all 22 Psalm 118 stanzas on it at 161 and build the review box
  (22 dots, any selection joined into one song and opened in Loop a part). `window.isonSongRec()` (localhost only)
  hands the practice-song record to the packing step.

## Fit each line (13 November 2026)

- The Song Maker setting "Fit each line" (`s.fit`, `sgFit`) makes a fixed melody take one phrase per line of words.
  Long notes are cut into beats so extra words go there first, then a note is repeated mid-phrase; short lines get
  slurs. No syllable shares a note shorter than a beat. Eli asked for this because at about 190 a minute words were
  being swallowed (two syllables on one short note). On stanza 1 with Monastery (`d2`) at 150% speed: 23 syllables
  under a quarter second before, none after.
- Whole-stanza fitting (`sgFitLines`, 17 November 2026, Eli's request "begin with the end in mind"): the words are cut
  into a whole number of passes through the melody's phrases, so the text always ends on the closing phrase. Before,
  a semicolon, colon or period inside a line started an extra phrase ("I cry out to You; save me" made "save me" its
  own phrase), so stanzas 11, 12, 16 and 19 ended mid-melody and short scraps were drawn out. Cuts prefer typed line
  breaks, then periods, semicolons, commas; never after a little word like "the" or "when". Each piece gets about
  0.85 of its phrase's beats in syllables. Typed line breaks are a preference, not a rule (Eli does not care where
  his breaks fall). Stanzas 10, 11, 12, 14, 16, 19, 20 and 22 of the Monastery review set were sung again
  (`R118M_REV`). `sgFollow` (reading tones) still starts a phrase at a mid-line semicolon.
- Planned next, once Eli approves the sample by ear: sing all 22 Psalm 118 stanzas on Monastery with Fit each line
  (speed about 150%, 189 a minute) and add a melody drop-down to the review box (sets live in `r118/`; a second set
  needs its own folder and a name in the JSON).

- `p118l` "Psalm 118, the long song" (17 November 2026; sung for all 22 stanzas at speed 120 as the review set `r118l/`, about 90 s each): written for the app, Hijaz, 16 phrases = one stanza arc (low opening, rise to the tense 2nd step, high cry from the top Pa, return and sealed ending). With Fit each line each 16-line stanza sings it once and ends home. Not traditional; no melody from David's time survives.

## Heart song: hand-scored stanzas (18 November 2026)

- What Eli asked for: a step above the reading tone, melodic and expressive, but quick (about 45 seconds a stanza, under
  a minute), words at speaking pace, and ONE drawn-out, beautiful moment per stanza placed where the heart of that
  stanza is, tailored stanza by stanza, every syllable decided. He will sing along daily for about a month to
  memorize it. Monastery and the long song stay; this is a third thing. First trial: stanzas 1 to 3 only.
- How: `tools/heart.py` turns a score written by hand (every syllable with its own notes and length; format at the top
  of the file) into the notes file, the practice-song record and a loudness line, sings it with `sing.py`, shapes loud
  and soft afterwards (the voice has none of its own; the range is kept narrow for the loud shop), and writes
  `r118h-N.m4a`/`.json` for `pack118.py ... r118h`. The scores hold the words, so they live in `~/ison-singer/heart/N.txt`,
  not here. Review menu value `r118h`; `R118_HAVE` says how many stanzas a set has.
- The style (written for the app, not traditional): Hijaz on A2, one unit = 0.2 s (a quick syllable), accented syllables
  1.5 to 2 units and often a step higher. Three registers: calm or pleading lines recite on the home note with the
  step below it; affirming lines recite on the fourth; the high point reaches the fifth and sixth, never the octave.
  Lines end by walking down the Hijaz steps to home (the signature close is the half step onto home), or stay open on
  the fourth when the thought continues. The drawn-out word follows the shape measured from the Hallelujah Eli loves
  in the Psalm 91/121 recording (step up, climb, hold, quick flick to the top, stepwise fall, small closing turn, about
  3 seconds). High points chosen: stanza 1 "O Lord" (verse 7), stanza 2 "Blessed are You, O Lord" (verse 12),
  stanza 3 "My soul longed" (verse 20). Eli found the long song's climb too high, held too long and slow to return.
- Eli approved the style by ear on 18 November 2026 ("keep this as a full style") and all 22 stanzas are scored and
  sung (`r118h/`, 46 to 54 seconds each, 18:49 together). Each stanza's score begins with a comment naming its
  high point (4 "enlarged", 5 "Behold", 6 "which I love", 7 "Your name", 8 "mercy", 9 "good", 10 "live",
  11 "help me" as a weeping fall, 12 "Forever" at the opening, 13 "sweet", 14 "joy", 15 "saved", 16 "the Lord",
  17 "shine", 18 "home" landing on the home note, 19 "cry" at the opening, 20 "life", 21 "peace", 22 "overflow",
  and the psalm's last line slow and gentle). Checked by measurement: a speech recognizer heard 91 to 98% of the
  words in every stanza, 99 to 100% of notes within half a step. Crowded words (transgressed, persecute) need 1.5 to
  2 units on their syllables or they blur. To change one spot: edit `~/ison-singer/heart/N.txt`, run
  `heart.py ... --sing`, pack, and give that stanza a new name in the app so phones fetch it (as `R118M_REV` does).
- The review box has two buttons (18 November 2026, Eli's request): "Learn it" builds the picked stanzas and opens them in
  Master a song (`rv118Build('sm')`: unit 6, `smSong`), "Review it" opens them in Loop a part as before. His way of
  working: Master a song first, until he knows a melody by heart, then Loop a part for repetition.
- Eli's long aim (18 November 2026): a library of such styles over the years, master a few, then sing the whole
  psalm himself for YouTube. The TIGER voice is personal, non-commercial, no re-hosting: it teaches, it is not
  what gets published. Melodies written for the app are his to use.

## The Psalm 23 melody on Psalm 118 (18 November 2026)

- What Eli asked for: the deepest possible scan of the Psalm 23 Tone 3 recording (he spent 20 to 25 hours learning it),
  then that same melody rebuilt, stanza by stanza and by hand, on Psalm 118. Quality over time: up to 2 minutes a
  stanza is fine. Stanzas 2 and 11 were the trial; he called them "absolutely beautiful" and asked for the rest, so all
  22 are now set (18 November 2026, 76 to 97 seconds each). He will come back with small changes stanza by stanza.
- The scan: `~/ison-singer/venv/bin/python -I tools/scan.py psalm23.mp3 ~/ison-singer/p23/words.txt ~/ison-singer/p23/scan
  --spoken "tone three" --home 55.82 --ladder 48.72,50.70,51.78,53.84,55.82,56.78,58.80,61.04` writes `scan.txt` (read
  it) and `scan.json`. Pitch is measured twice (Praat through parselmouth, and pyin), laid on the singer's own ladder,
  every letter is placed by the MMS aligner, and each syllable gets its notes, loudness, vibrato and an emphasis mark.
  The words were confirmed by faster-whisper large-v3 (now on this Mac) and small.en: the same words both times.
- What it found. Ladder (steps from the home note G sharp 3, 18 cents flat): -4 = -7.10 half steps, -3 = -5.12,
  -2 = -4.04, -1 = -1.98, 0, +1 = +0.96, +2 = +2.98, +3 = +5.22: a Kurd-type scale (half step above home), no drift.
  The song is nine short shapes, in this order, and the whole order runs twice (about 59 s each):
  `A B A B C D | E H I D | F G D`. Notes per syllable (step:quarter seconds, ~ = silence):
  - A opening: `-4:2.4 | -4:2.2 | 0:2 | 0:1.8 | -1:1.2_0:1 | -2:1.1_-1:1 | 0:2.5 ~1.5 | 1:.9_0:1.2 | -1:1.9_-2:1`
  - B low close: `[-2:1] | -1:1.8 | -2:1.1_-1:1 | 0:.8_1:.4_0:.6_-1:1.6 ~.6 | -2:1_-3:1.05_-2:.95_-1:.8 | -4:2.5 ~2`
  - C middle: `0:1.8 | 1:1_0:.8 | -1:2.5 | 0:2.1_1:1 ~1 | 1:.7_2:.8_1:1.6 | 0:1.5 | 0:2.1 | -1:.8_0:.9 | 0:2.1`
  - D full close: `0:2 (one to three, more when reciting) | 1:1.8_0:.85 ~1.5 | -1:2.3 | 2:.35_1:1.15 | 0:2.2_1:.75_-1:1.1_0:1.75 ~2.2`
    (the last one of a stanza: `0:3_1:.75_-1:1.35_0:2.8`)
  - E second opening: `-2:2.1 | -1:2.3 | 0:1.8 | 0:2.1 | 0:1.1_2:.7 | 1:1.05_0:.8 | -1:.8_-2:1`
  - H the descent: `-1:1.9 | 0:.85_-1:.8 | -2:.85_-3:1 | -2:1.9_-1:.7 ~1.5 | -2:.9_-1:.7 | -2:.5_-3:.45_-4:1.2 | -4:1.7 ~2.2`
  - I the recovery: `-1:.8_0:3.4 | 1:1.8_0:.9 ~1.2 | -1:2.6 | 2:.3_1:.9_0:.4 | 0:1.4 | -1:.7_0:1 | 0:1.6`
  - F the climb: `-2:2.1 | -1:.65_-2:.35_-1:1 | 0:1.1_1:.65 | 0:1.2_1:1 | 2:1_3:.8`
  - G the height: `2:.85_1:.75 | 0:1.75 | 1:.8_2:1.9_1:1.45 | 0:2.05 | 1:2.05 | 2:1.45 ~.85 | 2:.8_0:1.2 | 0:2`
  Heard joins only: A to B; B to A or C; C to D; D to A, E or F; E to H; H to I; I to D; F to G; G to D. The singer is
  softest on H (about 4 dB down), a little soft on B and D, level elsewhere. He often holds little words (of, and, the).
- How a stanza is set: blocks `(A B)+ C D`, `E H I D`, `F G D`, always starting on A and ending on a D with the long
  last close; every stanza has `F G D` at least once (on its plea or praise), H on its darkest line where it has one.
  One shape per half line; a long half line is cut in two, or its extra syllables are recited on the home note at
  the front of D (up to 8), on A's -4 and 0, on E's 0, on B's -1; never two syllables on a short note. Accents go where
  the singer puts his (D: the +1, then the leap 2 to 1, last syllable on the closing figure; a word like "righteousness"
  shares the closing figure). D lands on sentence ends where the words allow. A word may run from F into G ("mer-cy").
  A short half line may use only the first half of G (cells 1 to 4).
- Making one: write `~/ison-singer/p23m/N.s.txt` shape by shape (`tools/shapes.py` explains the notation: `A  My/c1
  soul/c2 ...`, cells of the shapes above); `shapes.py N.s.txt N.txt` turns it into heart.py's notation and warns about
  very short syllables and about joins the singer never makes; then `heart.py ~/ison-singer/p23m/N.txt N <out> --unit 0.25
  --home 51 --scale p23 --set r118p --sing` (home E flat 3, five half steps under the singer, for Eli's lower voice;
  `{t1.06}` at the top because the shapes come out a little quick without the singer's consonant gaps), then
  `pack118.py <out> NB_KEY r118p`. Stanzas 2 and 11 were written straight in heart.py's notation (no `.s.txt`). The
  scores hold the words, so none of this is in the repo. In the app: review menu value `r118p`. If a stanza is sung
  again, give it a letter in `R118P_REV` (as `R118M_REV` does for Monastery) so phones fetch it.
- Checked by measurement, all 22 after the re-laying (81 to 103 s each, 33:48 together): every stanza has 99 to 100%
  of its notes within half a step; a speech recognizer heard 88 to 98% of the words (17 the lowest; most misses are
  near sound-alikes such as "searched" heard as "search"); and laid over the singer's own recording (timing lined up,
  five half steps down) the sung line is within three quarters of a half step of his 94 to 97% of the time. Every join
  between shapes is one the singer makes (shapes.py checks this). The measuring scripts (verify.py, similar.py,
  singall.sh) were scratch files; verify.py's method is the one described under "Heart song".
- Eli is working through the stanzas one at a time, starting at 4, changing each until it is the one version he will
  master. Changes so far (each re-sung stanza gets its letter in `R118P_REV`): stanza 4 `b`: "earth" in the first line
  carries on up to the held home note and ends there, a short lift, then a quick "Give me" on the next two notes (before,
  "Give" was the held note and the th of "earth" ran into it).
  Stanza 4 `c`: from "and I shall meditate" on, rebuilt as `A B | A B | C D | E H | I D | F G D` (86 s; the earlier
  layout is kept as `4.s.v2.txt`). He called it "fantastic" and "very well balanced": it is the model for the rest.
- What Eli wants from every stanza (his words, 18 November 2026): "every part of every sentence and every word is
  intentionally placed", the way the singer's own words each have their spot. It is not about speed: a crowded line
  "doesn't have a place, it's just trying to get past that part". The cure for crowding is another shape (for example
  the opening pair A B again), never a slower tempo; up to about 2 minutes a stanza is fine, but no dragging for its own
  sake. The rules that follow from it:
  1. A sentence ends on a shape that closes and breathes: B, H or D. A, E and F never end one. C, I and G end on the
     home note, so they may end a sentence only with a breath written after them (`~2`), as the song itself does
     ("they comfort me." on G, then "O Lord, protect me" on D).
  2. Sentence pairs the song allows: `A|B`, `C|D`, `E|H`, `I|D`, `F|G D` or `F G|D`; in order `(A B)+ C D`, `E H I D`,
     `F G D`. A long verse takes two pairs, one per half line.
  3. Fullest lines he has approved (stanzas 2, 4, 11): A 11, B 8, C 10, D 11 or 12 (up to 7 recited on the home note
     before the +1), E 11 (recited), H 9, I 10, the climb F 9 one syllable to a note, G 10. Over that, split the line
     across two shapes. Fewer syllables than the singer's own count is fine (a word drawn over several notes).
  4. Word ends: a word's last consonant should fall at the end of a held note with a lift after it, not run into the
     next word on a new long note (the "earth" then "Give" fix).
- All stanzas were re-laid by these rules on 18 November 2026 (`R118P_REV` letter `b`; the first layouts are kept as
  `N.s.v1.txt`). Left as they were: 2 and 11 (he called them beautiful; 2 still closes on "I delight in the way" before
  "of Your testimonies", and 11 runs "help me" on E into H), 9, 19 and 21 (already right). Still fuller than the rule
  and worth his ear: 13 "it is my meditation the whole day long" (B 11), 17 "for this reason my soul searches them
  out" (B 10), 6 "with a word, for I hope in Your words" (B 9). `shapes.py` no longer slows anything by itself; it
  prints "crowded" for a line quicker than 2.3 syllables a second (the climb F always is).
- The singer's pauses (18 November 2026). Eli heard that "the perfect pauses at the right times for the breath" were
  slightly off, and that the pause is often in the middle of a word. Measured in the recording (37 pauses of 0.15 s or
  more; 6 inside a word: shep-herd, e-nemies, bri-dal, fol-low, com-fort, res-tores): the pauses belong to the melody,
  not the words. He pauses at the same cell of a shape every time, as long inside a word as between words: A 0.38 s
  after the held home note (cell 7) and about 0.3 s after the shape; B none after the turn (be-fore, a-noint are sung
  through), half a second at its close; C 0.21 s after cell 4 and 0.24 s after cell 7; D 0.35 s after the +1 0 (cell 1)
  and half a second after the close; H 0.37 s after cell 4; I 0.27 s after cell 2 and 0.18 s after cell 5; G 0.2 s
  after cells 2 and 6; E and F none. His shapes' highest note is mid-word 9 times of 26. His sentences do not always
  end on closing shapes ("name's sake" runs into "Though I walk"); ours are tidier, which Eli likes.
  Our first layouts left a pause out whenever it fell inside a word (about half the pause points in stanza 4, because
  Psalm 118 has longer words) and had small errors (a pause after B's turn, none after C's cell 7 or I's cell 5).
  `#! singer-pauses` at the top of a `.s.txt` makes `shapes.py` use the measured pauses (`REST2`) and keep them inside
  words (`or/1:1.8_0:.85~1.3-di/...` in heart.py's notation). Trial: stanza 4 this way is the review set `r118q`
  (`~/ison-singer/p23m/4q.s.txt`, 89 s), beside the unchanged `r118p` stanza 4, for Eli to compare by ear. If he
  prefers it: add the line to every `.s.txt`, re-sing, give each a new letter in `R118P_REV`, and remove `r118q`.
  Eli's answer on trial B: "definitely better", the breath "a lot better and more natural". So the singer's pauses are
  right; they are not yet rolled out to the other stanzas.
- Trial C (`r118r`, `4r.s.txt`, 95 s, 22 shapes): Eli found the last 30 to 40 seconds of stanza 4 still crammed and asked
  for more of the melody there, even 10 to 20 seconds longer. Verses 29 to 32 went from 9 shapes to 12:
  `C D | E H | I D | F G D | F G D` (half a C for "Remove the way", D "of unrighteousness from me", E "and with Your
  law", H "have mercy on me", I and D for verse 30, the climb for "I cleave to Your testimonies, O Lord", the close
  "do not disappoint me", then the final climb as before). No line now has more syllables than the singer's own lines
  of that shape, and the stanza's rate (1.5 a second) equals the song's. Waiting on his ear; he will then name exact
  words and sentences. The song's own load, for reference: 175 syllables, 138 words, 26 shapes, 6.7 syllables a shape;
  by shape A 8 to 9, B 5 to 6, C 9, D 5 to 7, E 7, H 7, I 6 to 7, F 5, G 8.
  Eli on trial C: "Overall, this is good", fine with the two climbs in a row, nothing he would change by listening; he
  will sing along with it for a while and come back with exact spots. Trial C is now also stanza 4 of the main set
  (`r118p`, letter `d`, `4.s.txt`; the layout before it is `4.s.v3.txt`). The trial entries `r118q` and `r118r` are still
  in the menu; remove them when he no longer needs the comparison. Not done yet, and not asked for: the singer's pauses
  in the other stanzas (2 and 11 have no `.s.txt`), and the same un-crowding for their fullest lines. In singer-pauses
  mode a pause written by hand inside a shape gives way to his longer one, so old `~0` and `~.5` marks need no editing;
  the shortened held notes in A (`c7*.6` and the like) should go back to full length when a stanza is converted.
- Key advice given to Eli (18 November 2026): this melody sits in the middle and only touches the top, while its low
  notes are long, so choose the key by the low notes; stay at "As sung" or at most 1 or 2 down, and keep one key.

## Notes on each line (18 November 2026)

- Eli stopped the roll-out of stanza 4's changes to the other stanzas: he thinks stanza 4 was overcompensated and wants to
  refine one stanza at a time, with notes down to the word, before anything is copied to all 22. Do not roll out until he
  says a stanza is final. `tools/lay.py` (a helper that lays a stanza out from a hand-written plan) is unfinished and unused.
- To make his notes easy: Loop a part has "Notes on each line" (`lnBox`, everything named `ln...`). It lists every line of
  the picked part (for the Psalm 23 melody sets one line is one melody shape, named in plain words from `R118_FORM`, the
  syllable counts of each stanza's shapes; other songs fall back to half lines or phrases), with a note box beside each.
  While a session runs the panel moves into the running screen, the line being sung lights up, and typing never stops
  the audio. Notes are kept as typed (`ison-ln-draft`). "Save these notes to the log" stores them (`ison-ln-log`, newest 40)
  and copies the text; he pastes it into a message. Claude cannot read his phone, so pasting is the hand-over.
- First notes from the log (stanza 4, letter `e`, 18 November 2026; the layout before is `4.s.v4.txt` and still in the menu as
  trial C). He felt trial C had overcompensated into slowness. (1) "and with Your law have mercy on me": too much on "law",
  no weight wanted on "Your"; now E carries "and with Your law have" with the first four quick and the rise and fall on
  "have", H carries "mercy on me" with the steps down spread over "mercy", a quick "on", a long "me". (2) "I chose the way of
  truth": quicker, the weight on "truth" as it hands over (held note on "chose" halved, no pause after "the", "truth" on the
  last two cells). (3) "I ran on the path of Your commandments": quick syllabic climb (Fs) to "com-", the height's first
  three cells all on "-mand-"; "When You enlarged my heart" quick, "heart" on the leap and the whole last figure.
  The lesson: little words quick, and the melody's long figures on the one word that carries the meaning.
- The singer's spacing, measured from the scan (18 November 2026, Eli asked for rules found in the recording to guide every
  change). His syllables are even: 10th to 90th percentile 0.34 to 0.97 s, middle half 0.43 to 0.65 s, median 0.54; only 8% are
  under 0.3 s and 9% over 1 s. Little words (the, of, and, me) are as long as accented syllables (median 0.53 against 0.54);
  figures of 3 or 4 notes fall on little words and weak syllables as often as on accents (the melody decides, one syllable to
  a cell); the long closing figure (1.3 to 2 s) sits on the last syllable of a line whatever its accent (shep-HERD, e-VIL,
  cham-BER); extra syllables are recited on home notes of half a second, not a quarter. Our stanza 4 was two-speed: 27% of
  syllables under 0.3 s (the q recitations and split cells) and 13% over 1 s (cells stacked on one syllable). The lines Eli
  approved earliest ("I made known my ways and You heard me") are exactly the even, one-syllable-to-a-cell ones.
  Rules from it: one syllable to a cell where possible; no syllable under about 0.33 s (recite on `h`, not `q`; lengthen
  split cells); mid-line no stacking over about 1 s, drop a cell (a repeated or rebound one: H 4, E 7, G 2, D 2) instead;
  the long figure only at a line's end or on the one word Eli asked for. Trial D (`r118s`, `4s.s.txt`, 96.5 s) is stanza 4
  by these rules on top of his three notes: 3% under 0.3 s, 12% over 1 s; waiting on his ear. `r118p` stanza 4 stays at `e`.
- Eli on trial D (18 November 2026): a step in the wrong direction. Changing lengths, dropping cells and adding recited
  notes "leaves the melody": the beats and their timing are what give the melody its identity. His rule: the melody the
  same in tone and timing, only which words fall on which notes changes. He added: follow the heart of that, not the
  letter; a little exaggeration here and there is fine, and it must not be so rigid that a stanza cannot fit.
  So no `*.6` factors, no cells left out, no q/r/h recitation, no half shapes, no Fs.
- `tools/overlay.py` does this (trial E, `r118t`, `4t.txt`, 97.4 s). It reads the singer's real performance from the scan
  (every note, length and pause of each of his 26 phrases) and lays a stanza's syllables on the notes, each syllable on
  one or more notes in a row. `--free` picks his whole phrases in the best order for the words (only joins he makes,
  begins on A, ends on D, a verse ends on B, D or H); without it the whole song is used in his order, which for stanza 4
  (140 syllables on his 175) stretches too many words. `--pin=word=SHAPE,...` puts a word on a shape (stanza 4:
  life=A, unrighteousness=H, from=I, have=D, ran=F, when=D); three lines were then corrected by hand (first line, "meditate",
  "O Lord do not"). Stanza 4 came out as A B A B A B C D F G D E H I D A B C D F G D with a median syllable of 0.55 s
  (his 0.54). Its weights are a first guess. Waiting on his ear. The older shape tools (shapes.py, lay.py) alter the melody
  and should not be used for new versions unless he asks.
- Rolled out to all 22 stanzas at Eli's word (18 November 2026, version 50, `R118P_REV` letter `f` for every stanza; the
  trial sets `r118q` to `r118t` were removed from the menu and the repo). `r118p` is now this exact-phrase method
  everywhere; the older shape scores (`N.s.txt`, `N.txt`) stay on disk as history. The scores sung are
  `~/ison-singer/p23m/Nu.txt` (+ `.form`). Stanza 4 is trial E as he heard it (`4u.txt`, rebuilt from its sung record
  after the working file was overwritten). Stanza 1 is a layout written by hand (`1.oplan.txt`, run with `--plan`);
  the other 20 are the tool's fit steered by `~/ison-singer/p23m/overlay.pins.txt` (one line a stanza: `word=F` puts a
  word on a phrase, `/word` a phrase begins there, `+word` no phrase begins there, `#2` the second time the word comes).
  To change a spot: edit that line (or write `N.oplan.txt`), run `overlay.py N Nu --free` (or `--plan`), read the layout
  it prints, then `heart.py ~/ison-singer/p23m/Nu.txt N <out> --unit 0.25 --home 51 --scale p23 --set r118p --sing`,
  `pack118.py <out> NB_KEY r118p`, a new letter in `R118P_REV`, and that stanza's entry in `R118_FORM`.
- What the tool holds to (all from Eli's notes and the scan): his phrases whole and unaltered, joined only as he joins
  them; a verse never ends on an opening phrase (A, E, F) and best on B, D or H; a phrase never ends on a word that
  leans on the next (the, of, and, I, shall ...); breaks prefer line ends, punctuation, or just before a word that opens
  a group (of, in, for, that, and ...); no syllable under about 0.3 s where it can be helped; only his closing figures
  are long; the climb once or twice, not twice in a row; his descent on a dark line when one fits. Honest limits: 20
  stanzas were read line by line and corrected by direction, not polished line by line as stanza 4 was; a few phrases
  still carry only three or four syllables (so those words are drawn out), a few breaths fall inside a word (he does
  that too), and stanza 1 has its only climb on "Would that my ways were led". Eli refines one stanza at a time from here.
- If a stanza of `r118p` is laid out again, update its entry in `R118_FORM` (from `N.txt.form`) or its lines fall back to half lines.
- One syllable to each of his (19 November 2026). Stanza 4 has 105 words and 140 syllables (the song: 138 and 175, on 26
  phrases). Eli felt the stretch just past halfway was off; there "Remove the way" had 4 syllables on a phrase where the
  singer has 7. His rule now, above where sentences begin and end: where the singer has three syllables on some notes we
  may not put one or two there; our syllable count on a phrase should be his. `overlay.py N name --plan --exact` does this
  for a hand plan (`N.oplan.txt`): a line with his count is laid one to one, a line one or two short joins neighbouring
  syllables of his (never across a breath), a line with more falls back to the old fit. Trial F (`r118v`, stanza 4 only,
  `~/ison-singer/p23m/4w.txt`, 95 s): first half as trial E, second half `F5 G8 D7 | A9 B6 | C9 D7 | F5 G7 D4`, exact except
  two joins in the last climb ("When" and "heart"; verse 32 is 16 syllables, his climb and close need 18). The cost: phrases
  end mid-thought ("Remove the way of / unrighteousness from me. And with / Your law have mercy on me", "O / Lord"), and
  the climb comes three times. The first half is not exact yet (B7 on his 6, C6 on 9, D4, F4, G7). Waiting on his ear.
  If he likes it: do the first half the same way, then it replaces stanza 4 of `r118p` and `r118v` leaves the menu.
- Eli on trial F (19 November 2026): "this sounded very, very good", make it the current version. It is now stanza 4 of
  `r118p` (letter `g`, version 53; `~/ison-singer/p23m/4u.txt` is trial F, the one before is `4u.trialE.txt`), and `r118v`
  is gone from the menu and the repo. So the one-syllable-to-each-of-his rule is confirmed by ear for the second half.
  Not done and not asked for: the first half of stanza 4 by the same rule, and the other 21 stanzas.
- Trial G (`r118w`, stanza 4 only, `~/ison-singer/p23m/4g.txt`, plan `4.oplan.txt`, 92 s, version 54): the first half laid
  the same way, `A9 B6 | A9 B7 | C9 D5 | E7 H7 I7 D7`, then trial F's second half unchanged. Every phrase has his count
  except "Teach me Your ordinances" (7 on his 6; 73 syllables do not divide otherwise). The climb on "My soul fainted" is
  gone from the first half; those words are now on his descent (unused before), so the stanza has two climbs, both in
  the second half. Waiting on his ear; if he likes it, it becomes stanza 4 of `r118p` and `r118w` leaves the menu.

## The lessons file and the Tone 4 melody (19 November 2026)

- `notes/psalm23-melody-lessons.md` (on this Mac only: `notes/` is in `.gitignore` because the file quotes the psalm
  wording) is the running record of what was learned putting Psalm 118 on the singer's melodies: Eli's rules in order of
  weight, every trial and his verdict, the measured facts, how a stanza is made, open points. Eli asked for it so nothing
  is lost when a long conversation is summarized. Read it before changing a stanza of these sets, and add to it whenever
  he gives a verdict or a new rule.
- Tone 4 (`psalm23-tone4.mp3`, same singer, same words): scanned the same way (`~/ison-singer/p23t4/scan/`), 26 phrases of
  eight kinds, `A K | A K S J | A K V W X Y K` twice (A opening, K cadence, S rise and fall, J pickup and cadence, V turn,
  W low line, X way back, Y level line). `tools/p23t4.mel.json` + `overlay.py --mel=...`; `heart.py --scale p23t4 --home 49`
  (as sung: his Tone 4 already sits in the range Tone 3 has after lowering). Review set `r118t4`, stanza 4 only, version 1
  (76 s, 14 of 20 phrases on his exact syllable count, six syllables over in all, none stretched), waiting on his ear.
  The layout and its weak spots are in section 8 of the lessons file.

## Learning a formula from a recording (14 November 2026)

- `t7p91` is Tone 7 learned from the built-in Psalm 91/121 recording: words heard by faster-whisper and corrected
  (`~/ison-singer/p91/words.txt`), letters aligned, every syllable's pitch measured, then the line formulas read off
  by hand from 54 lines of Psalm 91. Ladder above home: 0, 1.1, 2, 3, 3.8, 5.1 semitones (home about MIDI 51).
  Applied back to his own Psalm 91 words it puts 90% of syllables on the note he sang (86% exactly; the rest mostly
  his two close upper notes). The Psalm 121 part and the ending (lines 55 on) use other patterns and are not in it.
- `sgFollow` knows refrains (`M.refrain`): a line of only Hallelujah/Alleluia is sung the refrain way, and with
  refrains present the first line after one takes the first formula and the rest the second.

## Learn a song settings (14 November 2026)

- Ears only, Learn a song (unit 5, `earSongDrills`, `earSongFit`). Eli asked to drop the "on your own" (from memory)
  pass on long stretches: he only waits through it. Setting `songAlone`: `short` (default; notes, moves, pieces keep
  it; joins, whole part and recording sing along once more instead), `never`, `all` (old way). `lwac`/`hold` take
  `noAlone` and `reps`.
- `songReps` (auto or a number): times each note, move, piece and join is sung with the tone. With a number, moves
  are one step each, nothing is cut, and a lesson longer than the session continues next session from the step
  saved in `ison-ears` `songPos` (per song and part, `esPosSave` from `bgLog`).
- `songWeight` 0 to 100: shares the count out by difficulty (`esShare`, rated 1 to 10 by `esNoteD`, `esMoveD`,
  `esSeqD` from the notes alone: jump size, jumps up, tritone, cents off the piano note, quick notes, high or low,
  turns, direction changes). A first guess; Eli has not judged the ratings yet. In Ears only the app does not hear him.
- Master a song (unit 6) has the same three settings, kept separately: `smReps`, `smWeight`, `smAlone` (`smSetReps`,
  `smDx` rates every note, move, formula, phrase, piece and hard spot with the same `esNoteD`/`esMoveD`/`esSeqD`, `smTimes`).
  Default `never` (Eli, 15 November 2026: singing from memory is not useful to him, so by default none of it). `short`
  keeps the on-your-own pass on notes, moves, formulas and hard spots; whole phrases, joins, runs and the finish
  are sung with the tone, and Start anywhere and Fill the gap are left out. The Memory focus counts as `all`. A number in
  `smReps` replaces the fading stages' counts (mature items are sung with the tone that many times too). Daily practice
  uses the same plan, so the settings apply there as well.
- `esShare` measures against the average rating of that kind of bit, held between 3.5 and 6.5, so all-easy kinds (single
  notes) get fewer than the chosen number and all-hard kinds (hard spots) more.

## Bible tab: listen and memorize (17 November 2026)

- Eli memorizes scripture (now Psalm 118, Septuagint) by listening while he works with his hands or at the computer,
  following along with a plain reading voice. The Bible tab (`bbOpen`, everything named `bb...`) is that: pick
  stanzas (bubbles 1 to 22 with the Hebrew letter names), they are read in order and start over, each stanza
  once or N times in a row, until a time limit (counted only while it plays; then it stops at the end of the
  verse). Voice pitch (half steps, -7 to +5) and speed (60% to 180%) change live, also while paused. Tap a verse
  to read from there. Lock screen: play, pause, next and previous stanza. "Keep all 22 on this phone" saves them
  for no-internet use (`BlobDB` keys `bb118:N:rev`).
- The readings: `rd118/N.bin` (packed by `tools/pack118.py <folder> NB_KEY rd118`, run with the singer's Python,
  which has the lock library). Each holds `{name,text,dur,v}` (`v` = start and end of each of the 8 verses,
  found by counting words against the syllable timings) and a 64 kbps m4a. Made by the singer (TIGER, defaults)
  on the `rd2` reading tone at speed 160 (the Song Maker's top speed; about 68 s a stanza). A speech recognizer
  heard nearly every word of stanza 1. When a stanza is read again, give it a new number in `BB_REVS` so phones fetch it (stanza 20 is 2: Eli changed "pursue" to "persecute" in verse 157, 17 November 2026, also in `n118.bin` and the notebook).
- Pitch uses the songs' natural key change (`keyDecode`, `keyRun`), cached in `KeyDB` with only the newest voice
  per stanza (`ison-bb-keys`); speed is the audio element's own `playbackRate` with the pitch kept.
- Tone under the reading (`isoT`, `isoV`), mixed into the stanza's audio itself (`bbBlob` over `bbKeyed`) so it keeps
  going with the phone locked; same organ harmonics as the app's tone, A4 = 440 like the singer. Default `follow`:
  it plays the reader's own notes (`rd118/notes.json`, from the notes files the singer sang, same-note neighbours
  joined; checked 96 to 97% of the time within half a step of his voice), sliding between them and silent in his
  breaths, moved with the voice. Eli asked for this, not a steady drone (17 November 2026); `auto` (steady on the
  reading note C3, `BB_READ_NOTE`) and steady C2 to C4 remain as choices. Volume 0 to 10 (default 3). Changes rebuild
  the current stanza and carry on from the same spot. If a stanza is read again, rebuild notes.json and raise `BB_NOTES_REV`.
- More books later: the Book drop-down is ready for them, but only Psalm 118 exists.

## Polish the vibrato (19 November 2026)

- What Eli asked for: he has Psalm 23 Tone 3 "pretty much down" except the subtle vibrato spots, and wanted a lesson
  plan for a song that is nearly finished. A vibrato trainer for one song: find every spot that has vibrato, give him
  settings (how many times through, how slow to start, slowed-down passes), then let him hit play, set 60 or 90
  minutes and get well-rounded training by ear until the smallest shifts in the singer's voice are his.
- It is Ears only **unit 15, "Polish the vibrato"** (everything named `vb...`; the card is `#vbBox`, the settings live
  in `earSet().vb` the way Loop a part's live in `.lp`). Both built-in recordings are in it: Psalm 23 Tone 3 (43
  spots) and Tone 4 (40). Progress per spot is `ison-vb` (seconds played, one pass per 25 s), credited from `bgLog`.
- **Finding the spots** (`tools/vibrato.py`, run with the singer's Python): pitch every 2.5 ms (Praat), a cubic taken
  out of each note the deep scan found so a slide does not count, then a sine fitted at every rate from 3.2 to 9.8 a
  second. Kept when the fit explains 55% or more of what is left, is 12 to 95 cents wide and lasts 1.6 swings. The
  script prints the rows of `VB_DAT` in index.html. Tone 3: median 8 swings a second, 28 cents wide (a quarter of a
  half step); 26 of the 43 are on his home note and 18 of them are in the full close (D). Tone 4: 7 a second, 29 cents.
- **One spot's drill**, in this order (each piece can be turned off): his own moment; the same moment slowed to half
  speed with the pitch kept; a ladder of swings on the tone, from about one a second and a half step wide up to his
  exact rate and width in 4 steps (soft ticks on each swing while it is slow); the note held straight then let go
  into the swing; his moment again to sing with; the whole phrase it sits in. Every 8 spots they all come back one
  after another. A session opens with a warm-up on the home note. "Slower" and "faster" during a session change how
  many times through each piece (1 to 6); "next" skips to the next spot.
- **Why it is built that way** (asked for, researched 19 November 2026): teachers build vibrato by holding a straight
  note and letting the swing in, and by swinging slowly and wide on purpose like a gentle trill, then speeding it up
  and narrowing it (London Singing Institute, 30daysinger, Cari Cole; flute pulse-counting from The Instrumentalist;
  NATS Journal of Singing on holding width while the rate changes). Ornate chant has always been taught by slow
  exegesis, the melody rendered slowly and then at speed. Blocked practice looks better in the session, interleaved
  holds better the next day, hence the mixed round.
- **Engine additions** (small and additive, they serve any unit): step kinds `wob` (a tone swinging: `m`, `r` swings a
  second, `c` cents wide, `sg` seconds held straight first) and `clip` (a span of the recording at a speed, pitch
  kept), both in `bgTimeline` and `earStepsSec`; event type `wob` in `bgSynth`; source `'VB'` in `bgRecs`. Clips are
  cut by the existing `wsolaMap`, so slowing keeps his pitch. `VB` is the recording decoded once at 22050 (in the song's
  key through `keyedAudio`), and spot times are plain seconds in the mp3. The key is the app's own key for that song
  (`keyRowIds` entry `vb`, the same Change row as Loop a part; Eli asked for that on 19 November 2026 after a
  drop-down of my own looked out of place), so the tones move with `vbKey()` and his voice is moved by `keyedAudio`.
- **Checked by measurement only, Claude cannot hear it.** Rendering a spot and measuring the result: the tone lands
  within 0.03 of a half step of his pitch and within 0.15 swings a second of his rate; the slowed moment keeps his
  pitch within 0.1 of a half step and halves the swing; his voice is there at the right pitch in every pass. Eli
  judges the sound.
- Known gaps, if he asks: the ladder's widths are the app's own choice (a half step at the bottom, his width at the
  top), not measured from him; sessions longer than about 46 minutes are rendered at 11 kHz by `bgSessionSr`, so his
  voice is duller in a 60 or 90 minute session; the app does not hear him, so nothing is scored.

## The Lord's Prayer, Kedrov (20 November 2026)

- What Eli asked for: the English version of "that most popular Our Father hymn that they sing during liturgy, usually a
  whole choir", the sheet music, which version fits his range, and it put into the app. He said it is old and not
  copyrighted, which is right for the music itself.
- What it is: **"Otche Nash" by Nikolai Kedrov Sr. (1871 to 1940), written in Paris in 1922**, the four-part setting
  Orthodox choirs everywhere sing. Kedrov died in 1940 and it was published in 1922, so the music is out of copyright
  (United States: published before 1930; life plus 70 countries: since 2011). Editions and arrangements of it are not:
  Musica Russica's English edition is in copyright, and the usual CPDL and MuseScore files each carry their own licence.
- The score used: John Kilpatrick's free English edition, `https://www.johnkilpatrick.co.uk/music/misc/Kedrov-Ourfather-D.pdf`
  ("©2006 John Kilpatrick; may be freely copied and performed"), SATB in D, Adagio, free rhythm, two alternative Amens.
  The PDF, its two pages as pictures and the transcription are in `notes/our-father/` (gitignored, so on this Mac only).
  CPDL and cpdl.org file links are behind a bot check and cannot be fetched; the browser pane gets the same block.
- How the melody was read (and this is the method to reuse for any engraved PDF): MuseScore and Sibelius PDFs carry the
  noteheads as glyphs of a music font, so nothing has to be read by eye. PyMuPDF is on this Mac's system python3 (`import
  fitz`; there is no poppler, no pdftotext). Staff lines come from `page.get_drawings()`, noteheads from
  `page.get_text('rawdict')` where the font is `MScore` and the codepoint is U+E0A2 whole, U+E0A3 half, U+E0A4 black,
  U+E1E7 dot; the glyph's `origin` y against the staff lines gives the exact staff degree. Checks done: all four voices
  together make a plain triad or one of the piece's own suspensions at 83 of 83 chords, and three passages were zoomed
  and read by eye. The scripts are in the session scratchpad only.
- In the app: a built-in chant, id `song-ourfather`, in `SONGS` with its `credit`, in `BUILTIN`, and as an `<option>` in
  the Songs tab list (that list is hand-written in the HTML; the Ears-only pickers build themselves from `BUILTIN`).
  85 notes, 150 seconds at bpm 60, written D4 to D5, which the men's octave (`S.shift` = -12) sings as **D3 to D4**.
  That is almost the same ground as Psalm 23 Tone 3 as sung (C3 to C#4), so "as sung" should fit him; down 2 puts the
  top D4 on "not" at C4 and the bottom at C3. The key sheet (Change the key) says whether it fits his range.
- The words are the ones most parishes say (who art, on earth, those who trespass). Kilpatrick's edition uses the 1662
  Book of Common Prayer wording (which art, in earth, them that trespass); the swap is one syllable for one, so the
  notes are untouched.
- **Sung in his key (20 November 2026).** Eli asked for it mapped to his range and sung by the voice on this Mac so he
  can follow along, with no lock on the file. His range was taken from what he already sings daily: the Psalm 23 melody
  on Psalm 118 sits G2 to G#3 (home 51), the heart songs are Hijaz on A2, so about **G2 to A3**. The chant is therefore
  written in A (five steps under the choir's D): `A3` to `A4` as typed, which the men's octave sings as **A2 to A3**.
- `tools/songmid.py <song id> <out.mid> [--shift -17]` turns any built-in chant in index.html into the singer's notes
  file (it reads SONGS out of index.html, so the app stays the only copy of the melody; hyphenated syllables become the
  word + `+` + `-` the singer wants). Then `tools/sing.py`, then `tools/scorepdf.py`'s own voices as a quiet organ
  chorus under it (the scratchpad's render_pad.py; alto, tenor and bass five steps down, 13 dB under the voice, the one
  low octave in the last Amen raised). The result is `ourfather.m4a` (1.8 MB, 96 kbps, 2:31) in the repo, unlocked.
- Checked by measurement: all 85 notes within a quarter step of the score, 4 cents off on average; a speech recognizer
  heard 52 of 56 words (93%), missing only "and lead" run together and the long held "evil. Amen".
- How it is wired: `SUNG` holds the file (`pubAudio('ourfather','ourfather.m4a')`, cached in BlobDB like psalm23), the
  SONGS entry names it with `sung:'ourfather'`, and `builtinRec` returns it with `builtinRecording` and **`exact:true`**
  so `smEnsure` trusts the written notes instead of measuring the audio (without that it heard the low voice an octave
  down in places). The Songs tab plays it as the guide, but only while Transpose is at the men's octave it was sung in.
  Note for next time: the song map is cached in localStorage as `ison-smap-<ver>-<id>-a|-n`, so clear that when testing.
- `tools/scorepdf.py` is the reader that got the notes out of the PDF, saved as a tool: staff lines from the page's
  drawings, noteheads and dots from the music font's glyphs (SMuFL codepoints), pitch from where each notehead sits.
  `--check` says whether every system's voices add up, which is what catches a missed dot. It needs the Mac's own
  python3 (PyMuPDF is there, not in the singer's venv). For engraved PDFs this beats any music-reading program because
  nothing is guessed; for scans and photos it is useless and homr or Audiveris is the right tool (not installed here).
- Not done, and worth asking him: whether his parish sings this one at all. The other candidates, if he says it is not
  the one, are the Antiochian Archdiocese English setting (the app already holds other Antiochian settings), the Greek
  Byzantine "Pater imon" in English, Rimsky-Korsakov's Our Father in English, and the Syriac "Abun d'bashmayo".

## Blessed art Thou, O Lord: the Evlogitaria (20 November 2026)

- What Eli asked for: the whole hymn, done the same way as the Our Father, from real sheet music with the words in it.
- What it is: the **Evlogitaria of the Resurrection, Kievan chant (Moscow tune), Tone 5**, sung at Matins every Sunday:
  the refrain "Blessed art Thou, O Lord, teach me Thy statutes" with five stanzas, the Glory, the Now and ever and the
  Alleluias. 392 notes, 3 minutes 37 at 140 a minute. Written in F in the score; in the app five steps down, so the
  men's octave sings it **C3 to G3** (his daily ground is G2 to A3). Only five notes are used, C3 to G3, as the chant
  is a pentachord; the reciting note is F3 and every stanza ends on C3.
- The score: the parish edition of the Diocese of the West, Department of Liturgical Music (2019), English text of the
  OCA, `https://stnicholasjuneau.org/wp-content/uploads/2021/01/Evlogetaria-Resurrection_-_K_T5_3-part.pdf`, kept in
  `notes/blessed-art-thou/` with the transcription (gitignored). The chant tune is old and free; that typesetting and
  translation are theirs, published for church use, so the app credits them. CPDL stays unreachable (bot check), and
  antiochian.org needs JavaScript, so their settings could not be read.
- Reading it was harder than the Kedrov PDF and taught three things worth keeping, all now in `tools/scorepdf.py`'s
  sibling notes: (1) Finale draws noteheads as **filled paths, not font letters**, so they are found by shape (about
  7 x 5.6 points; 5.6 high is filled, 5.8 hollow, 9 wide is a whole note) rather than by glyph; (2) the three voices
  are written as **chords on one staff**, so the melody is the top note of each chord, and a chord where only the lower
  voices move (its top note sits four or more half steps below both neighbours) is not a melody note; (3) the chant
  **recites several syllables on one note**, so the words are laid on the notes by a small dynamic program that may
  put several syllables on one note or skip a note (a held syllable). Each recited syllable gets its own beat in the
  app, which is how it is sung.
- Checks: all four refrains came out identical note for note, every one of the 351 syllables got a note, and the 26
  systems all read without a short line. Master a song makes 47 phrases of it.

## Blessed art Thou, the Byzantine melody (20 November 2026)

- Eli heard the Kievan version and said it was "a lot different" from the one he knew, and sent a YouTube video
  ("Evlogitaria of the Resurrection", the group *Ncense, 2016, `kwgbkyyp9oo`). It is the **Byzantine melody, Tone 5
  (Plagal First Mode)**, sung over a held drone (ison) the whole way. Same hymn, different melody. He asked for that
  melody, said he loves that translation, and wants every sung word in English.
- Score used: **Basil Kazan**, "Evlogetaria", Antiochian Archdiocese Matins book (Rev 3, 2010),
  `https://antiochianprodsa.blob.core.windows.net/musiclibrary/matins-kazan-complete-4-resurrectional_evlogetaria.pdf`,
  kept in `notes/blessed-art-thou-byz/kazan.pdf` (gitignored). Same wording as the video ("The company of the angels was
  amazed..."). At a steady 211 a minute every section of it starts within about a second of the video, the repeat of
  the Alleluias included, so the video sings exactly this setting.
- Reading it (Finale, font Anastasia, size 24 = melody, size 16.8 = the ison notes): filled heads U+02C6 and U+0153,
  half U+02D9, whole `w`, dot `.`, accidentals `b # n` (they last to the bar line), quarter rest `Œ`, staff lines are
  the `=` glyph (origin y = bottom line, 3 points a step), bar lines `l`, beams are filled boxes. Lyrics are Times 12;
  a bold "the" (macron) and a dash above it are the score's mark for "thee". Measures vary in length (chant); each one
  was checked to be a pickup, a rest or a whole. One line on page 1 is a pasted picture that changes "from hell" to
  "from Hades" with other notes; the text underneath is what the video sings and is what the app uses ("hell", which
  is also the English Eli asked for). Reader: session scratchpad only (readkaz.py).
- An earlier attempt used Chadi Karam's setting (Holy Transfiguration text, "Hades"); it was replaced before release.
- In the app: `song-evlogitaria-byz` ("Byzantine, Tone 5"), 615 notes with three rests, bpm 211, written G4 home (two
  steps under the score's A), men's octave E flat 3 to E flat 4, home G3. Kazan's short forms destroy'ng, pow'r,
  t'ward and the old word spake are in `tools/sing.py`'s SAY.
- Sung file `blessed-art-thou-byz-voice.m4a` (BlobDB key `evlogitaria-byz-v`): the voice only. Version 64 and before also
  had a drone from Kazan's small notes mixed in; it was taken out in version 65 (see "Nothing mixed under a sung voice").

## The *Ncense recording as the singer's voice (20 November 2026)

- Eli sent the *Ncense recording of the Evlogitaria (3:31, the same as the YouTube video) and asked for a complete
  breakdown, every lyric and note, lined up with the sheet music, with the recording itself as the singer's voice and
  matched to the score's pitch. He expects to sing it six half steps down.
- Version 64: built in (`blessed-ncense-ab.m4a`, `blessed-ncense-d.m4a`, BlobDB keys `ncense-ab`, `ncense-d`) after Eli said he
  has full permission (20 November 2026). Before that it was kept off the public repository as a released recording. The repo holds only the timings.
  Eli adds his own copy once on the Songs tab (`ownBox`, `ownFile`, BlobDB `own:ncense` and `own:ncense-d`); a SONGS
  entry with `own:` shows the picker. Songs `song-evl-ncense` (A flat, as sung) and `song-evl-ncense-d` (6 lower, D).
  Use the 6 lower entry rather than the key setting: the app's key change (`keyedAudio`) is made for one voice.
  Version 63: Eli heard only the tone in Loop a part because the file had never been added (the picker was only on the
  Songs tab). Now any screen that opens such a song without its file (`smEnsure`, `songRecFor`) pops up `ownSheet` with
  the file picker and the exact file name; tested in the browser with the real file, then reloaded: Loop a part finds it.
- Work folder `~/ison-singer/ncense` (outside the repo): `drone.json` (the ison every 20 ms), `align.py` (MMS forced
  alignment of every word of Kazan's text, syllables split by letters), `align2.py` (notes inside each syllable by a
  dynamic programme on the melody's harmonic salience with the drone's steady partials taken out, the score's rhythm as a
  strong prior; `--second` retunes from the melody itself), `check.py`, `build_app.py` (typed notes in seconds at bpm 60,
  breaths as rests, the last note to where the voices fade), `gen_report.py` (the breakdown page,
  `notes/blessed-art-thou-byz/ncense-breakdown.html`, gitignored).
- Measured: 615 notes, 471 syllables; about 215 a minute (0.28 s a quarter); the choir drifts from about 60 to about 150
  cents under A. 85% of notes are plainly Kazan's note; most others are covered by the drone's overtones. Possible real
  differences (a G for Kazan's A) in "and didst give to Eve joy in place of sadness" and "those who had fallen"; the
  app keeps Kazan's notes. They sing the scale close to piano tuning (steps within about 6 cents).
- Retuning: `rubberband -3 --formant --pitchmap` along the measured curve onto exact A flat (after: every half minute
  within 0 to 10 cents of the notes, 91% of notes within a quarter step); the 6 lower copy is the same file through
  Rubber Band `-p -6` (88% within a quarter step of D). The files sent to Eli: `~/ison-singer/ncense/Blessed art Thou -
  Ncense (retuned to A flat).m4a` and `(6 lower, D).m4a`.

## Our Father: our church choir as the voice (20 November 2026)

- Eli has full permission for this recording (chant recorded in his own church), so it is in the repo:
  `ourfather-choir.m4a` (as sung, retuned to exact E flat) and `ourfather-choir-d.m4a` (one half step lower, D). Songs
  `song-of-choir` and `song-of-choir-d`. He plans to stop using the computer voice for the Our Father.
- It is Kedrov's four-part setting in E flat: chroma DTW of all four parts synthesized against the recording picks +1 from
  the score's D by a wide margin (cost 0.145 against 0.22 for the next key). Choir about 40 cents flat at the start,
  rising to pitch by the end; each melody note within about 10 cents of that curve.
- Timing (`~/ison-singer/ourfather-rec/align.py`, `align2.py`): a time map from the harmony (chroma DTW), the MMS word
  aligner and faster-whisper word times; each syllable is placed where two of the three agree (the map is blind inside a
  long held chord at the start, MMS loses its place after "against us", whisper words are matched by spelling and time);
  the rest are spread by the score's beats. Notes inside a syllable share it by beats. Breaths at punctuation as rests.
- Key advice given: men sing the tune an octave under the sopranos, so the as-sung E flat is already E flat 3 to E flat 4
  for him; the D copy is his D3 to D4. Eli had guessed eight half steps down; that would put the sopranos at G3 to G4 and
  the basses in a rumble, so it was not made. Offer it if he asks after listening.
- Checked: the app's own key change (PSOLA, `psolaShift`, 22 kHz) run on the *Ncense choir six down gave 71% of notes in
  tune against Rubber Band's 88%, and broke the drone up (its pitch wandering about 5 half steps instead of staying
  steady). So for choir recordings make lowered copies with Rubber Band on the Mac; do not rely on the key setting.

## His range, corrected (20 November 2026)

- The guess "about G2 to A3" (from the Psalm 118 sets at home 51) was wrong for these hymns: Eli found the Our Father at
  A2 to A3 too low and had to raise it five half steps "just to get it to a relatively normal range". So version 60 put
  the Our Father back in the choir's own D (men's octave **D3 to D4**, file `ourfather-d.m4a`, voice only since v65 as `ourfather-d-voice.m4a`), the Kievan Blessed art
  Thou in its score's own F (**F3 to C4**, `blessed-art-thou-f.m4a`) and the Byzantine one in G (**E flat 3 to E flat 4**, home G3).
  Older notes above that give A2 to A3 and C3 to G3 describe version 59. A key he had saved on those two songs is lowered
  by five once (`ison-key60`), so they sound where he had them. Choose new songs' keys around D3 to D4, not G2 to A3.
- He also felt the Our Father was very slow. Measured against Archangel Voices' English recording (YouTube
  `_0ZLVAMbSpE`): "Our Father, who art in heaven" 12 s there, about 15 s in the app; "Give us this day our daily bread"
  10 s in both. Choir recordings of it run 2:16 to 4:25; the app's 2:31. So the speed is right: it is written Adagio.
- A new sung file must have a new BlobDB key and file name: `pubAudio` keeps the first copy it fetched forever.

## Nothing mixed under a sung voice (20 November 2026)

- Eli heard a "sputtering" while matching his voice in Learn a song and Loop a part, as if two tones were playing. Three
  computer-voice files had a soft organ sound mixed in by Claude (Our Father in D: alto, tenor and bass; Kievan Blessed
  art Thou: the lower voices; Kazan Blessed art Thou: a drone), built with the same harmonics as the app's own tone, so
  with the app's tone on there were two organ layers. His rule: **never mix a tone, drone, pad or chord into a song
  file; the app adds its tone (and its own ison, "Ison drone under everything") when it plays.** Version 65 uses the
  voice alone: `ourfather-d-voice.m4a` (`ourfather-dv`), `blessed-art-thou-f-voice.m4a` (`evlogitaria-fv`),
  `blessed-art-thou-byz-voice.m4a` (`evlogitaria-byz-v`), made from `~/ison-singer/out/key60/* sung.wav`.
- The choir recordings (*Ncense, the church Our Father) have nothing added, but the *Ncense singers hold their own ison
  the whole way (about two thirds of the file's sound is held steady, against about a third for a solo voice), and a
  choir sits a little off any exact note: measured on held notes, median 10 to 20 cents from the written note (10 cent
  steps), which against the app's steady tone gives a slow waver of about 1 to 3 a second. That is the choir, not the file.
- To tell the tone from a choir, version 66 added two tone sounds (`earTimbre`): `reed` "Hollow reed" (odd harmonics
  only, like a clarinet) and `bright` "Bright buzz" (many strong harmonics, like a harmonica). Learn a song has its own
  Tone sound row (`earSongTimbre`); it is the same one setting (`earSet().timbre`) as Loop a part, Master a song and the
  Ears only "Sound and voice" list.

## Every change

1. Edit `index.html` (or the other files).
2. `python3 tools/check.py` must say OK. Raise `APP_VER` in index.html and `CACHE` in sw.js by one (the version shows on the Chant tab, with a "Get the newest version" button, because phones kept showing old copies).
3. Commit with a plain message and push to `main`. Tell Eli what changed and what to try.
4. Only if Eli wants the artifact copy current: `python3 tools/artifact.py` and publish it.

## The Psalm 23 singer's voice on other songs (20 November 2026)

- On this Mac only, never in this repository: `~/ison-singer/clone` holds SoulX-Singer (`sx` venv), Applio with an RVC
  model trained 300 epochs on the Psalm 23 recordings (`Applio/logs/psalm23singer`), and an 8.9 s voice sample
  (`voice/prompt.wav`, Tone 3 at 41.55 to 50.4 s). Eli has permission for the recordings; publishing a copy of the
  singer's voice singing other texts is a separate question to put to him before anything goes in the app.
- `~/ison-singer/clone/sx/bin/python ~/ison-singer/clone/hisvoice.py "<song> sung.wav" "<out name>"` re-voices a
  `tools/sing.py` result: SoulX (cfg 5, 48 steps, 25 s pieces cut at quiet spots) then the RVC model (index 0.6,
  protect 0.33). Eli chose this chain by ear ("test 4"). About 2.5 minutes of work a minute of song.
- Measured on the Byzantine Blessed art Thou (`clone/out/`): voice likeness 0.89 (computer singer 0.68; the singer's
  own other recording 0.94), 95% of notes within a quarter step (computer singer 98%), 69% of words heard back by a
  speech recognizer (computer singer 82%). The new voice is closer to him and a little less clear in the words.
- Version 67: at Eli's word it is in the app as an extra song beside the old one, `song-evl-byz-nv` "Blessed Art Thou,
  O Lord (Byzantine, new voice)", same notes as `song-evlogitaria-byz`, file `blessed-art-thou-byz-newvoice.m4a`
  (BlobDB key `evlogitaria-byz-nv`, `SUNG.evlbyznv`).

## Breathing room in a sung song (21 November 2026)

- Eli could find nowhere to breathe in the Byzantine Blessed art Thou: he runs out halfway through a line. Measured,
  he was right and it is the file's fault. The computer singer never breathes, so `song-evlogitaria-byz` has 3 rests
  of 0.28 s in 3 minutes 17, and one run of 73 seconds with no gap at all. The *Ncense singers pause about 49 times,
  every 2 to 11 seconds, at punctuation (measured by MMS word alignment of Kazan's text against their recording; the
  letter scores are low because of the drone, but every pause lands on a punctuation mark, so the places are right).
- The cure, and the rule for any future sung file: write the breaths into the melody. A breath at every full stop,
  colon, semicolon and question mark, and at a comma when more than three seconds have passed without one. On this
  hymn that is 50 breaths, the longest run 9 seconds, median 3.6, and the breath points land within a second or two
  of the real singers'. The song goes from 3:17 to 3:42.
- In the app: `song-evl-byz-br` "Blessed Art Thou, O Lord (Byzantine, new voice, room to breathe)", melody
  `EVLOGITARIA_BYZ_BR` (the same notes with `r:` rests inserted), file `blessed-art-thou-byz-breath.m4a`
  (BlobDB `evlogitaria-byz-br`, `SUNG.evlbyzbr`), sung by `hisvoice.py`. Measured: 93% of notes within a quarter step,
  71% of words heard back (the version without breaths: 95% and 69%).

## Ears only rebuilt as one screen (21 November 2026)

- Eli's complaint: the page is one huge scroll, the session length and difficulty sit at the top while a lesson's own
  settings are far below, so changing two things means scrolling past twenty cards he never touches. What he asked for:
  pick the lesson from a drop-down, edit everything about that session in one menu, press go.
- Now: the Ears only screen is the lesson drop-down (`earUnitSel`), a one-line summary (`earSum`, which is the button
  that opens the editor) and Start. Everything else lives in a sheet, `#earSheet` (`earSheetOpen`): saved setups, the
  session length and difficulty, the lesson's own card, Sound and voice, and the help. The lesson cards with the
  progress bars are still there, folded away under "All the lessons, with how far you are".
- **Saved setups** (`ison-ear-presets`, `earPresetSave`/`earPresetLoad`/`earPresetDel`, up to 20): a whole screen under
  a name, so the two or three ways he likes to work are one tap apart. The name in use is `presetName` in the settings.
- Learn a song's card is now four sections: the song and part, What to practice, How much repetition, Sound.

## Learn a song, what a session is made of (21 November 2026)

- `SG_STAGES` names the eleven stages of the lesson (notes, long, moves, pieces, joins, mix, think, whole, memory,
  real, rec). Every drill carries its stage (`d.st`), `earSet().songStages` says which are on, and `esStageOn` is the
  gate. Whatever is left is repeated for the whole session, so an hour of nothing but the moves is a valid lesson.
  If everything is off, the whole part alone is given back, never an empty lesson.
- Also added, all in the Learn a song card: **Order** (`songOrder`: build up, the whole part first, a fresh mix every
  round), **How big a piece** (`songPiece`, which drives `earSongPieces`), **Speed** (`songSpeed`, a fixed speed
  instead of the pace's ladder), **Ison drone under everything** (`songDrone`, on the note the part rests on longest or
  an octave below; `lwac` and `hold` now take `o.drone`), **Keep the tone under the recording** (`songToneRec`, default
  on: the `rec` steps carry the notes as `seq` and `bgTimeline` lays a quiet tone line under the singer, one line per
  breath, gain 0.5), **When the lesson reaches the end** (`songLoop`: go round again, or stop), and a button to start a
  long lesson over (clears `songPos`).
- **Singing on your own now defaults to "never"** for Learn a song, as it already does for Master a song: Eli heard no
  difference between With me and Alone and would rather have the repetition. When it is off, the Alone and Check lights
  are taken off the running screen instead of sitting there looking like buttons.
- Checked by measurement in the browser (`window.isonDbg` now also holds `bgTimeline`, `esStageOn`, `SG_STAGES`):
  with only the moves ticked the lesson is the moves alone and runs with no errors; the tone under the recording is
  6 tone lines under the 3 sing-along passes with the setting on and 0 with it off; "stop at the end" gives a 921
  second session where "go round again" fills the full 1800. Eli judges the sound.

## What is remembered (21 November 2026)

- Eli asked that nothing reset: settings stay as he set them when the app is closed and reopened and when he switches
  song, and the key or octave stays with the song it belongs to. Checked in the browser, and nearly all of it was
  already true: every Ears-only setting lives in `ison-ears-set` and survives a reload and a song change (tested with
  45 minutes, Extra hard, two stages, a fixed speed, drone on and the rest); the part (From and To) is per song in
  `ison-ears` `songs`; the **key** ("Change the key") is per song in `ison-songkey` and holds through switching back
  and forth; saved setups are `ison-ear-presets`.
- The one gap was the Songs tab's **Transpose**, which was one global number for every song. Version 72 keeps it per
  song in `ison-songshift` (`songShift`, `songShiftSet`): `loadSource` loads that song's own transpose and the
  drop-down saves it. A song with none yet takes whatever was last used, so nothing moved for existing songs.
  Recordings keep the shared `S.recShift`; the exercises (`ex-`) are not transposed. Because the sung voice only plays
  at the men's octave (`S.shift===-12`), each song now keeps the octave its recording was made in.

- Version 73, two faults in the new screen that Eli hit at once: the "Change the key" sheet opened *behind* the Edit
  sheet (both were `.sheetwrap` at z-index 55 and the Edit sheet comes later in the page), so in Loop a part the key
  could not be changed at all; `#keySheet` is now z-index 70. And the Difficulty row showed for Loop a part, Practice
  a melody and Polish the vibrato, which do not use it (they have their own repeats and speeds): `earPaceField` is
  hidden for units 13, 14 and 15 and the pace is left out of the one-line summary there.

## The breaths measured from the recording (21 November 2026)

- Eli's verdict on the punctuation breaths: the places and lengths were off, and he asked for the real thing, found
  in the *Ncense recording itself, with the choir separated from the drone and every pause timed. He also asked for
  no more new variations of the song: the existing `song-evl-byz-br` is modified in place.
- `tools/pauses.py` (run with the singer's Python) does the finding. The melody moves and the ison stands still, so
  it takes the drone's own harmonics out of the spectrum first (the drone was measured to 20 ms when the recording
  was first taken apart, `~/ison-singer/ncense/drone.json`), then scores a harmonic stack at every pitch from 150 to
  700 Hz every 5.8 ms and calls a frame empty when what is left falls under a fifth of the usual level. 38 gaps of
  0.12 s or more; merged, 28 real pauses.
- `tools/breaths.py` puts them into the melody. The app's melody and the aligned recording are the same 618 tokens
  note for note (checked), so each pause maps to an exact note; it is snapped to the start of a word when it does not
  already fall there (4 of 25 did). A choir staggers its breathing, so the sound never stops for long and the gaps
  alone leave stretches no one person could sing: wherever a breath would have to last more than 7.5 seconds, one
  more is added at the best full stop, colon, semicolon or comma in that stretch (16 of them).
- Version 74 added the breath time on top of the notes and came out 16 s longer than the recording. Eli heard it at
  once ("the length needs to be the same as the one I sent you"). He was right, and the audit said why: the alignment
  the app's timing came from stretches each note over the breath that follows it, so **the time a breath takes is
  already inside the note before it**. Version 76 carves each breath out of that note (at most 60% of it, never
  below 0.14 s, borrowing from up to three notes back), so the song stays its own 3 minutes 16.
- Confidence, measured and worth repeating before trusting this method again: the detection was run at twelve
  settings (four thresholds, three smoothings) and the gap count swings from 21 to 59; only 8 of 36 gaps appear at
  every setting, 21 at three quarters, and a gap's length moves by about 0.13 s between settings. Looking for the
  hiss of an inhalation inside each gap found one in only 2 of 36, so that test says nothing either way in a choir
  recording. What does hold up: 23 of 28 gaps land exactly where a word begins, against 51% of notes by chance.
- Two things were tried and failed, so do not repeat them. (1) Stripping the drone's frequencies out of the audio and
  re-running the word aligner on it: the letter score fell from 0.17 to 0.04, because taking those bins out damages
  the voice too. (2) `tools/retime.py`, a Viterbi that places all 615 notes freely along the measured pitch line:
  the written note was actually sounding in only 42 to 48% of the notes it placed, against 57% for the timing we
  already had, so the pitch tracker is not good enough on a choir to re-time from scratch.
- Giving every note the length the singers give it (their note times tile the song, total slack 0.91 s) does line the
  song up beautifully on paper: every note starts within 22 ms on average of theirs and the song comes to 200.25 s
  against their 200.1 s. Eli rejected it by ear on 21 November 2026: it "goes slow in some parts and extremely quick
  through certain words in a way that seems very unnatural" from a computer voice. `tools/breaths.py`
  `RECORDING_TIMING` is the switch, left off.
- Result, version 76: 41 breaths, 25 of them the singers' own at their own length (0.22 to 0.53 s), 16 added, longest
  run of singing 7.1 s, median 4.7 s, song 3 minutes 16, the same length as before the breaths. File
  `blessed-art-thou-byz-breath4.m4a`, BlobDB key `evlogitaria-byz-br4` (`pubAudio` keeps the first copy of a name
  forever, so a changed file needs a new one). A speech recognizer heard 63% of the words against 70% on the
  version with longer added breaths; Eli has not reported mush, so it is likely the recognizer's segmenting, but
  it is the thing to watch if he says words run together.
- A gotcha worth remembering: the rests in `align2.json` have `t0` present but null, so `n.get('t0',1e9)` returns
  None, not the default, and a naive "first note at or after this time" search stopped at the first rest and mapped
  every later pause to the same note.
- Version 77: the new-voice Byzantine hymn without the breaths (`song-evl-byz-nv`, `blessed-art-thou-byz-newvoice.m4a`)
  is gone, at Eli's word: "I only want one of these that have the new voice." The one that stayed is
  `song-evl-byz-br`, now called simply "Blessed Art Thou, O Lord (Byzantine, new voice)". A one-time move
  (`ison-byznv`) points anything saved on the dropped song, including its key and its octave, at the one that stayed.
  Still in the list, and his to prune when he gets to them: the computer-voice Byzantine (`song-evlogitaria-byz`),
  the two *Ncense recordings and the Kievan setting.

## Inworld Voice Isolator, tried 22 November 2026

- Eli found it and asked whether running it locally would help with recordings that have several voices. It is
  installed on this Mac at `~/ison-singer/isolate` (its own venv, outside the repo): `pip install
  inworld-voice-isolation`, `voice-isolate-doctor --full` to fetch the weights (about 490 MB from Hugging Face),
  then `voice-isolate in.wav out.wav --device mps`. Code and weights are Apache 2.0, no non-commercial or religious
  clause. It runs on the Mac's Metal backend and took 2 min 14 for the 3.5 minute *Ncense recording, writing the
  voice and, beside it, `*_background.wav` with what it removed.
- **It does not help with the choir.** Measured on the *Ncense recording: the ison drone is still there (10.3% of
  the sound before, 8.0% after, so about a fifth of it went), and the MMS word aligner did worse on the isolated
  voice than on the original (mean letter score 0.166 down to 0.109, letters under 0.3 up from 79% to 85%). Gap
  detection on it finds 61 gaps instead of 36 and a higher share hold up across settings, but their lengths wobble
  twice as much (0.27 s against 0.13 s), so it is not a better basis for breath finding. The README is honest about
  why: it is a denoiser, "not a speaker selector", and says nothing about singing or choirs. Both the melody and the
  ison are human voices, so it keeps both.
- Keep the install: it is the right tool for a different job, cleaning room noise out of a recording Eli makes
  himself in the shop, or out of a church recording, where the unwanted sound is not a voice. Do not reach for it
  to separate singers.

## Psalm 118 on the Psalm 91 singer's Tone 7 (22 November 2026)

- What Eli asked for: dissect the built-in Psalm 91/121 recording (Tone 7, the one with the hallelujah he loves), find
  every rule of where the hallelujahs fall and how the lines drop, and set Psalm 118 stanza 1 on it in the singer's voice,
  two ways: exactly his structure, and twice as much reading before each hallelujah. A test; nothing is in the app.
- `tools/scan.py p91.mp3 words_sung.txt scan --spoken "tone seven"` (work folder `~/ison-singer/p91/`): 1,135 notes, home
  E flat 3 (51.04). Steps used, in half steps above home: -1.8, 0, 2.06, 3.1, 3.4 to 3.6 (passing), 5.15.
- **Where the refrains fall.** One line of words is one half-verse. A refrain comes after every TWO lines whatever the
  sentence is doing (19 times; 3 lines 4 times), so it usually lands mid-verse. The psalm opens with three single lines,
  each with its own refrain, the second being the cantor's call Barekhmor (home, 2, 3 falling to 2).
- **The lines.** Line A, the first after a refrain: 2, 2 (later in the psalm a flick to the top, 5), 3, 2, then reads on
  home, and drops on its last four syllables: a held 2 (0.72 s), 3 lifting to 5, 3 falling to 2, a long home note that
  sinks to -1.8 at the very end. Line B, any later line: home, 2, 3 falling to 2, reads on home. Reading syllables 0.37 s
  (middle half 0.32 to 0.41); a scoop up from -1.8 on about one in five. He hardly breathes between lines (median 0.04 s).
- **The line before every Hallelujah** ends with one long figure on its last syllable, 16 times almost note for note:
  home 0.76, 2 0.28, 3 0.27, 5 0.51, 3.4 0.20, 2 0.26, 3 0.37, 2 0.65 (3.4 s). Every other line ends plainly or with the drop.
- **Three hallelujahs.** (1) All through Psalm 91, 17 times: hal scoops to home, le 2 to 3, lu leaps to 5 and falls to 3.6,
  jah holds 5 for a second then 3.3, 2, 3, settling on 2; 4 of the 17 add a quick flick back to 5 in the last turn.
  (2) Only in the Psalm 121 part, 6 times, sung straight on with no breath: 2, 3, then 2 to home, then 2, home, -1.8,
  falling below home. (3) Twice near the end, a doubled slow Hallelujah Hallelujah (about 8.5 s) that climbs to 5 twice.
  Eli said to ignore the end, so the settings use form 1 only.
- **`tools/t7set.py <stanza> <out.mid> [--double]`** writes it (the words come from the notebook, never this repo). Given
  his own Psalm 91 words in his own grouping, its rules put the main note of a syllable on his note 84% of the time and
  the long figure on the right syllable 16 times in 18; the misses are places where he himself varies. `--double` keeps
  his pairs and takes out every other refrain, so the groups are A B A B (the line that led into the dropped refrain
  ends plainly). The Barekhmor word needed a `SAY` entry in `tools/sing.py`.
- Sung (TIGER, then `hisvoice.py`): stanza 1 as he sings it 2:01, twice the reading 1:35, files in `~/ison-singer/p91/out/`.
  92% and 94% of notes within a quarter step; the computer singer gets 94% and 90% of the words across, the trained voice
  83% and 76%. That loss is in hisvoice's first stage (SoulX): RVC's protect (0.33 or 0.5) and index rate (0.6 or 0.4)
  made no real difference (75, 76, 72%). Likeness of the trained voice on this material is 0.948, as close as the Psalm
  23 singer's own other recording (0.943). The Psalm 91 singer himself measures 0.838 against the Psalm 23 singer, so
  he is probably a different man; the voice used is the Psalm 23 singer's.
- `hisvoice.py` now keeps its first stage as `<name> soulx.wav` and takes `--protect`, `--index` and `--rvc-only`, so
  the second stage can be retried in half a minute.

## Guitar lab (23 November 2026)

- What Eli asked for: he plays guitar, knows Psalm 23 Tone 3 by heart, and wants to try it with guitar and maybe learn
  to play it. Ten different guitar parts for that song ("different mindsets", not ten flavours of one idea), in a new
  section where he picks the song and the part, sets the guitar volume, presses play, and the two stay exactly
  together. Mid-task he added: a normal acoustic (steel string) guitar sound, not harsh, and "as much
  customizability where it doesn't break": sliders instead of hard-coded numbers, one of them sliding from nylon to
  steel, one for the room echo. He does not want a guitar sound coded from scratch; it must be real recorded guitars.
- It is the **Guitar tab** (eighth tab; `v-guitar`, everything named `gt...`, settings in `ison-gt`). The tab bar is
  now 8 across: at 375 wide each tab is 43 px and the longest labels are 42, so there is no room for a ninth.
- **The chords** (worked out from the melody, since the recording is one unaccompanied voice). His ladder is
  C# D# E F# G# A B with G# as home: G sharp Phrygian. Five chords only, each named by its job so any key can play it:
  `i` G#m (home), `II` A (the half step above home), `iv` C#m, `VI` E, `vii` F#m. No B major: in the low close
  his held E would sit a half step over the chord's D#. The same shape always takes the same chords:
  opening A = C#m, then F#m on the last word or two; low close B = E, then C#m on the last syllable; middle C = G#m,
  F#m, G#m; full close D and the recovery I = G#m, A, F#m, G#m (home arrives on the long last syllable);
  second opening E = E throughout; the descent H = F#m, C#m; the climb F = E, then A on the top note; the height
  G = E, A, G#m. Written per phrase in `GT_SONGS.psalm23.ch` (`syllable:role`, `0.1` = at the second note of
  syllable 0, used once, in the last line).
- Measured against the scan: 72% of the singing time is on a note of the chord, 17% on a soft neighbour (a seventh or
  ninth), 7% a half step under a chord note, 4% a half step over one (the harsh kind). Longest harsh one 0.28 s
  ("still", "name's", "with", "my"). Longest soft rub: G# held over the A chord for half a second ("staff", "dwell").
  A chord fitter left to itself chose F#m almost everywhere (everything is a soft neighbour of it), so the plan was
  written by hand, shape by shape, and then measured.
- **Guitar shapes.** Capo = (4 + key) mod 12 with the E family (Em, F, Am, C, Dm) while that is 7 or less; otherwise
  the A family (Am, Bb, Dm, F, Gm) with capo 5 lower. As sung: capo 4. Down 2: capo 2. Down 4: no capo. Down 5: A
  family, capo 6. The guitar the app plays uses these very fingerings (`GT_FAM`, frets counted from the capo), so
  what he hears is what his hands would play. The key is the app's own per-song key (`keyRowIds` entry `gt`).
- **Following the singer.** There is no beat. Every pluck is tied to a syllable start, a note start inside a
  syllable, or the end of a syllable (answers in his breaths), all from the scan (`GT_SONGS.psalm23.syl`: start,
  length, how late the vowel begins, text, notes as ladder steps). 11 of the 175 syllables begin their vowel 50 to
  120 ms after the aligner's mark (measured with pyin); the guitar follows the vowel.
- **The ten parts** (`GT_PARTS`, one generator each, `gtp...`): the ison (one low note under each phrase); one slow
  strum per chord; strum and walk (big strum, then bass notes stepping to the next root, skipping any that would
  sit a half step from his note); rolling arpeggio; thumb and pinch; the melody with him (oud style, tremolo on notes
  of 0.62 s or more, over the open low string); answers in his breaths (his own last notes an octave up, nothing
  while he sings); open fifths (no thirds); bells over a bass; Spanish (hard strums, upstroke, a two-stroke roll
  into the last chord of each low close and full close).
- **The sound.** Two real guitars from the FreePats project, each note cut to its pluck, tuning measured to a cent,
  packed into one file by `tools/guitarpack.py`: `guitar-nylon.m4a` (Spanish classical guitar, CC0, 19 notes) and
  `guitar-steel.m4a` (FSS Steel-String Acoustic Guitar, a Seagull, samples by Gary Campion of FlameStudios, GNU GPL 3
  or later with the FreePats exception that music made with it is not covered; 17 notes of the loud layer). The page
  plays the nearest note a little faster or slower (never more than about one half step). A string sounds one note
  at a time; a chord change stops every string whose fret the new shape does not hold (`gtSynth`).
  **The GPL file matters if the app ever goes to the App Store** (GPL 3 and the App Store terms do not mix): swap
  the steel guitar for another sample set first, or ask. The nylon one is free of any condition.
- **The sound lab** (`GT_SND`, each 0 to 10, kept in `ison-gt` `snd`): Strings (nylon to steel, both blended in
  between, default 5), Tone, Body, Pluck, Ring, Room (the Freeverb design), Strum (how spread a strum is), Looseness
  (hand-like differences in time and strength), Timing (the whole guitar earlier or later, 15 ms a step). Plus guitar
  and singer volume (3 dB a step) and Tuning: with the singer (guitar 18 cents flat, as he sings) or for a real
  guitar (the singer resampled up 18 cents, about 1% quicker, every time divided by the same ratio).
  Every part is first brought to the same loudness against the singer (8 dB under him at "6 of 10", `gtMix`,
  `gtLoud`), so the balance does not jump when the part changes.
- **Playing.** Voice and guitar are made into one WAV at 32 kHz and played through an audio element, so they cannot
  drift and it plays with the phone locked. Four layers are remembered (`gtBuild`): the singer, the guitar as
  played, the guitar after tone, body and room, the mix. A change redoes only what depends on it and the new sound
  takes over at the same word about a second later (measured on this Mac: first Play 0.8 s, a change 0.5 to 0.9 s).
  One build at a time (`GT.busy`): two at once made the first Play take 4 seconds.
- `gtAlign`: browsers hand a decoded mp3 back a few hundredths of a second apart. `GT_SONGS.psalm23.fp` holds where
  five loud moments of the recording fall; the page finds them and slides the voice onto the guitar. Chromium
  here needs no shift (0 samples); Safari on the phone could not be tested from this Mac.
- **The engine is one block** in index.html between `GT-ENGINE-START` and `GT-ENGINE-END`, free of page things.
  `node tools/guitar.mjs <folder> [--part walk] [--key -2] [--concert] [--strings 5 --tone 5 ...] [--stems]` cuts
  that block out and runs it, so the Mac renders what the app plays (the two decoders differ a little: guitar
  loudness 0.15 dB apart). On the Mac `--key` moves only the guitar, not the singer. The ten recordings sent to Eli
  are in `notes/guitar-lab/` (gitignored).
- **Checked by measurement only, Claude cannot hear it.** Every guitar note within 1 cent of its target (45 notes,
  both guitars, at the singer's tuning). Each pluck's sound begins a median 8 to 17 ms after its written time. In
  the page: his home note measured 55.9 as sung and 53.9 two down, the guitar's low C# 48.84 against a target of
  48.82. Guitar against voice 7 to 9 dB under by the loudness measure. Nobody has judged whether the chords or the
  ten parts sound good: that is Eli's ear. Likely first complaints and where to turn: harsh = Tone, Pluck, Strings;
  guitar early or late = Timing; a chord he dislikes = the `ch` string of the song.
- What was tried and dropped: the FluidR3 General MIDI nylon guitar from gleitz/midi-js-soundfonts (CC BY 3.0) is
  only 3.2 s a note at 38 kbps; a roll of strokes starting 0.2 s before a close put the home chord under his
  neighbour note, so the roll starts 0.13 s before, softly, on the top strings.
- To add a song: it needs the deep scan (`tools/scan.py`), its phrases, a chord for every stretch, and an entry in
  `GT_SONGS`. The scripts that wrote the Psalm 23 entry and measured it are kept in `~/ison-singer/guitar/` (`chords.py`
  the chord plan and its score, `onset.py` the vowel starts, `gen_data.py` the entry itself, `verify.py` and `pt.py`
  the measurements); they are written for Psalm 23 and need editing for another song. Psalm 23 Tone 4 has a scan and 26 phrases already (`~/ison-singer/p23t4/scan/`).


## Sing it without the tone (24 November 2026)

- What Eli asked for: about 40 hours into Psalm 23 Tone 3 he sings it well with the tone but loses it the moment
  nothing is playing. A lesson for exactly that stage, researched, and with every part of the lesson a control he
  can change himself ("everything you are hard coding as the lesson, make that a way for me to edit it"), so he does
  not have to come back for each tweak.
- It is Ears only **unit 16, "Sing it without the tone"** (everything named `nt...`; card `#ntBox`; settings in
  `earSet().nt`, defaults `NT_DEF`). Any song with a song map (`SM`), its own part (From, To), the app's key row (`nt`).
- **The lesson is a list of passes he edits** (`ntRows`, kept in `nt.ladder`; `NT_LADDERS` are only ready-made starting
  plans: Fade the tone away, Test yourself first, Trade lines with the tone, Hear it inside first, Landing notes, Only
  the ison under you, Performance). A pass = one time through a piece with: a name, tone volume 0 to 10, singer
  volume 0 to 10, which notes they play (`NT_SHAPES`, `ntMask`: every note, first note, first line, first or last note
  of every line, odd or even lines, long notes only, all but the long notes), the word said before it (`NT_CUES`),
  times, its own speed, and four ticks (starting note first, check note after, ison under it, a tick on each note).
  Passes can be switched off, moved, copied, removed and added. Tone 0 and singer 0 is singing alone.
- Around the passes: how the part is cut (`ntChunks`: one piece at a time, growing from the start, growing from the
  end, the whole part; phrases in a piece; move on by fewer to overlap; order; times through the list), the whole
  part alone at the start (cold) and after the pieces, what checks it, the starting note and check note (which note,
  how long, how loud, silence after), the help getting softer each round (`fadeT`, `fadeV`, `fadeFloor`; Listen and
  Check passes keep their volume), room after singing alone, pause between passes, what counts as a long note, and
  whether words are spoken. "Carry on next session" keeps the piece reached (`ison-nt-pos`, saved from `bgLog`).
- A change made during a session (the "Change this lesson" button on the running screen opens the Edit sheet) takes
  effect at the next pass (`ntChanged` then `bgReplanFromNext`). Slower and Faster change the speed by 5%.
- **Engine additions** (additive, any unit may use them): a `play` step takes `tg` (tone volume 0 to 1, 0 = no tone),
  `vg` (singer gain, overrides the song-voice setting), `tk` (a tick at each note start) and `droneD` (drone length
  when one pass is split into several play steps). `ntPlay` splits a pass into play steps wherever the help turns on
  or off, so the singer can be cut note by note too.
- **The research behind it** (24 November 2026): the guidance hypothesis (help that is always there during practice
  gives the best practice and the worst result without it; fading the help and giving the answer afterwards hold up
  better; Salmoni, Schmidt and Walter 1984, Winstein 1994, reviewed by Sigrist 2013, with some sound-feedback studies
  disagreeing); the testing effect (recall beats repetition; only lightly tested on music so far); Mauch, Frieler and
  Dixon 2014 on unaccompanied singers (steps are kept, the starting pitch slowly drifts), hence the check note;
  Chaffin on performance cues (landmarks to restart from), hence shuffled pieces and growing from the end. No study
  gives the right numbers for a song like this; the defaults are a reasoned start and Eli tunes them.
- Hours, as told to Eli (my estimate, no study gives one): from where he is, roughly 15 to 30 hours of mostly
  tone-free practice to sing it start to finish from memory in tune; the finest vibrato is general voice skill and
  takes months to a year. He had earlier asked for singing on your own to be off by default in Learn a song and
  Master a song; that stays as it is, this lesson is where the tone-free work lives.
- **Checked by measurement only.** In the browser: the session builds and plays, a live change is taken up, and a
  rendered session measured pass by pass: tone at 5 with the singer at 8 about -16 dB together, the softer tone pass
  -22 dB, the alone pass silent apart from its starting and check notes, the singer alone at 8 about -20 dB (so the
  defaults were raised: singer 10 in Listen and Check passes). The app does not hear him in this lesson.
- Not built: hearing one pass on its own before a session (a preview button), and spoken phrase numbers.
- Hours per song (version 80, Eli's request): this lesson counts its own playing time for each song (`ison-nt-time`:
  seconds, per day, sessions; `ntTimeAdd` from `bgLog`, pauses not counted) and shows it on the card against a goal
  (`nt.goalH`, default 30 hours, his own target: double the estimate because he is a new singer), with today, the
  last 7 days and weeks to go at this pace. He can type a corrected figure. Other lessons still count per lesson only.
- **He pops in and out** (version 81). Eli tried version 79 in the shop and it did not work by ear: it did not say
  what was coming, and the cold run was a long silence with no word of what it was. What he asked for instead, and
  what the lesson now starts as: he sings the whole part while the singer and the tone join him for the first moment,
  drop out, pop back in for a moment now and then, and join again at the end, so he can tell he is on the right note
  and at the right pace. It is pass shape `pop` (`ntPops` makes the windows, `ntCut` cuts notes at their edges) with
  its own section "Popping in and out": percent of the piece (default 20, not counting start and end), seconds each
  time (1.5), spread evenly or at random, new moments every time or the same, seconds with him at the start (1.5)
  and at the end (1.5), and percent less each round. His plan: lower the numbers over the weeks. Plan `pop` is the
  default (whole part as one piece, no cold run, no whole-part finale); a plan may carry settings (`set`). A one-time
  move (`nt.v` 2) put anyone who had opened the lesson onto it.
- Spoken parts: the first pass of each piece is announced with clips the app already had ("the whole part", or
  "phrase" and its number up to 30; `ntVo`, setting `sayPiece`), and passes can say "Sing with the singer", "Singer
  only" or "Tone only" (`NT_CUE_VO`). No new clips were recorded; phrases past 30 get the word without a number.
  Rule for this lesson and any other Ears only work: he cannot look, so nothing may start without saying what it is,
  and no long silence without a word before it.
- Measured (8 phrases of Psalm 23, 40 s, 20%, 1 s, even): sound in exactly the planned windows, 1.5 s at each end and
  eight 1 s windows 3.2 s apart.
- Version 82, after Eli's first look at the pop-in plan: the pop settings were in a section far below the pass, so the
  pass's own line ("first 1.5 s...") read to him as hard coded. He uses this lesson as a modified Loop a part: one
  way of helping, the same all session, changed only by him. So the card now opens with **"How he helps you"**
  (`#ntPopBox`): tone volume and singer volume (they edit the pop pass, `ntRowStep`), speed, percent, seconds each
  time, even or random, start and end seconds. Plans and the list of passes are folded under "Advanced". The running
  screen has the same four as plus and minus buttons (`#ntLiveBox`: percent, seconds, tone, singer). The Easy to
  Extra hard row had come back for this lesson because `renderLoop` un-hid it; fixed there. Nothing in the pop plan
  changes by itself during a session (`popFade`, `fadeT`, `fadeV` are 0).
