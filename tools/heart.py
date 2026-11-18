#!/usr/bin/env python3
"""A song written by hand, every syllable on its own notes: score -> notes file -> the singer -> the app's review set.

    ~/ison-singer/venv/bin/python -I tools/heart.py <score.txt> <stanza number> <out folder> [--sing] [--unit 0.2]
                                                    [--home 45] [--scale hijaz|p23] [--set r118h]

The score (kept outside this repository, it holds the words) is plain text. Words are written syllable by syllable,
each syllable with its notes after a slash, syllables of one word joined by a hyphen:

    Bless/0'-ed/2 are/3 the/3 blame/4'-less/3 in/3 the/3 way/3:2.5 ,  Who/3 walk/3' ...  Lord/4_5:.75_4:3_3:2 /

  notes      steps of the scale counted from the home note (0 home, 3 the fourth, -1 the step below home); several
             notes on one syllable are joined with _ (a slide or a drawn-out word)
  lengths    in units (one unit = one quick syllable): nothing = 1, ' = 1.5 (an accented syllable), " = 2,
             :x = x units. A ! after a note makes that syllable a little stronger.
  pauses     ,  a lift with no breath (0.75 unit)     /  a breath (1.75 units)     ~x  x units of silence
             or/1:1.8~1.2-di/-1:2   a lift inside a word: ~x straight after a syllable's notes
  marks      {p} {mp} {mf} {f} {ff} how loud from here on     {t1.2} everything 1.2 times slower from here on
             |  a new line of the words (only for reading the score)       # starts a comment

It checks that the words are exactly the stanza's words, that every word has as many syllables as the singer will
sing, prints every line with the accents the dictionary gives (so a strong syllable on a quick low note stands out),
and writes <out>/r118h-N.mid, .json (the app's practice-song record) and .gain.json (the loudness line). With --sing
it then sings it (tools/sing.py), shapes the loudness, and writes r118h-N.m4a for tools/pack118.py.
"""
import json, math, os, re, struct, subprocess, sys, wave

HIJAZ = [0, 1, 13 / 3, 5, 7, 8, 10]                      # the app's Hijaz, church tuning (semitones above home)
LEVEL = {'pp': -3.5, 'p': -2.2, 'mp': -1.0, 'mf': 0.0, 'f': 1.5, 'ff': 2.5}   # kept narrow: low lines are already softer by nature, and he listens in a loud shop
SAY = {'blessed': 'blessid', 'beloved': 'belovid'}       # the two-syllable church readings, as the app writes them
NOTEBOOK = os.path.expanduser('~/ison-singer/notebook/Psalm 118 notebook.txt')
HERE = os.path.dirname(os.path.abspath(__file__))


# the Psalm 23 (Tone 3) singer's own ladder, measured from the recording built into the app (tools/scan.py): a Kurd-type
# scale; step 0 is the note the song ends on, and his top note is a little sharp of the octave of his bottom note
P23 = {-4: -7.10, -3: -5.12, -2: -4.04, -1: -1.98, 0: 0.0, 1: 0.96, 2: 2.98, 3: 5.22}
SCALE = HIJAZ


