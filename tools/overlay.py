#!/usr/bin/env python3
"""New words on the Psalm 23 (Tone 3) singer's melody, the melody left exactly as he sings it.

    ~/ison-singer/venv/bin/python -I tools/overlay.py <stanza number> [<out name>]     ->  ~/ison-singer/p23m/<out name>.txt (+ .form)

Eli's rule (18 November 2026): the melody must be the same in every note, every length and every pause; the only thing
that changes is which word is sung on which notes. So nothing here stretches, shortens, drops or adds a note. The whole
performance is read from the deep scan (tools/scan.py -> ~/ison-singer/p23/scan/scan.json): 338 notes, his 26 shapes in
his order, about two minutes. A stanza's syllables (from ~/ison-singer/heart/N.txt, as tools/lay.py reads them) are then
laid on those notes, each syllable on one or more notes in a row, by the cheapest fit:
  - a verse ends where one of his closing shapes ends (B, D or H); a syllable never runs over one of his breaths or from
    one shape into the next
  - his breaths fall at our punctuation and line ends where they can, inside a word only when they must (he does that too)
  - no syllable quicker than about a third of a second; the long figures go to accented syllables and to the last
    syllable before a breath (as his do: shep-HERD, e-VIL), not to little words in the middle of a line
  - our syllables begin where his do when they can
The result is a score for tools/heart.py (run it with --unit 0.25 --home 51 --scale p23, no tempo mark).
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lay

SCAN = os.path.expanduser('~/ison-singer/p23/scan/scan.json')
OUT = os.path.expanduser('~/ison-singer/p23m/%s.txt')
SHAPES = [('A', 8), ('B', 6), ('A', 9), ('B', 5), ('C', 9), ('D', 7), ('E', 7), ('H', 7), ('I', 6), ('D', 6), ('F', 5), ('G', 8), ('D', 5),
          ('A', 9), ('B', 5), ('A', 9), ('B', 5), ('C', 8), ('D', 7), ('E', 7), ('H', 7), ('I', 7), ('D', 5), ('F', 5), ('G', 8), ('D', 5)]   # his syllables in each
LOUD = {'A': 'mf', 'B': 'mp', 'C': 'mf', 'D': 'mp', 'E': 'mf', 'H': 'p', 'I': 'mf', 'F': 'mf', 'G': 'mf'}
BREATH = 0.25                                            # a silence this long is a breath; shorter ones are his consonants
INF = 1e9


def melody(skip=()):
    """-> notes [{step, d (seconds, with a short silence after it held through), gap (silence after, seconds), slot, shape, sl (last note of his syllable), sh (last note of a shape)}]"""
    S = [s for L in json.load(open(SCAN))['lines'] for s in L['syl']]
    assert len(S) == sum(k for _, k in SHAPES), len(S)
    notes, si = [], 0
    for hi, (name, k) in enumerate(SHAPES):
        for j in range(k):
            s = S[si]; ns = [[a, b] for a, b, _ in s['notes']]
            while len(ns) > 1 and (ns[-1][1] < 0.13 or (ns[-1][1] <= 0.2 and abs(ns[-1][0] - ns[-2][0]) >= 4)):     # a blip as the syllable lets go: not a note
                ns[-2][1] += ns[-1][1]; ns.pop()
            m = []
            for a, b in ns:
                if m and m[-1][0] == a:
                    m[-1][1] += b
                else:
                    m.append([a, b])
            nxt = S[si + 1]['t0'] if si + 1 < len(S) else None
            gap = max(0.0, nxt - (s['t0'] + s['dur'])) if nxt is not None else 0.0
            for q, (a, b) in enumerate(m):
                last = q == len(m) - 1
                notes.append({'step': a, 'd': b, 'gap': gap if last else 0.0, 'slot': si, 'shape': hi, 'name': name, 'sl': last, 'sh': last and j == k - 1})
            si += 1
    return [x for x in notes if x['shape'] not in skip]


def cost(syl, N, i, a, b):
    """what it costs to sing syllable i on notes a..b of the row of notes N (INF = not allowed)"""
    s, last, m, n = syl[i], N[b], len(N), len(syl)
    for j in range(a, b):
        if N[j]['gap'] >= BREATH or N[j]['sh']:
            return INF
    D = sum(N[j]['d'] + (N[j]['gap'] if N[j]['gap'] < BREATH else 0.0) for j in range(a, b + 1)) - (last['gap'] if last['gap'] < BREATH else 0.0); k = b - a + 1
    R = last['gap'] if last['gap'] >= BREATH else 0.0
    endw = s['k'] == s['nk'] - 1; fin = (R > 0 and endw) or i == n - 1; st = s['st']; little = s['w'] in lay.LITTLE and s['nk'] == 1
    c = 0.0
    if s['ve'] and not (last['sh'] and last['name'] in 'BDH'):
        return INF
    c += 30 if D < 0.18 else 8 if D < 0.25 else (4 if st == 2 else 2.5) if D < 0.32 else 0
    lim = 2.3 if fin else 1.3 if st == 2 else 1.1 if st == 1 else 0.75 if little else 0.85
    if D > lim:
        c += 3 + 12 * (D - lim)
    if st == 0 and not fin and D > 0.65:
        c += 1.5 * (D - 0.65)
    if k >= 3 and st == 0 and not fin:
        c += 2.5 if little else 1.5
    if st == 2:
        c -= 1.0 * min(D, 1.0)
    if not last['sl']:
        c += 0.6
    if st == 0 and not fin and N[b]['slot'] != N[a]['slot']:
        c += 4                                           # a weak syllable stretched over two of his
    if st == 2 and D < 0.4:
        c += 1.5
    if st == 2 and fin and D < 0.45:
        c += 4
    if R:
        if not endw:
            c += 2.5
        elif s['pu']:
            c -= 3 if s['pu'] in '.;?!' else 2
        elif s['hl']:
            c -= 1.5
        else:
            c += 3 if little else 1.0
    elif endw and not last['sh']:
        if s['pu']:
            c += 6 if s['pu'] in '.;?!' else 2.5
        elif s['hl']:
            c += 4
    if last['sh']:
        if not endw:
            return INF
        if s['ve']:
            c -= 2
        elif s['pu']:
            c -= 1.5
        elif s['hl']:
            c -= 1
        else:
            c += 9 if little else 2.5
    if 0.12 <= last['gap'] < BREATH and not endw:
        c += 0.3
    return c


def inner(syl, N, i0):
    """the syllables from i0 on, laid on the whole of one row of notes N: {how many syllables: (cost, cuts)}"""
    m, n = len(N), len(syl); K = min(m, n - i0)
    best = [[INF] * (m + 1) for _ in range(K + 1)]; back = [[0] * (m + 1) for _ in range(K + 1)]; best[0][0] = 0.0
    for k in range(K):
        for a in range(k, m):
            if best[k][a] >= INF:
                continue
            for b in range(a, min(a + 10, m)):
                c = cost(syl, N, i0 + k, a, b)
                if c < INF and best[k][a] + c < best[k + 1][b + 1]:
                    best[k + 1][b + 1] = best[k][a] + c; back[k + 1][b + 1] = a
                if N[b]['gap'] >= BREATH or N[b]['sh']:
                    break
    out = {}
    for k in range(1, K + 1):
        if best[k][m] < INF:
            cuts, b = [], m
            for q in range(k, 0, -1):
                a = back[q][b]; cuts.append((a, b - 1)); b = a
            out[k] = (best[k][m], cuts[::-1])
    return out


def fit(syl, N):
    """the whole song in his order: every one of his notes, the stanza's syllables laid over them"""
    r = inner_whole(syl, N)
    return r


