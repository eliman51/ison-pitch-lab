#!/usr/bin/env python3
"""A first layout of a Psalm 118 stanza on the Psalm 23 (Tone 3) melody, by the rules Eli settled on stanza 4.

    ~/ison-singer/venv/bin/python -I tools/lay.py <stanza number> [<stanza number> ...]   ->  ~/ison-singer/p23m/N.auto.s.txt

It reads the stanza's syllables from the hand score in ~/ison-singer/heart/N.txt (where every word is already cut
into sung syllables and every half line is marked), its punctuation from the notebook, and decides
  1. which melody shape carries which words: the shapes follow each other only as the singer joins them; a verse ends on
     a shape that closes (B, H or D) and the stanza on D; no shape carries more syllables than the singer's own lines of
     that shape, and a shape is not cut after a little word (the, of, and ...) when it can be helped; the climb F G D
     comes at least once, if possible on the stanza's high word;
  2. which syllable sits on which cell of the shape, from a short list of ways for each count, taking the way that puts
     the accents on the strong cells.
The result is a draft to read through and correct by hand (copy it to N.s.txt), not a finished score: tools/shapes.py and
tools/heart.py then check and sing it. Nothing of the words is kept in this file.
"""
import os, re, sys

HEART = os.path.expanduser('~/ison-singer/heart/%d.txt')
NOTEBOOK = os.path.expanduser('~/ison-singer/notebook/Psalm 118 notebook.txt')
OUT = os.path.expanduser('~/ison-singer/p23m/%d.auto.s.txt')
PLAN = os.path.expanduser('~/ison-singer/p23m/%d.plan.txt')
JOIN = {'A': 'B', 'B': 'AC', 'C': 'D', 'D': 'AEF', 'E': 'H', 'H': 'I', 'I': 'D', 'F': 'G', 'G': 'D'}
# the singer's own load of each shape, and how far a line may go either way. c and g are the first halves of C and G.
LOAD = {'A': (9, 5, 11), 'B': (5.5, 4, 8), 'C': (9, 6, 10), 'c': (4.5, 4, 5), 'D': (6, 4, 10), 'E': (7, 4, 8), 'H': (7, 5, 8), 'I': (6.5, 5, 8),
        'F': (5, 4, 7), 'G': (8, 6, 8), 'g': (4, 3, 5)}
REAL = {'c': 'C', 'g': 'G'}
LITTLE = set('the a an of and to in on at by for from with as is are was were be been am it its or nor but if than so that which who my our your their his her i you he she we they them me him us not shall will would may might'.split())
HIGH = {1: 'thanks', 2: 'blessed', 3: 'longed', 5: 'behold', 6: 'love', 7: 'name', 8: 'mercy', 9: 'good', 10: 'live', 12: 'forever', 13: 'sweet', 14: 'joy',
        15: 'saved', 16: 'lord', 17: 'shine', 18: 'home', 19: 'cry', 20: 'life', 21: 'peace', 22: 'overflow', 11: 'help', 4: 'enlarged'}

