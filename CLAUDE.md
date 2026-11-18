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
- Checked by measurement, all 22 (76 to 97 s each, 31:37 together): every stanza has 99 to 100% of its notes within
  half a step; a speech recognizer heard 91 to 100% of the words (17 the lowest at 88%; most misses are near
  sound-alikes such as "searched" heard as "search"); and laid over the singer's own recording (timing lined up, five
  half steps down) the sung line is within three quarters of a half step of his 94 to 97% of the time. Every join
  between shapes is one the singer makes (shapes.py checks this). The measuring scripts (verify.py, similar.py,
  singall.sh) were scratch files; verify.py's method is the one described under "Heart song".
- Eli is working through the stanzas one at a time, starting at 4, changing each until it is the one version he will
  master. Changes so far (each re-sung stanza gets its letter in `R118P_REV`): stanza 4 `b`: "earth" in the first line
  carries on up to the held home note and ends there, a short lift, then a quick "Give me" on the next two notes (before,
  "Give" was the held note and the th of "earth" ran into it).
  Stanza 4 `c`: from "and I shall meditate" on, rebuilt as `A B | A B | C D | E H | I D | F G D` (86 s; the earlier
  layout is kept as `4.s.v2.txt`). What he asked, and it is a rule for every stanza from now on: nothing crammed, and no
  two sentences run together as if they were one. A sentence must end on a shape that closes and breathes (B, H or D);
  A, C, E, I, F and G run straight on, so they only carry the first half of a sentence. In sentence pairs the song
  allows: `A|B`, `C|D`, `E|H`, `I|D`, `F|G D` or `F G|D`. Making a stanza longer for this is fine with him. The other
  stanzas were laid out before this rule and several break it (a sentence ending on E, I, F or G); fix each as he
  reaches it.
- Key advice given to Eli (18 November 2026): this melody sits in the middle and only touches the top, while its low
  notes are long, so choose the key by the low notes; stay at "As sung" or at most 1 or 2 down, and keep one key.

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

## Every change

1. Edit `index.html` (or the other files).
2. `python3 tools/check.py` must say OK. Raise `APP_VER` in index.html and `CACHE` in sw.js by one (the version shows on the Chant tab, with a "Get the newest version" button, because phones kept showing old copies).
3. Commit with a plain message and push to `main`. Tell Eli what changed and what to try.
4. Only if Eli wants the artifact copy current: `python3 tools/artifact.py` and publish it.