def inner_whole(syl, N):
    n, m = len(syl), len(N)
    best = [[INF] * (m + 1) for _ in range(n + 1)]; back = [[0] * (m + 1) for _ in range(n + 1)]; best[0][0] = 0.0
    for i in range(n):
        for a in range(i, m - (n - i) + 1):
            if best[i][a] >= INF:
                continue
            for b in range(a, min(a + 10, m - (n - i) + 1)):
                c = cost(syl, N, i, a, b)
                if c < INF and (i == n - 1) == (b == m - 1) and best[i][a] + c < best[i + 1][b + 1]:
                    best[i + 1][b + 1] = best[i][a] + c; back[i + 1][b + 1] = a
                if N[b]['gap'] >= BREATH or N[b]['sh']:
                    break
    if best[n][m] >= INF:
        sys.exit('no fit found')
    cuts, b = [], m
    for i in range(n, 0, -1):
        a = back[i][b]; cuts.append((a, b - 1)); b = a
    return cuts[::-1], best[n][m]


JOIN = {'': 'A', 'A': 'B', 'B': 'AC', 'C': 'D', 'D': 'AEF', 'E': 'H', 'H': 'I', 'I': 'D', 'F': 'G', 'G': 'D'}


def freefit(syl, ALL, high=None, pins={}):
    """his shapes, each one whole and exactly as he sings it, in the best order for these words (only joins he makes;
    begins on A, ends on D): -> (the row of notes, cuts, cost)"""
    n = len(syl); inst = {}
    for x in ALL:
        inst.setdefault(x['shape'], []).append(x)
    inst = list(inst.values())
    best = {(0, ''): (0.0, None)}
    for i in range(n):
        for last in [''] + list('ABCDEFGHI'):
            if (i, last) not in best:
                continue
            c0 = best[(i, last)][0]
            for I in inst:
                t = I[0]['name']
                if t not in JOIN[last]:
                    continue
                for k, (c, cuts) in inner(syl, I, i).items():
                    if i + k == n and t != 'D':
                        continue
                    if any(pins.get(j, t) != t for j in range(i, i + k)):
                        continue
                    c += 0.5
                    if high is not None and t in 'FG' and i <= high < i + k:
                        c -= 4
                    key = (i + k, t)
                    if c0 + c < best.get(key, (INF,))[0]:
                        best[key] = (c0 + c, ((i, last), I, cuts))
    if (n, 'D') not in best:
        sys.exit('no fit found')
    key, chain = (n, 'D'), []
    while best[key][1] is not None:
        prev, I, cuts = best[key][1]; chain.append((I, cuts)); key = prev
    N, C = [], []
    for hi, (I, cuts) in enumerate(chain[::-1]):
        off = len(N); N += [dict(x, shape=hi) for x in I]; C += [(a + off, b + off) for a, b in cuts]
    return N, C, best[(n, 'D')][0]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--skip=')]
    skip = set()
    for a in sys.argv[1:]:
        if a.startswith('--skip='):                      # --skip=20-23 : leave those of his 26 shapes out (counted from 1)
            for part in a[7:].split(','):
                lo, _, hi = part.partition('-'); skip |= set(range(int(lo) - 1, int(hi or lo)))
    n = int(args[0]); name = args[1] if len(args) > 1 else '%dx' % n
    args = [a for a in args if a != '--free' and not a.startswith('--pin=')]
    pinspec = [a[6:] for a in sys.argv if a.startswith('--pin=')]      # --pin=mercy=H,ran=F,way#2=I : that word is sung on that shape
    n = int(args[0]); name = args[1] if len(args) > 1 else '%dx' % n
    syl, N = lay.read(n), melody(skip)
    if '--free' in sys.argv:
        hw = lay.HIGH.get(n); hi = next((i for i, s_ in enumerate(syl) if s_['w'] == hw and s_['st'] == 2), None)
        pins = {}
        for tok in ','.join(pinspec).split(','):
            if tok:
                w, t = tok.split('='); w, _, occ = w.partition('#')
                where = [i for i, s_ in enumerate(syl) if s_['w'] == w.lower() and s_['k'] == 0]
                pins[where[int(occ or 1) - 1]] = t
        N, cuts, total = freefit(syl, N, hi, pins)
    else:
        cuts, total = fit(syl, N)
    fm = lambda x: ('%.2f' % x).rstrip('0').rstrip('.')
    out = ['# Psalm 118, stanza %d on the Psalm 23 (Tone 3) melody exactly as the singer sings it: his notes, lengths and pauses; only the words are new.' % n,
           '# Written by tools/overlay.py. One unit = a quarter second.']
    line, word, shape, form, rows, cur = [], [], -1, [], [], []
    for i, (s, (a, b)) in enumerate(zip(syl, cuts)):
        hi = N[a]['shape']
        if hi != shape:
            if line:
                out.append(' '.join(line)); line = []
            shape = hi; line.append('{%s}' % LOUD[N[a]['name']]); form.append([N[a]['name'], 0])
        form[-1][1] += 1
        last = N[b]; R = last['gap'] if last['gap'] >= 0.12 else 0.0
        spec = []
        for j in range(a, b + 1):
            d = N[j]['d'] + (N[j]['gap'] if (j < b and N[j]['gap'] < BREATH) else 0.0)
            spec.append('%d:%s' % (N[j]['step'], fm(d / 0.25)))
        endw = s['k'] == s['nk'] - 1
        tok = s['s'] + '/' + '_'.join(spec)
        D = sum(N[j]['d'] for j in range(a, b + 1))
        cur.append('%s%s %.2f%s' % ('' if s['k'] == 0 else '-', s['s'], D, '~%.2f' % R if R >= BREATH else ''))
        if not endw and R:
            tok += '~' + fm(R / 0.25)
        word.append(tok)
        if endw:
            line.append('-'.join(word)); word = []
            if R:
                line.append('~' + fm(R / 0.25))
            if s['hl']:
                line.append('|')
        if last['sh'] or i == len(syl) - 1:
            rows.append('  %s  %s' % (N[a]['name'], '  '.join(cur))); cur = []
    if word:
        line.append('-'.join(word))
    out.append(' '.join(line))
    open(OUT % name, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    open(OUT % name + '.form', 'w').write(' '.join('%s%d' % (a, b) for a, b in form) + '\n')
    print('\n'.join(rows))
    d = sorted(sum(N[j]['d'] for j in range(a, b + 1)) for a, b in cuts)
    print(''.join(f[0] for f in form), '%.1f s' % (sum(x['d'] + x['gap'] for x in N)))
    print('stanza %d: %d syllables on his %d notes, cost %.0f; quicker than 0.3 s: %d, longer than 1 s: %d; median %.2f s' % (n, len(syl), len(N), total, sum(x < 0.3 for x in d), sum(x > 1 for x in d), d[len(d) // 2]))


if __name__ == '__main__':
    main()