WAYS = {   # for each shape and number of syllables: the ways to give the cells out (cells of tools/shapes.py)
    'A': {4: ['c1 c2 c5+c6+c7 c8+c9'], 5: ['c1 c2 c3 c5+c6+c7 c8+c9', 'c1 c2 c3+c5+c6 c7 c8+c9'],
          6: ['c1 c2 c3 c5+c6 c7 c8+c9', 'c1 c2 c3 c4 c5+c6+c7 c8+c9', 'c1 c2 c3 c5 c7 c8+c9'],
          7: ['c1 c2 c3 c5 c6 c7 c8+c9', 'c1 c2 c3 c4 c5 c6+c7 c8+c9', 'c1 c2 c3 c5 c7 c8 c9', 'c1 c2 c3 c4 c5 c7 c8+c9'],
          8: ['c1 c2 c3 c4 c5 c6 c7 c8+c9', 'c1 c2 c3 c5 c6 c7 c8 c9', 'c1 c2 c3 c4 c5 c7 c8 c9'], 9: ['c1 c2 c3 c4 c5 c6 c7 c8 c9'],
          10: ['c1 c2 c3 c4 0:1 c5 c6 c7 c8 c9', 'c1 -4:1 c2 c3 c4 c5 c6 c7 c8 c9', 'c1 c2 c3 c4 c5 c6a c6b c7 c8 c9'],
          11: ['c1 c2 c3 c4 0:1 c5 c6a c6b c7 c8 c9', 'c1 c2 c3 c4 c5 c6 c7 c8a c8b c9a c9b', 'c1 -4:1 c2 c3 c4 0:1 c5 c6 c7 c8 c9']},
    'B': {3: ['c1 c2+c3 c4+c5'], 4: ['c1 c2 c3+c4 c5', 'c1 c2+c3 c4 c5'], 5: ['c1 c2 c3 c4 c5'], 6: ['c0 c1 c2 c3 c4 c5', 'c1 c2a c2b c3 c4 c5'],
          7: ['c0 c1 c2a c2b c3 c4 c5', 'c0 c1 c2 c3ab c3cd c4 c5', 'c0 c1 c2 c3 c4ab c4cd c5'], 8: ['c0 c1 c2a c2b c3ab c3cd c4 c5', 'c0 c1 c2a c2b c3 c4ab c4cd c5']},
    'c': {3: ['c1 c2 c3+c4'], 4: ['c1 c2 c3 c4'], 5: ['c1 c2a c2b c3 c4']},
    'C': {6: ['c1 c2 c3 c4 c5 c8+c9'], 7: ['c1 c2 c3 c4 c5 c6 c8+c9', 'c1 c2 c3 c4 c5 c7 c8+c9'], 8: ['c1 c2 c3 c4 c5 c6 c7 c8+c9', 'c1 c2 c3 c4 c5 c6 c8 c9'],
          9: ['c1 c2 c3 c4 c5 c6 c7 c8 c9'], 10: ['c1 c2a c2b c3 c4 c5 c6 c7 c8 c9', 'c1 c2 c3 c4a c4b c5 c6 c7 c8 c9']},
    'E': {4: ['c1 c2 c3+c4 c5+c6+c7'], 5: ['c1 c2 c3+c4 c5 c6+c7', 'c1 c2 c3 c4 c5+c6+c7'], 6: ['c1 c2 c3 c4 c5 c6+c7', 'c1 c2 c3+c4 c5 c6 c7'], 7: ['c1 c2 c3 c4 c5 c6 c7'],
          8: ['c1 c2 c3 c4 q c5 c6 c7', 'c1 c2 c3 q c4 c5 c6 c7']},
    'H': {4: ['c1 c2 c3+c4 c6+c7'], 5: ['c1 c2 c3 c4 c6+c7', 'c1 c2 c3+c4 c6 c7'], 6: ['c1 c2 c3 c4 c6 c7', 'c1 c2 c3 c4 c5 c6+c7'], 7: ['c1 c2 c3 c4 c5 c6 c7'],
          8: ['c1 c2 c3a c3b c4 c5 c6 c7', 'c1 c2a c2b c3 c4 c5 c6 c7']},
    'I': {4: ['c1 c2 c3+c4 c6+c7'], 5: ['c1 c2 c3 c4 c6+c7', 'c1a c1b c2 c3+c4 c6+c7'], 6: ['c1 c2 c3 c4 c5 c6+c7', 'c1a c1b c2 c3+c4 c5 c6+c7'],
          7: ['c1 c2 c3 c4 c5 c6 c7', 'c1a c1b c2 c3 c4 c5 c6+c7'], 8: ['c1a c1b c2 c3 c4 c5 c6 c7']},
    'F': {4: ['c1 c2 c3 c4+c5', 'c1 c2 c3+c4 c5'], 5: ['c1 c2 c3 c4 c5'], 6: ['Fs c1 c2 c3+c4 c5+c6 c8 c9', 'c1 c2 c3 c4 c5a c5b'], 7: ['Fs c1 c2 c3+c4 c5 c6 c8 c9', 'Fs c1 c2 c3 c4 c5+c6 c8 c9']},
    'g': {3: ['c1 c2 c3+c4'], 4: ['c1 c2 c3 c4'], 5: ['c1 c2 c3a c3bc c4']},
    'G': {6: ['c1 c2 c3 c4 c5+c6 c7+c8', 'c1 c2 c3 c4 c5 c6+c7+c8'], 7: ['c1 c2 c3 c4 c5 c6 c7+c8'], 8: ['c1 c2 c3 c4 c5 c6 c7 c8']},
}
STRONG = {'A': 'c2 c3 c5 c7 c8', 'B': 'c1 c2 c5', 'C': 'c2 c3 c5 c7 c9', 'c': 'c2 c3 c4', 'E': 'c2 c3 c4 c6', 'H': 'c2 c3 c4 c6', 'I': 'c1 c3 c4 c7', 'F': 'c2 c3 c5 c9', 'G': 'c2 c3 c4 c6 c7', 'g': 'c2 c3 c4'}


