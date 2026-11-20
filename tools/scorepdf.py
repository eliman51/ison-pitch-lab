#!/usr/bin/env python3
"""Read an engraved PDF of sheet music exactly: every voice, note, length and word.

    python3 tools/scorepdf.py <score.pdf>                       what is in it, voice by voice
    python3 tools/scorepdf.py <score.pdf> --voice 0 --typed     the top voice in the app's own notation
    python3 tools/scorepdf.py <score.pdf> --voice 0 --typed --shift -5 --key D

Most sheet music on the web is a PDF made by a music program (MuseScore, Sibelius, Finale, LilyPond). In that kind
of file the noteheads are not a picture: they are letters of a music font sitting at exact places on the page. So
nothing has to be guessed or recognised. This reads the staff lines out of the page's drawings and the noteheads,
dots, clefs and key signature out of its text, and works out the pitch from where each notehead sits.

That is why no music-reading program (OMR) is needed for this kind of file, and why what comes out is exact rather
than a good guess. For a photograph or a scan it is the other way round: nothing is in the file but ink, and a
reader such as homr or Audiveris is the right tool.

What it needs: PyMuPDF (`import fitz`), which is already on this Mac's own python3.
What it cannot do: handwriting, scans, two voices written on one staff, grace notes, triplets, repeats and endings
(it reads them as plain notes in page order), and it assumes one key signature for the whole piece. The notes and
their lengths come out exact; the WORDS do not. Syllables are cut apart by the gaps between letters, which splits
a wide capital off its own word ("O ur"), so read the words through and fix them by hand before using them.

Checks worth running on anything it reads (both were run on the Kedrov Our Father):
  * every system's voices must add up to the same number of beats (`--check`), which catches a missed dot or note
  * the voices sounded together should be ordinary chords; a misread note usually shows up as a strange one
"""
import argparse, collections, os, sys

try:
    import fitz
except ImportError:
    sys.exit('This needs PyMuPDF. The Mac\'s own python3 has it: run with python3, not the singer\'s venv.')

NOTE = {0xE0A2: 4.0, 0xE0A3: 2.0, 0xE0A4: 1.0}        # whole, half, black notehead (in quarter-note beats)
DOT, SHARP, FLAT, NAT = 0xE1E7, 0xE262, 0xE260, 0xE261
CLEF = {0xE050: 'G', 0xE052: 'G8', 0xE062: 'F'}        # treble, treble sung an octave down, bass
STEPS = 'CDEFGAB'
SEMI = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
SHARPS = 'FCGDAEB'                                     # the order sharps are written in a key signature
FLATS = 'BEADGCF'