def pitch(deg, home):
    if isinstance(SCALE, dict):
        if deg not in SCALE:
            sys.exit('Step %d is not in this scale' % deg)
        return home + SCALE[deg]
    return home + 12 * (deg // 7) + SCALE[deg % 7]


def parse(path, home, unit):
    """-> syllables [{s, ws, word, k, line, notes:[(deg, units)], t, acc, db}], pauses placed, times in seconds."""
    syl, t, tempo, db, line = [], 0.15, 1.0, 0.0, 0
    body = '\n'.join(l.split('#')[0] for l in open(path, encoding='utf-8'))
    for tok in body.split():
        if tok == '|':
            line += 1; continue
        if tok == ',':
            t += 0.75 * unit * tempo; continue
        if tok == '/':
            t += 1.75 * unit * tempo; continue
        if tok[0] == '~':
            t += float(tok[1:]) * unit * tempo; continue
        if tok[0] == '{':
            k = tok.strip('{}')
            if k in LEVEL:
                db = LEVEL[k]
            elif k[0] == 't':
                tempo = float(k[1:])
            else:
                sys.exit('Unknown mark ' + tok)
            continue
        parts = re.split(r'-(?=[A-Za-z])', tok)
        word = ''.join(p.split('/')[0] for p in parts)
        for k, p in enumerate(parts):
            if '/' not in p:
                sys.exit('No notes on "%s" in "%s"' % (p, tok))
            s, spec = p.split('/', 1); notes, acc = [], False
            spec, _, lift = spec.partition('~')            # or/1:1.8_0:.85~1.2 : a lift (silence) after this syllable, inside the word
            for q in spec.split('_'):
                m = re.fullmatch(r"(-?\d+)(?:(')|(\")|:(\d*\.?\d+))?(!)?", q)
                if not m:
                    sys.exit('Cannot read the notes "%s" in "%s"' % (q, tok))
                u = 1.5 if m.group(2) else 2.0 if m.group(3) else float(m.group(4)) if m.group(4) else 1.0
                acc = acc or bool(m.group(5)); notes.append((int(m.group(1)), u))
            ns = []
            for deg, u in notes:
                d = u * unit * tempo; ns.append({'t': t, 'd': d, 'm': pitch(deg, home), 'deg': deg, 'u': u}); t += d
            syl.append({'s': s, 'ws': k == 0, 'word': word, 'k': k, 'nk': len(parts), 'line': line, 'notes': ns, 'db': db + (1.6 if acc else 0.0)})
            if lift:
                t += float(lift) * unit * tempo
    return syl, t


def midi_file(notes, name):
    """Format 1, 480 ticks a quarter at 120 a minute (so 960 ticks a second), lyrics, and the app's exact tuning event."""
    tk = lambda s: int(round(s * 960)); enc = lambda s: list(s.encode())
    def vl(n):
        b = [n & 127]; n >>= 7
        while n:
            b.insert(0, (n & 127) | 128); n >>= 7
        return b
    meta = lambda ty, data: [255, ty] + vl(len(data)) + list(data)
    chunk = lambda cid, body: cid + struct.pack('>I', len(body)) + bytes(body)
    cents = [int(round((n['m'] - round(n['m'])) * 100)) for n in notes]
    t0 = [0] + meta(3, enc(name)) + [0] + meta(0x51, [0x07, 0xA1, 0x20]) + [0] + meta(0x58, [4, 2, 24, 8]) + [0] + meta(0x7F, [0x7D] + enc('ison1:' + ','.join(map(str, cents)))) + [0] + meta(0x2F, [])
    ev = []
    for i, n in enumerate(notes):
        a = tk(n['t']); b = max(a + 1, tk(n['t'] + n['d'])); p = int(round(n['m']))
        ev.append((a, 1, i, meta(5, enc(n['ly'])))); ev.append((a, 2, i, [0x90, p, 96])); ev.append((b, 0, i, [0x80, p, 0]))
    ev.sort(key=lambda e: e[:3]); body, last = [0] + meta(3, enc('Voice')), 0
    for e in ev:
        body += vl(e[0] - last) + e[3]; last = e[0]
    body += [0] + meta(0x2F, [])
    return b'MThd' + struct.pack('>IHHH', 6, 1, 2, 480) + chunk(b'MTrk', t0) + chunk(b'MTrk', body)


def stanza_text(n):
    blocks = re.split(r'^=== (.+?) ===$', open(NOTEBOOK, encoding='utf-8').read(), flags=re.M)
    return blocks[2 * n - 1], blocks[2 * n].strip()


def main():
    skip = {i + 1 for i, x in enumerate(sys.argv) if x in ('--unit', '--home', '--scale', '--set')}
    a = [x for i, x in enumerate(sys.argv) if i and i not in skip and not x.startswith('--')]
    if len(a) < 3:
        sys.exit(__doc__)
    score, n, out = a[0], int(a[1]), a[2]; os.makedirs(out, exist_ok=True)
    opt = lambda k, d: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    unit, home = opt('--unit', 0.2), int(opt('--home', 45))
    sopt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    global SCALE
    SCALE = {'hijaz': HIJAZ, 'p23': P23}[sopt('--scale', 'hijaz')]; SET = sopt('--set', 'r118h')
    syl, end = parse(score, home, unit)
    name, text = stanza_text(n)
    # 1. the words are the stanza's words
    norm = lambda w: re.sub(r"[^a-z']", '', w.lower().replace('’', "'")).strip("'")
    want = [norm(w) for w in text.split() if norm(w)]; got = [norm(s['word']) for s in syl if s['ws']]
    for i in range(max(len(want), len(got))):
        if i >= len(want) or i >= len(got) or want[i] != got[i]:
            sys.exit('WORDS: word %d is "%s" in the score but "%s" in the stanza' % (i + 1, got[i] if i < len(got) else '(nothing)', want[i] if i < len(want) else '(nothing)'))
    # 2. every word has as many syllables as the singer sings, and where the accents fall
    import importlib.util as iu, cmudict
    sp = iu.spec_from_file_location('sing', os.path.join(HERE, 'sing.py')); sing = iu.module_from_spec(sp); sp.loader.exec_module(sing)
    snd = sing.Sounds(os.path.join(os.path.expanduser('~/ison-singer'), 'voices', 'tiger', 'bank')); cmu = cmudict.dict(); bad = 0
    FN = set('the a an of and to in on at by for from with as is are was were be been am it its or nor but if than so do does did have has had that which who whom me he she we they them him us his her my our your their i you shall will would should may might can could this these those o'.split())
    words = []
    for s in syl:
        if s['ws']:
            words.append([])
        words[-1].append(s)
    for W in words:
        w = norm(W[0]['word']); lyr = SAY.get(w, W[0]['word']) if not (w in SAY and len(W) != 2) else W[0]['word']
        ph = snd.say(lyr, len(W)); nv = sum(p in snd.vowels for p in ph)
        if nv != len(W):
            print('SYLLABLES: "%s" is written in %d but is sung in %d (%s)' % (W[0]['word'], len(W), nv, ' '.join(ph))); bad += 1
        pr = [p for p in cmu.get(w, []) if sum(x[-1].isdigit() for x in p) == len(W)] or cmu.get(w, [])
        st = [x[-1] for x in pr[0] if x[-1].isdigit()] if pr else ['1'] * len(W)
        st = (st + ['0'] * len(W))[:len(W)]
        for s, c in zip(W, st):
            s['st'] = 0 if (len(W) == 1 and w in FN) else 2 if c == '1' else 1 if c == '2' else 0
            s['lyr'] = lyr
    if snd.unknown:
        print('NOT IN THE DICTIONARY (check how they sound):', sorted(set(snd.unknown)))
    # 3. the page to read: each line, each syllable with its steps and length; flags where an accent is quick and not raised
    lines, flags = {}, []
    for i, s in enumerate(syl):
        lines.setdefault(s['line'], []).append(s)
        u = sum(x['u'] for x in s['notes']); top = max(x['deg'] for x in s['notes'])
        prev = syl[i - 1]['notes'][-1]['deg'] if i and syl[i - 1]['line'] == s['line'] else None
        nxt = syl[i + 1]['notes'][0]['deg'] if i + 1 < len(syl) and syl[i + 1]['line'] == s['line'] else None
        if s['st'] == 2 and u < 1.25 and not ((prev is not None and top > prev) or (nxt is not None and top > nxt)):
            flags.append('line %d: accented "%s" (%s) is quick and not raised' % (s['line'] + 1, s['s'], s['word']))
        if s['st'] == 0 and u >= 2 and nxt is not None:
            flags.append('line %d: unaccented "%s" (%s) is long (%.2g units)' % (s['line'] + 1, s['s'], s['word'], u))
    for k in sorted(lines):
        L = lines[k]; t0 = L[0]['notes'][0]['t']; t1 = L[-1]['notes'][-1]['t'] + L[-1]['notes'][-1]['d']
        print('%2d  %4.1f-%4.1fs  ' % (k + 1, t0, t1) + ' '.join(('' if s['ws'] else '-') + s['s'] + ('*' if s['st'] == 2 else '') + '[' + '_'.join('%d%s' % (x['deg'], '' if x['u'] == 1 else ':%g' % x['u']) for x in s['notes']) + ']' for s in L))
    for f in flags:
        print('  look: ' + f)
    nsyl = len(syl); dur = end + 0.35
    print('%s: %d syllables, %d notes, %.1f seconds, %.1f syllables a second' % (name, nsyl, sum(len(s['notes']) for s in syl), dur, nsyl / dur))
    if bad:
        sys.exit('Fix the syllables first.')
    # 4. the files
    notes = []
    for s in syl:
        for j, x in enumerate(s['notes']):
            notes.append({'t': x['t'], 'd': x['d'], 'm': x['m'], 'ly': '-' if j else (s['lyr'] if s['ws'] else '+')})
    base = os.path.join(out, '%s-%d' % (SET, n))
    open(base + '.mid', 'wb').write(midi_file(notes, name))
    jn = [{'t0': round(x['t'], 3), 't1': round(x['t'] + x['d'], 3), 'm': round(x['m'], 3)} for x in notes]
    ct, k = [], 0
    for i in range(int(math.ceil(dur / 0.02))):
        t = i * 0.02
        while k < len(notes) and t >= notes[k]['t'] + notes[k]['d']:
            k += 1
        ct.append([round(t, 3), round(notes[k]['m'], 2) if k < len(notes) and t >= notes[k]['t'] else None])
    sx = sum(math.cos(2 * math.pi * (x['m'] - round(x['m']))) for x in notes); sy = sum(math.sin(2 * math.pi * (x['m'] - round(x['m']))) for x in notes)
    words_j = [{'t0': round(s['notes'][0]['t'], 3), 't1': round(s['notes'][-1]['t'] + s['notes'][-1]['d'], 3), 's': s['s'], 'ws': s['ws'], 'line': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[s['line'] % 26]} for s in syl]
    json.dump({'n': n, 'text': text, 'dur': round(dur, 3), 'notes': jn, 'contour': ct, 'words': words_j, 'off': math.atan2(sy, sx) / (2 * math.pi) if (sx or sy) else 0},
              open(base + '.json', 'w', encoding='utf-8'), ensure_ascii=False)
    gain = [[round(s['notes'][0]['t'], 3), round(s['notes'][-1]['t'] + s['notes'][-1]['d'], 3), s['db']] for s in syl]
    json.dump(gain, open(base + '.gain.json', 'w'))
    print('Wrote ' + base + '.mid and .json')
    if '--sing' not in sys.argv:
        return
    # 5. the singer, then the loudness line (the voice itself has no loud and soft: it is shaped afterwards, gently)
    raw = base + '.raw.wav'
    r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'sing.py'), base + '.mid', '-o', raw], capture_output=True, text=True, cwd='/')
    if r.returncode:
        sys.exit(r.stderr[-800:])
    print([l for l in r.stdout.split('\n') if l.startswith('Sung') or l.startswith('Before')])
    import numpy as np
    w = wave.open(raw); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32) / 32768; w.close()
    g = np.zeros(len(x), dtype=np.float32); cur = gain[0][2]; pos = 0
    for t0, t1, db in gain:                                # each syllable's level from a little before it (its consonants) to its end; silences keep the level before
        a_ = max(0, int((t0 - 0.06) * sr)); g[pos:a_] = cur; cur = db; pos = a_
    g[pos:] = cur
    k = int(0.09 * sr); g = np.convolve(np.pad(g, (k, k), mode='edge'), np.ones(2 * k + 1, dtype=np.float32) / (2 * k + 1), mode='valid')[:len(x)]
    y = x * 10 ** (g / 20); pk = float(np.abs(y).max()) or 1.0; y *= 0.89 / pk
    w = wave.open(base + '.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((y * 32767).astype('<i2').tobytes()); w.close()
    os.remove(raw)
    m4 = base + '.m4a'
    for extra in ('.raw.m4a',):
        if os.path.exists(base + extra):
            os.remove(base + extra)
    subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', '96000', base + '.wav', m4], check=True, capture_output=True)
    print('Sung: ' + m4)


if __name__ == '__main__':
    main()