def read(n):
    """-> syllables [{s, word (index), k (place in word), nk, st (2 accent, 1 half, 0 none), hl (a half line ends after it), ve (a verse ends), pu (mark after the word)}]"""
    import cmudict
    cmu = cmudict.dict()
    body = '\n'.join(l.split('#')[0] for l in open(HEART % n, encoding='utf-8'))
    words, lines = [], 0
    for tok in body.split():
        if tok == '|':
            if words:
                words[-1]['hl'] = True
            continue
        if tok in (',', '/') or tok[0] in '~{':
            continue
        words.append({'syl': [p.split('/')[0] for p in re.split(r'-(?=[A-Za-z])', tok)], 'hl': False})
    hl = [i for i, w in enumerate(words) if w['hl']]
    for j, i in enumerate(hl):
        words[i]['ve'] = j % 2 == 1                     # every second half line ends a verse
    blocks = re.split(r'^=== (.+?) ===$', open(NOTEBOOK, encoding='utf-8').read(), flags=re.M)
    raw = blocks[2 * n].split(); norm = lambda w: re.sub(r"[^a-z']", '', w.lower().replace('’', "'")).strip("'")
    raw = [w for w in raw if norm(w)]
    assert len(raw) == len(words), (len(raw), len(words))
    syl = []
    for wi, (w, r) in enumerate(zip(words, raw)):
        word = norm(''.join(w['syl'])); m = re.search(r'[.,;:?!]+["”]?$', r)
        pr = [p for p in cmu.get(word, []) if sum(x[-1].isdigit() for x in p) == len(w['syl'])] or cmu.get(word, [])
        st = [x[-1] for x in pr[0] if x[-1].isdigit()] if pr else ['1'] * len(w['syl'])
        st = (st + ['0'] * len(w['syl']))[:len(w['syl'])]
        for k, s in enumerate(w['syl']):
            last = k == len(w['syl']) - 1
            syl.append({'s': s, 'word': wi, 'k': k, 'nk': len(w['syl']), 'w': word,
                        'st': 0 if (len(w['syl']) == 1 and word in LITTLE) else 2 if st[k] == '1' else 1 if st[k] == '2' else 0,
                        'hl': last and w['hl'], 've': last and w.get('ve', False), 'pu': (m.group(0)[0] if m else '') if last else ''})
    return syl