def staves(page):
    """the five-line staves on a page, top to bottom"""
    seg = []
    for g in page.get_drawings():
        for it in g['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                if abs(a.y - b.y) < 0.3 and abs(a.x - b.x) > 80:
                    seg.append((round(a.y, 1), min(a.x, b.x), max(a.x, b.x)))
            elif it[0] == 're':
                r = it[1]
                if r.height < 1.2 and r.width > 80:
                    seg.append((round(r.y0, 1), r.x0, r.x1))
    by = collections.defaultdict(list)
    for y, x0, x1 in seg:
        by[y].append((x0, x1))
    out, cur = [], []
    for y in sorted(by):
        if cur and y - cur[-1] > 8:
            out.append(cur); cur = []
        cur.append(y)
    if cur:
        out.append(cur)
    res = []
    for grp in out:
        for i in range(0, len(grp) - 4, 5):
            L = grp[i:i + 5]
            xs = [x for y in L for x in by[y]]
            res.append(dict(lines=L, x0=min(a for a, b in xs), x1=max(b for a, b in xs)))
    return res


def glyphs(page):
    out = []
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                for ch in s['chars']:
                    out.append(dict(c=ord(ch['c']), t=ch['c'], x=ch['origin'][0], y=ch['origin'][1],
                                    font=s['font'], size=s['size']))
    return out


def pitch(pos, clef):
    base = {'G': ('E', 4), 'G8': ('E', 3), 'F': ('G', 2)}[clef]
    k = STEPS.index(base[0]) + 7 * base[1] + pos
    return STEPS[k % 7], k // 7


def read(path, music_font=None):
    """-> rows [{page, system, voice, x, letter, octave, midi, beats, word}], and how many sharps or flats"""
    doc = fitz.open(path)
    fonts = collections.Counter()
    pages = []
    for page in doc:
        G = glyphs(page)
        for g in G:
            if g['c'] in NOTE or g['c'] in CLEF:
                fonts[g['font']] += 1
        pages.append((page, G))
    mf = music_font or (fonts.most_common(1)[0][0] if fonts else None)
    if not mf:
        sys.exit('No music font found: this looks like a scan, not an engraved PDF. Try homr or Audiveris.')
    rows, acc = [], 0
    for pi, (page, G) in enumerate(pages):
        st = staves(page)
        st.sort(key=lambda s: s['lines'][0])
        if not st:
            continue
        per = len(st)
        M = [g for g in G if g['font'] == mf]
        clef, keyacc = {}, {}
        for g in M:
            if g['c'] in CLEF:
                for i, s in enumerate(st):
                    if s['x0'] - 14 <= g['x'] <= s['x1'] + 6 and s['lines'][0] - 14 <= g['y'] <= s['lines'][4] + 14:
                        clef.setdefault(i, CLEF[g['c']]); break
        for g in M:
            if g['c'] in (SHARP, FLAT):
                for i, s in enumerate(st):
                    if s['x0'] - 4 <= g['x'] <= s['x0'] + 34 and s['lines'][0] - 10 <= g['y'] <= s['lines'][4] + 10:
                        keyacc.setdefault(i, [0, 0])
                        keyacc[i][0 if g['c'] == SHARP else 1] += 1; break
        if keyacc:
            n = collections.Counter(tuple(v) for v in keyacc.values()).most_common(1)[0][0]
            acc = acc or (n[0] if n[0] else -n[1])
        notes = []
        for g in M:
            if g['c'] not in NOTE:
                continue
            for i, s in enumerate(st):
                if not (s['x0'] - 6 <= g['x'] <= s['x1'] + 6 and s['lines'][0] - 22 <= g['y'] <= s['lines'][4] + 22):
                    continue
                sp = (s['lines'][4] - s['lines'][0]) / 4
                pos = round((s['lines'][4] - g['y']) / (sp / 2))
                p, o = pitch(pos, clef.get(i, 'G'))
                notes.append(dict(page=pi, staff=i, x=g['x'], y=g['y'], beats=NOTE[g['c']], letter=p, octave=o))
                break
        for g in M:
            if g['c'] != DOT:
                continue
            c = [n for n in notes if 2 < g['x'] - n['x'] < 16 and abs(g['y'] - n['y']) < 3.6]
            if c:
                min(c, key=lambda n: g['x'] - n['x'])['beats'] *= 1.5
        # words under each staff, cut into syllables by the gaps between them
        words = collections.defaultdict(list)
        sizes = collections.Counter(round(g['size'], 1) for g in G if g['font'] != mf)
        lyr = sizes.most_common(1)[0][0] if sizes else None
        for g in G:
            if g['font'] == mf or round(g['size'], 1) != lyr:
                continue
            for i, s in enumerate(st):
                if s['x0'] - 14 <= g['x'] <= s['x1'] + 14 and s['lines'][4] + 3 <= g['y'] <= s['lines'][4] + 24:
                    words[i].append(g); break
        syl = {}
        for i, gs in words.items():
            gs.sort(key=lambda g: g['x'])
            S, cur, x0, last = [], '', None, None
            for g in gs:
                if last is not None and g['x'] - last > 1.6 and cur:
                    S.append((x0, cur)); cur, x0 = '', None
                if x0 is None:
                    x0 = g['x']
                cur += g['t']; last = g['x'] + g['size'] * 0.52
            if cur:
                S.append((x0, cur))
            syl[i] = [(x, t) for x, t in S if t.strip(' -_')]
        for i in range(per):
            v = sorted([n for n in notes if n['staff'] == i], key=lambda n: n['x'])
            for n in v:
                n['word'] = ''
            for x, t in syl.get(i, []):
                if not v:
                    continue
                n = min(v, key=lambda n: abs(n['x'] - x))
                if n['word']:
                    free = [q for q in v if not q['word']]
                    n = min(free, key=lambda q: abs(q['x'] - x)) if free else n
                n['word'] = t
            for n in v:
                sh = 1 if acc > 0 and n['letter'] in SHARPS[:acc] else -1 if acc < 0 and n['letter'] in FLATS[:-acc] else 0
                rows.append(dict(page=pi + 1, system=i // 4 + 1, voice=i % 4, x=n['x'], beats=n['beats'],
                                 letter=n['letter'], octave=n['octave'], word=n['word'],
                                 midi=(n['octave'] + 1) * 12 + SEMI[n['letter']] + sh))
    return rows, acc


def name(m):
    return NAMES[int(m) % 12] + str(int(m) // 12 - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--voice', type=int, default=None, help='0 is the top staff of each system')
    ap.add_argument('--typed', action='store_true', help='print it in the app\'s notation (Note:beats:word)')
    ap.add_argument('--shift', type=int, default=0, help='move every note this many half steps')
    ap.add_argument('--check', action='store_true', help='do the voices of each system add up?')
    a = ap.parse_args()
    rows, acc = read(a.pdf)
    if not rows:
        sys.exit('No notes found.')
    print('%d notes, key signature %d %s' % (len(rows), abs(acc), 'sharps' if acc > 0 else 'flats' if acc else ''), file=sys.stderr)
    if a.check:
        by = collections.defaultdict(lambda: collections.defaultdict(float))
        for r in rows:
            by[(r['page'], r['system'])][r['voice']] += r['beats']
        bad = 0
        for k in sorted(by):
            t = [round(by[k][v], 2) for v in sorted(by[k])]
            if len(set(t)) > 1:
                bad += 1; print('page %d system %d: the voices do not add up: %s' % (k[0], k[1], t), file=sys.stderr)
        print('%d systems checked, %d do not add up' % (len(by), bad), file=sys.stderr)
    if a.voice is None:
        for v in sorted(set(r['voice'] for r in rows)):
            ms = [r['midi'] for r in rows if r['voice'] == v]
            print('voice %d: %d notes, %s to %s' % (v, len(ms), name(min(ms)), name(max(ms))), file=sys.stderr)
        return
    v = [r for r in rows if r['voice'] == a.voice]
    if a.typed:
        toks = [name(r['midi'] + a.shift) + ':' + ('%g' % r['beats']) + (':' + r['word'] if r['word'] else '') for r in v]
        for i in range(0, len(toks), 8):
            print(' '.join(toks[i:i + 8]))
    else:
        for r in v:
            print('%-5s %-5g %s' % (name(r['midi'] + a.shift), r['beats'], r['word']))


main()
