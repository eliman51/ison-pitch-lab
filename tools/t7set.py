#!/usr/bin/env python3
"""A Psalm 118 stanza set the way the Psalm 91/121 singer sings Tone 7, every rule measured from his recording.

    python3 tools/t7set.py <stanza> <out.mid> [--double]       then tools/sing.py, then the trained voice

The psalm's words are read from ~/ison-singer/notebook/verses.txt (outside this repository; never commit them).

What the recording shows (tools/scan.py on the built-in Psalm 91/121 recording, 22 November 2026; all pitches are
half steps above his home note, E flat 3, 51.04, and all lengths are medians over every instance):

  The lines. Every line of the words is one half-verse, and a refrain comes after every TWO lines, whatever the
  sentence is doing, so it usually lands in the middle of a verse ("...the terror of the night / Hallelujah / nor of
  the arrow that flies by day"). Now and then a group has three lines. The psalm opens with three single lines, each
  with its own refrain, and the second of those refrains is the cantor's call Barekhmor instead of Hallelujah.

  Line A, the first line after a refrain: 2, then 2 (later in the psalm a flick to the top, 5), then 3, then 2, then
  it reads on home; its last four syllables are the drop: a held 2, a 3 lifting to the top 5, 3 falling to 2, and a
  long home note that sinks under itself at the very end.
  Line B, any later line: home, 2, then 3 falling to 2, then it reads on home to the end.
  The line just before a Hallelujah ends with his long figure on its last syllable (16 times, 3.4 s, almost note for
  note the same): home 0.76, 2 0.28, 3 0.27, top 0.51, 3.4 0.20, 2 0.26, 3 0.37, 2 0.65.
  Hallelujah (the form he uses all through Psalm 91, 17 times): hal scoops up from below to home, le 2 to 3, lu leaps to
  the top and falls to 3.6, jah holds the top a second, then 3.3, 2, 3, and settles on 2.
  Now and then (4 times in 17) the last turn of jah or of the long figure has a quick flick back up to the top.
  Barekhmor: home, 2, then 3 falling to 2.
  While reading on home he scoops up from the step below on about one syllable in five; the reading syllables are
  0.37 s each (middle half 0.32 to 0.41); he barely breathes between lines (median gap 0.04 s, longest 0.31).

--double sets twice as much reading before each refrain: the groups of two become groups of four, which is his two
pairs with the refrain between them taken out (the line that led into it then ends plainly on home).
"""
import os, re, struct, sys

NOTEBOOK = os.path.expanduser('~/ison-singer/notebook/verses.txt')
HOME = 51.04
P = {-2: -1.80, 0: 0.0, 2: 2.06, 3: 3.10, 3.4: 3.40, 3.6: 3.60, 5: 5.15}

# ---- the words: syllables and accents from the CMU dictionary, with the church readings the singer uses
import cmudict
CMU = cmudict.dict()
SAY = {'blessed': 2, 'hallelujah': 4, 'barekhmor': 3}      # syllables the dictionary would get wrong or lacks


def syllables(word):
    """-> list of accents (True for a stressed syllable) for one word"""
    w = re.sub(r"[^a-z']", '', word.lower())
    if w in SAY:
        n = SAY[w]
        return [True] + [False] * (n - 1) if w != 'hallelujah' else [False, False, True, False]
    pr = CMU.get(w)
    if pr:
        st = [ph[-1] for ph in pr[0] if ph[-1].isdigit()]
        return [s in '12' for s in st] or [True]
    n = max(1, len(re.findall(r'[aeiouy]+', w)) - (1 if w.endswith('e') and len(w) > 3 else 0))
    return [True] + [False] * (n - 1)


def line_syls(text):
    """-> [(word, syllable index, accent)] for one line"""
    out = []
    for w in text.split():
        for k, a in enumerate(syllables(w)):
            out.append((w, k, a))
    return out


# ---- notes: (pitch in half steps above home, seconds, word, syllable index); a held note has syllable index -1
def note(step, dur, w=None, k=-1):
    return [P[step] if step in P else step, dur, w, k]