def plan(syl, n):
    """the cheapest row of shapes over the syllables -> [(shape, first syllable, one past the last)]"""
    N = len(syl); INF = 1e9
    end_word = [s['k'] == s['nk'] - 1 for s in syl]
    pins, mustcut = {}, set()                        # ~/ison-singer/p23m/pins.txt:  7: name=F /because law#2=D   (word=shape, /word = a shape starts there)
    pf = os.path.expanduser('~/ison-singer/p23m/pins.txt')
    for l in (open(pf, encoding='utf-8') if os.path.exists(pf) else []):
        if l.split(':')[0].strip() == str(n):
            for tok in l.split(':', 1)[1].split():
                m = re.fullmatch(r"(/?)([a-z']+)(?:#(\d+))?(?:=([A-I]))?", tok)
                if not m:
                    sys.exit('pins.txt: cannot read "%s"' % tok)
                occ = [i for i, s_ in enumerate(syl) if s_['w'] == m.group(2) and s_['k'] == 0]
                if len(occ) < int(m.group(3) or 1):
                    sys.exit('pins.txt, stanza %d: no "%s"' % (n, tok))
                i = occ[int(m.group(3) or 1) - 1]
                if m.group(1):
                    mustcut.add(i)
                if m.group(4):
                    pins[i] = m.group(4)
    hi = HIGH.get(n); hiset = {i for i, s in enumerate(syl) if hi and s['w'] == hi}
    first_hi = min(hiset) if hiset else None
    hiset = {i for i in hiset if syl[i]['word'] == syl[first_hi]['word']} if hiset else set()

    def load(t, k):
        nat, lo, hi_ = LOAD[t]
        if k < lo or k > hi_:
            return INF
        return (1.5 * (k - nat) ** 2 if k > nat else 0.8 * (nat - k) ** 2) + (1.0 if t in 'cg' else 0) + 2.5      # 2.5: every shape costs time

    def cut(q, t):                                       # what it costs to end shape t after syllable q-1
        s = syl[q - 1]
        if q == N:
            return 0 if t == 'D' else INF
        if not end_word[q - 1]:                          # only the climb may stop inside a word, on its accent, the word ending on the height
            return 1.0 if (t == 'F' and s['st'] == 2 and s['nk'] - s['k'] - 1 <= 2) else INF
        if s['ve']:
            return 0 if REAL.get(t, t) in 'BHD' else INF
        c = 0.0 if (s['hl'] and s['pu']) else 0.3 if s['hl'] else 0.8 if s['pu'] else 4.0
        if s['w'] in LITTLE and not s['pu']:
            c += 6
        if q in mustcut:
            c -= 50
        if s['pu'] in '.;?!' and s['pu'] and REAL.get(t, t) not in 'BHD':
            c += 3
        return c

    def inside(p, q):                                    # marks swallowed by one shape
        c = 0.0
        for i in range(p, q - 1):
            if syl[i]['ve']:
                return INF
            if syl[i]['pu']:
                c += 15 if syl[i]['pu'] in '.;?!' else 5 if syl[i]['hl'] else 2.5
            elif syl[i]['hl']:
                c += 5
            if i + 1 in mustcut:
                return INF
        return c
    best = {(0, '', 0, 0): (0.0, None)}                 # (place, last shape, a climb so far, climbs in a row) -> (cost, where from)
    order = sorted
    frontier = [(0, '', 0, 0)]
    for p in range(N):
        for key in [k for k in list(best) if k[0] == p]:
            cost0 = best[key][0]; _, last, hasF, run = key
            nexts = ['A'] if not last else list(JOIN[REAL.get(last, last)])
            for t0 in nexts:
                for t in ([t0, t0.lower()] if t0 in 'CG' else [t0]):
                    if last and last in 'cg' and t0 != 'D':
                        continue
                    nat, lo, hi_ = LOAD[t]
                    for k in range(lo, hi_ + 1):
                        q = p + k
                        if q > N:
                            break
                        c = load(t, k)
                        if c >= INF:
                            continue
                        c2 = cut(q, t)
                        if c2 >= INF:
                            continue
                        c3 = inside(p, q)
                        if c3 >= INF:
                            continue
                        c += c2 + c3
                        if any(pins.get(i) not in (None, REAL.get(t, t)) for i in range(p, q)):
                            continue
                        if p and not end_word[p - 1] and t0 != 'G':
                            continue
                        nrun = run
                        if t == 'F':
                            c += 4 * run * run + (0, 3, 8, 14)[min(hasF, 3)]; nrun = run + 1
                            if hiset and p <= min(hiset) < q + (8 if True else 0):   # the high word on the climb or the height after it
                                c -= 3
                        elif t0 in 'AE':
                            nrun = 0
                        nk = (q, t, min(3, hasF + (t == 'F')), nrun)
                        if c + cost0 < best.get(nk, (INF,))[0]:
                            best[nk] = (c + cost0, key)
    ends = [(v[0], k) for k, v in best.items() if k[0] == N and k[1] == 'D' and k[2] >= 1]
    if not ends:
        sys.exit('no layout found for stanza %d' % n)
    cost, key = min(ends); row = []
    while best[key][1] is not None:
        prev = best[key][1]; row.append((key[1], prev[0], key[0])); key = prev
    return row[::-1], cost


def fromplan(syl, n):
    """a layout written by hand, ~/ison-singer/p23m/N.plan.txt: one line a shape, its letter and the words it carries
    (  A  Blessed are the blameless in the way  ). The words are only checked against the stanza, in order.
    testimonies:3 = only the first 3 syllables of that word here, the rest opens the next line (written there as -nies or
    left out); c and g are the first halves of C and G; ~2 at the end is a breath; after = the cells may be written out,
    one for each syllable (  B  on Your wonders = c1 c2 c3+c4 c5  )."""
    pf = PLAN % n
    if not os.path.exists(pf):
        return None
    row, p, N = [], 0, len(syl)
    for ln, l in enumerate(open(pf, encoding='utf-8'), 1):
        l = l.split('#')[0]
        if not l.strip():
            continue
        l, _, over = l.partition('=')
        toks = l.split(); t = toks[0]; p0 = p; trail = ''
        if t not in LOAD:
            sys.exit('%s line %d: no shape "%s"' % (pf, ln, t))
        if p < N and syl[p]['k'] > 0:                     # the rest of a word begun on the line before
            p += syl[p]['nk'] - syl[p]['k']
        for tok in toks[1:]:
            if tok[0] == '~':
                trail = tok; continue
            if tok[0] == '-':
                continue
            w, _, k = tok.partition(':'); norm = re.sub(r"[^a-z']", '', w.lower())
            if p >= N or syl[p]['w'] != norm or syl[p]['k'] != 0:
                sys.exit('%s line %d: "%s" does not come next (the stanza has "%s", syllable %d)' % (pf, ln, tok, syl[min(p, N - 1)]['w'], syl[min(p, N - 1)]['k'] + 1))
            p += int(k) if k else syl[p]['nk']
        if p0 == p:
            sys.exit('%s line %d: no words' % (pf, ln))
        row.append((t, p0, p, over.split() or None, trail))
    if p != N:
        sys.exit('%s: the plan stops at "%s", syllable %d of %d' % (pf, syl[min(p, N - 1)]['w'], p, N))
    return row