def reading(syls, start, n_end, scoop_every=5):
    """syllables start..n_end on home, a scoop from below on about one accented syllable in five"""
    out, c = [], 0
    for i in range(start, n_end):
        w, k, a = syls[i]
        d = 0.40 if a else 0.33
        if a:
            c += 1
            if c % scoop_every == 2 and d > 0.3:
                out += [note(-2, 0.10, w, k), note(0, d - 0.10)]; continue
        out.append(note(0, d, w, k))
    return out


def line_A(syls, late=False, end='drop'):
    """first line after a refrain: 2 (2|5) 3 2, read on home, then the drop or the long figure"""
    n = len(syls); out = []
    head = [2, 5 if late else 2, 3, 2]
    h = min(len(head), max(0, n - 5))
    for i in range(h):
        w, k, a = syls[i]
        out.append(note(head[i], 0.34 if i else 0.36, w, k))
    tail = 4 if end == 'drop' else 1
    out += reading(syls, h, n - tail)
    out += ending(syls, end)
    return out


def line_B(syls, end):
    """a later line: home, 2, 3 falling to 2, read on home, then its ending"""
    n = len(syls); out = []
    head = [(0,), (2,), (3, 2)]
    h = min(len(head), max(0, n - 3))
    for i in range(h):
        w, k, a = syls[i]
        if len(head[i]) == 2:
            out += [note(3, 0.15, w, k), note(2, 0.22)]
        else:
            out.append(note(head[i][0], 0.36, w, k))
    tail = 4 if end == 'drop' else 1
    out += reading(syls, h, n - tail)
    out += ending(syls, end)
    return out


def line_read(syls, end):
    """the opening single lines: read on home from the first syllable"""
    tail = 4 if end == 'drop' else 1
    return reading(syls, 0, len(syls) - tail) + ending(syls, end)


def ending(syls, end, flick=False):
    n = len(syls)
    if end == 'drop':                         # held 2, 3 up to the top, 3 down to 2, long home sinking under itself
        (w1, k1, _), (w2, k2, _), (w3, k3, _), (w4, k4, _) = syls[n - 4:]
        return [note(2, 0.72, w1, k1), note(3, 0.20, w2, k2), note(5, 0.16), note(3, 0.20, w3, k3), note(2, 0.18),
                note(0, 0.82, w4, k4), note(-2, 0.14)]
    w, k, a = syls[-1]
    if end == 'plain':
        return [note(0, 0.48, w, k)]
    # the long figure that leads into a Hallelujah
    f = [note(-2, 0.12, w, k), note(0, 0.76), note(2, 0.28), note(3, 0.27), note(5, 0.51), note(3.4, 0.20), note(2, 0.26)]
    f += [note(3, 0.15), note(5, 0.08), note(3.4, 0.12)] if flick else [note(3, 0.37)]
    return f + [note(2, 0.65)]


def hallelujah(flick=False):
    w = 'Hallelujah'
    out = [note(-2, 0.15, w, 0), note(0, 0.29), note(2, 0.22, w, 1), note(3, 0.20), note(5, 0.17, w, 2), note(3.6, 0.23),
           note(5, 1.05, w, 3), note(3.4, 0.17), note(2, 0.24)]
    out += [note(3, 0.15), note(5, 0.07), note(3.4, 0.11)] if flick else [note(3, 0.34)]
    return out + [note(2, 0.65)]


def barekhmor():
    w = 'Barekhmor'
    return [note(0, 0.32, w, 0), note(2, 0.28, w, 1), note(3, 0.24, w, 2), note(2, 0.32)]


def rest(d):
    return [[None, d, None, -1]]


# ---- the plan
def plan(n, double):
    """-> groups of line numbers (0-based) and the refrain after each: his opening of single lines, then pairs"""
    G = []
    if not double:
        G += [([0], 'H'), ([1], 'B'), ([2], 'H')]
        i = 3
        while i < n:
            left = n - i
            take = 3 if left == 3 else 2
            G.append((list(range(i, i + take)), 'H')); i += take
    else:
        G += [([0, 1], 'H'), ([2, 3], 'B')]
        i = 4
        while i < n:
            take = min(4, n - i)
            G.append((list(range(i, i + take)), 'H')); i += take
    return G