def cells(t, S, spill):
    """the syllables S of one shape on its cells -> (shape name for shapes.py, [cell spec for each syllable])"""
    n = len(S)
    if t == 'D':
        # as the singer lays his closes: the last syllable on the closing figure, the one before it on the leap (2 1), the
        # accent before that on the step up (1 0, his pause after it), what lies between on the low note, the rest recited
        last3 = S[-3:] if n >= 5 else []
        dact = len(last3) == 3 and last3[0]['st'] == 2 and last3[1]['word'] == last3[0]['word'] == last3[2]['word']
        j3 = n - 3 if dact else n - 2
        tail = ['c3', 'c4ab', 'c4cd'] if dact else ['c3', 'c4']
        cand = [i for i in range(j3 - 1, max(-1, j3 - 5), -1) if S[i]['st'] == 2]
        c1 = cand[0] if cand else max(0, j3 - 2)
        if c1 == j3 - 1 and j3 >= 2:                       # nothing would fall on the low note: step back one
            c1 = j3 - 2
        mid = list(range(c1 + 1, j3)); spec = {}
        if len(mid) >= 2 and S[c1 + 1]['word'] == S[c1]['word']:
            spec[c1] = 'c1a'; spec[c1 + 1] = 'c1b'; mid = mid[1:]
        else:
            spec[c1] = 'c1'
        for k, i in enumerate(mid):
            spec[i] = 'c2' if len(mid) == 1 else ('c2*.6' if k == len(mid) - 1 else '-1:.9')
        if not mid and j3 - c1 == 1:
            pass
        for k, i in enumerate(range(j3, n)):
            spec[i] = tail[k]
        return 'D', [spec.get(i, 'r' if S[i]['st'] == 2 else 'q') for i in range(n)]
    bestv = None
    for way in WAYS[t][n]:
        parts = way.split(); name = REAL.get(t, t)
        if parts[0] == 'Fs':
            name = 'Fs'; parts = parts[1:]
        strong = set((STRONG[t] if name != 'Fs' else 'c2 c4 c6 c9').split()); v = 0.0
        for s, c in zip(S, parts):
            base = set(re.findall(r'c\d', c)); big = c.count('+') >= 1 or c in ('c8+c9',)
            if s['st'] == 2:
                v += 1 if base & strong else -0.5
            if s['st'] == 0 and c.count('+') >= 1 and s is not S[-1]:
                v -= 0.6
            if s['st'] == 0 and s is S[-1] and c.count('+') >= 2:
                v -= 0.7
        if t == 'F':
            v += 2 * (S[-1]['st'] == 2)
        if bestv is None or v > bestv[0]:
            bestv = (v, name, parts)
    return bestv[1], bestv[2]


def write(n):
    syl = read(n); hand = fromplan(syl, n)
    if hand:
        row, cost, extra = [r[:3] for r in hand], 0, {i: r[3:] for i, r in enumerate(hand)}
        for a, b in zip(row, row[1:]):
            if REAL.get(b[0], b[0]) not in JOIN[REAL.get(a[0], a[0])]:
                print('  stanza %d: %s then %s is a join the singer never makes' % (n, a[0], b[0]))
    else:
        (row, cost), extra = plan(syl, n), {}
    out = ['# Psalm 118, stanza %d on the Psalm 23 (Tone 3) melody.  ' % n + ' '.join(REAL.get(t, t) for t, _, _ in row), '#! singer-pauses', '{t1.06}']
    for i, (t, p, q) in enumerate(row):
        S = syl[p:q]; over, trail = extra.get(i, (None, ''))
        if (q - p) not in WAYS.get(t, {q - p: 1}) and not over:
            sys.exit('stanza %d, line %d: no way written for %s with %d syllables' % (n, i + 1, t, q - p))
        name, cs = cells(t, S, 0); toks = []; word = []
        if over:
            if over[0] == 'Fs':
                name = 'Fs'; over = over[1:]
            if len(over) != len(S):
                sys.exit('stanza %d, line %d: %d cells written for %d syllables' % (n, i + 1, len(over), len(S)))
            cs = over
        if i == len(row) - 1:
            name = 'D!'
        for j, (s, c) in enumerate(zip(S, cs)):
            word.append(s['s'] + '/' + c)
            if s['k'] == s['nk'] - 1 or j == len(S) - 1:
                w = '-'.join(word)
                if s['k'] != s['nk'] - 1:
                    w += '-'                              # the word runs on into the next shape
                if S[j - len(word) + 1]['k'] > 0:
                    w = '-' + w
                toks.append(w); word = []
        out.append('%-3s%s%s%s' % (name, ' '.join(toks), ' ' + trail if trail else '', ' |' if S[-1]['hl'] else ''))
    open(OUT % n, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    form = ' '.join('%s%d' % (REAL.get(t, t), q - p) for t, p, q in row)
    print('stanza %d: %d syllables on %d shapes (%.1f each), cost %.0f: %s' % (n, len(syl), len(row), len(syl) / len(row), cost, form))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for a in sys.argv[1:]:
        write(int(a))