def build(lines, double):
    out = barekhmor() + rest(0.18)
    hcount = 0
    for gi, (idx, ref) in enumerate(plan(len(lines), double)):
        late = gi >= 5                        # he lifts the second syllable of line A to the top later in the psalm
        for j, li in enumerate(idx):
            syls = line_syls(lines[li])
            last = j == len(idx) - 1
            if last and ref == 'H':
                end = 'long'
            elif last and ref == 'B':
                end = 'drop'
            elif j == 0 or (double and j == 2):
                end = 'drop'
            else:
                end = 'plain'
            if len(idx) == 1 and ref == 'H' and not double:
                part = line_read(syls, end)                   # his single opening lines: read, then the long figure
            elif j == 0 or (double and j == 2):
                part = line_A(syls, late=late, end=end)
            else:
                part = line_B(syls, end)
            if end == 'long' and hcount in (1, 4):
                part = part[:-(len(ending(syls, 'long')))] + ending(syls, 'long', flick=True)
            out += part + rest(0.05 if not last else 0.2)
        if ref == 'H':
            out += hallelujah(flick=hcount in (2, 5)) + rest(0.15); hcount += 1
        else:
            out += barekhmor() + rest(0.15)
    return out


# ---- the notes file the singer reads (whole word on its first note, + for its next syllable, - for a held note)
def vlq(v):
    b = [v & 127]; v >>= 7
    while v:
        b.append((v & 127) | 128); v >>= 7
    return bytes(reversed(b))


def write(notes, path, bpm=60.0, div=480):
    ev, t = [], 0.15
    tick = lambda s: int(round(s * bpm / 60.0 * div))
    cents, sung = [], []
    for p, d, w, k in notes:
        if p is None:
            t += d; continue
        if w is None: ly = '-'
        elif k == 0: ly = 'blessid' if w.lower().strip('.,;:?!') == 'blessed' else re.sub(r"[^A-Za-z']", '', w)
        else: ly = '+'
        m = HOME + p
        a, z = tick(t), max(tick(t) + 1, tick(t + d * 0.98))
        ev.append((a, 0, b'\xff\x05' + vlq(len(ly.encode())) + ly.encode()))
        ev.append((a, 1, bytes([0x90, int(round(m)), 90])))
        ev.append((z, 2, bytes([0x80, int(round(m)), 0])))
        cents.append(str(int(round((m - round(m)) * 100)))); sung.append(d)
        t += d
    body = b'\x00\xff\x51\x03' + struct.pack('>I', int(6e7 / bpm))[1:]
    c = ('ison1:' + ','.join(cents)).encode()
    body += b'\x00\xff\x7f' + vlq(len(b'\x7d' + c)) + b'\x7d' + c
    ev.sort(key=lambda x: (x[0], x[1])); last = 0
    for tk, _o, data in ev:
        body += vlq(tk - last) + data; last = tk
    body += vlq(240) + b'\xff\x2f\x00'
    open(path, 'wb').write(b'MThd' + struct.pack('>IHHH', 6, 0, 1, div) + b'MTrk' + struct.pack('>I', len(body)) + body)
    return t


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 2: sys.exit(__doc__)
    st, out = int(a[0]), a[1]
    double = '--double' in sys.argv
    rows = [l.rstrip('\n').split('|') for l in open(NOTEBOOK, encoding='utf-8') if l.strip()]
    verses = [r for r in rows if r and r[0].isdigit() and (st - 1) * 8 < int(r[0]) <= st * 8]
    lines = [re.sub(r'[.,;:?!]', '', h).strip() for r in verses for h in r[1:] if h.strip()]
    notes = build(lines, double)
    dur = write(notes, out)
    nn = sum(1 for x in notes if x[0] is not None)
    print('stanza %d, %s: %d lines, %d notes, %.1f s' % (st, 'twice the reading' if double else 'as he sings it', len(lines), nn, dur))
    for idx, ref in plan(len(lines), double):
        print('   ' + ' / '.join(lines[i] for i in idx) + '  ->  ' + ('Hallelujah' if ref == 'H' else 'Barekhmor'))


if __name__ == '__main__':
    main()
