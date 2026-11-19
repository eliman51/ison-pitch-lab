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
OPEN, CLOSE, CLOSELONG, END, SCOOP = 'AEF', 'BDH', 'BDCH', 'D', False     # phrases that never end a verse; that end one best; whose last figure is long; that may end a stanza


def use(path):
    """another recording's melody (--mel tools/p23t4.mel.json): its scan, its phrases and how he joins them"""
    global SCAN, OUT, SHAPES, LOUD, JOIN, OPEN, CLOSE, CLOSELONG, END, SCOOP
    M = json.load(open(path))
    SCAN = os.path.expanduser(M['scan']); OUT = os.path.expanduser(M['out']); os.makedirs(os.path.dirname(OUT), exist_ok=True)
    SHAPES = [tuple(x) for x in M['shapes']]; LOUD = M['loud']; JOIN = M['join']
    OPEN, CLOSE, CLOSELONG, END, SCOOP = M['open'], M['close'], M['closelong'], M['end'], M.get('scoop', False)
    global MUST
    MUST = M.get('must', '')
    for t, _ in SHAPES:
        lay.LOAD.setdefault(t, (0, 0, 99))
SHAPECOST = 3.0                                          # every phrase costs time: no more of them than the words need
DARK = set('affliction afflict sinners enemies perished persecute persecuted arrogant transgressors transgressed lawlessness humbled ashamed snares ensnared wander tears trouble evil unrighteous unrighteousness hate hated kill fainted reproach contempt accursed despondency curdled frost evildoers wrong falsely lost astray shamed insult vanity greediness blame listlessness sin slander foolishly'.split())
STARTERS = set('of in on at by for from with to and but or nor that which who whom when where because according as than like so if before upon unto into toward more rather'.split())
HAND = False                                             # a layout written by hand decides its own phrase ends
HANG = set('the a an of and to in on at by for from with as is are was were be been am or nor but if than so that which who my our your their his i he she we they not shall will would may might have has had do did does'.split())
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
            while SCOOP and len(ns) > 1 and ns[0][1] < 0.2 and ns[1][0] - ns[0][0] >= 2:      # a low creak as the syllable starts: not a note
                ns[1][1] += ns[0][1]; ns.pop(0)
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
    hang = s['w'] in HANG and s['nk'] == 1 or s['w'] in STARTERS     # a word that leans on the next one: nothing ends on it
    c = 0.0
    if s['ve'] and not last['sh']:
        return INF
    if 'cut' in s and s['cut'] != bool(last['sh']):
        return INF
    nxt = syl[i + 1]['w'] if i + 1 < n else ''
    starter = nxt in STARTERS                          # the next word opens a new group of words: a good place to break
    c += 30 if D < 0.18 else (16 if st == 2 else 9) if D < 0.25 else (7 if st == 2 else 2.5) if D < 0.32 else 0
    close = last['sh'] and last['name'] in CLOSELONG      # only his closing figures are long: a word before a small breath is not
    lim = ((1.2 if little else 2.3) if close or i == n - 1 else 1.0 if little else 1.3) if fin else 1.3 if st == 2 else 1.1 if st == 1 else 0.75 if little else 0.85
    if D > lim:
        c += 3 + 12 * (D - lim)
    if D > 1.5 and not fin:
        c += 8
    if st == 0 and not fin and D > 0.65:
        c += 1.5 * (D - 0.65)
    if k >= 3 and st == 0 and not fin:
        c += 2.5 if little else 1.5
    if st == 2:
        c -= 0.6 * min(D, 0.8)
        if D > 0.9 and not fin:
            c += 2.0 * (D - 0.9)
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
            c += 12 if hang else 0.4 if starter else 3.0
    elif endw and not last['sh']:
        if s['pu']:
            c += 6 if s['pu'] in '.;?!' else 2.5
        elif s['hl']:
            c += 4
    if last['sh']:
        if not endw:
            return INF
        if s['ve']:
            if last['name'] in OPEN:
                return INF                                # a verse never ends on a phrase of his that opens
            c += -2 if last['name'] in CLOSE else 8      # a verse closes best on his closing phrases
        elif s['pu']:
            c -= 1.5
        elif s['hl']:
            c -= 1
        else:
            if hang and not HAND:
                return INF                                # a phrase of his never ends on a word that leans on the next
            c += 1.0 if starter else 4.5
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
            out[k] = (best[k][m] + (7 if k < 3 else 4 if k < 4 else 0), cuts[::-1])
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
    best = {(0, '', 0): (0.0, None)}
    for i in range(n):
      for hasF in range(16):                              # the climbs so far (0 to 3) and whether the last block was one (+4)
        for last in [''] + list('ABCDEFGHI'):
            if (i, last, hasF) not in best:
                continue
            c0 = best[(i, last, hasF)][0]
            for I in inst:
                t = I[0]['name']
                if t not in JOIN[last]:
                    continue
                for k, (c, cuts) in inner(syl, I, i).items():
                    if i + k == n and t != 'D':
                        continue
                    if any(pins.get(j, t) != t for j in range(i, i + k)):
                        continue
                    c += SHAPECOST
                    if high is not None and t in 'FG' and i <= high < i + k:
                        c -= 4
                    nF, run, hadE = hasF % 4, (hasF // 4) % 2, hasF // 8
                    if t == 'F':
                        c += (0, 0, 5, 12)[nF] + 6 * run      # the climb is the high point: seldom, and not twice in a row
                        nh = min(3, nF + 1) + 4
                    else:
                        nh = nF + (0 if t in 'AE' else 4 * run)
                    if t in 'EH' and any(syl[j]['w'] in DARK for j in range(i, i + k)):
                        c -= 3                                # his dark phrase on a dark line
                    if t == 'E' and not hadE:
                        c -= 6                                # the descent once in a stanza, where it can be afforded
                    nh += 8 * (1 if t == 'E' else hadE)
                    key = (i + k, t, nh)
                    if c0 + c < best.get(key, (INF,))[0]:
                        best[key] = (c0 + c, ((i, last, hasF), I, cuts))
    ends = [(v[0], k_) for k_, v in best.items() if k_[0] == n and k_[1] == 'D' and k_[2] % 4 >= 1]
    if not ends:
        sys.exit('no fit found')
    key, chain = min(ends)[1], []; endkey = key
    while best[key][1] is not None:
        prev, I, cuts = best[key][1]; chain.append((I, cuts)); key = prev
    N, C = [], []
    for hi, (I, cuts) in enumerate(chain[::-1]):
        off = len(N); N += [dict(x, shape=hi) for x in I]; C += [(a + off, b + off) for a, b in cuts]
    return N, C, best[endkey][0]


EXACT = False                                            # --exact: one of our syllables to each of his (Eli, 19 November 2026)


AUTO = False                                             # --auto: the tool chooses the phrases too
JOINCOST = 10.0                                          # with --auto; 40 without, as trial F was made
SPLITCOST = 16.0
MUST = ''                                                # phrases a stanza uses at least once


def cost2(syl, N, i, a, b):
    """the cost of syllable i on his notes a..b when the tool chooses the phrases itself. Eli's order of weight: his own
    number of syllables first (JOINCOST), then whole words in a phrase, then where verses and sentences end, then accents."""
    s, last, n = syl[i], N[b], len(syl)
    D = sum(N[j]['d'] for j in range(a, b + 1)); R = last['gap'] if last['gap'] >= BREATH else 0.0
    endw = s['k'] == s['nk'] - 1; st = s['st']; little = s['w'] in lay.LITTLE and s['nk'] == 1
    hang = endw and (s['w'] in HANG and s['nk'] == 1 or s['w'] in STARTERS) and not s['pu']
    c = 0.0
    if last['sh']:
        if not endw:
            c += 200
        elif s['ve']:
            c += -8 if last['name'] in CLOSE else 6 if last['name'] in OPEN else -3
        elif s['hl']:
            c -= 4
        elif s['pu']:
            c -= 3
        else:
            c += 15 if hang else 6
    else:
        if endw and s['ve']:
            c += 5 if R else 12
        elif endw and (s['hl'] or s['pu']) and not R:
            c += 2.5
        if R:
            c += 7 if not endw else -2 if (s['hl'] or s['pu']) else 4 if hang else 0.5
    heavy = D >= 0.62
    if heavy:
        c += -1.5 if st == 2 else 0.0 if (st == 1 or (endw and (R or last['sh']))) else 2.5 if little else 1.5
    if D < 0.25 and st == 2:
        c += 2.0
    if D < 0.2:
        c += 5.0
    if D < 0.3 and (a == 0 or not N[a - 1]['sl'] or not last['sl']):
        c += 8.0                                         # a piece cut from one of his syllables must not be a scrap
    return c


def exact(syl, I, i0, k):
    """k syllables on one of his phrases, his own syllables kept: the same count as his is one to one. One fewer: two
    neighbouring syllables of his are joined (never across a breath). One more (only when the tool chooses, --auto, or the
    plan says so): one of his syllables that has two or more notes carries two of ours. As few of either as can be."""
    m = len(I); S = sum(1 for x in I if x['sl'])
    if k > S and not AUTO:
        return None
    best = {(0, 0): (0.0, [])}                             # (syllables laid, notes used)
    for q in range(k):
        for a in range(q, m):
            if (q, a) not in best:
                continue
            c0, cuts = best[(q, a)]
            if a and not I[a - 1]['sl'] and sum(x['d'] for x in I[cuts[-1][0]:a]) < 0.2:
                continue
            joins = 0
            for b in range(a, m):
                if b > a and I[b - 1]['gap'] >= BREATH:
                    break
                if b > a and I[b - 1]['sl']:
                    joins += 1
                if not I[b]['sl'] and not AUTO:
                    continue
                D = sum(x['d'] for x in I[a:b + 1])
                c = c0 + (JOINCOST if AUTO else 40.0) * joins + (0 if I[b]['sl'] else SPLITCOST + (20 if D < 0.2 else 0))
                c += cost2(syl, I, i0 + q, a, b) if AUTO else min(cost(syl, I, i0 + q, a, b), 500.0)
                if (q + 1, b + 1) not in best or c < best[(q + 1, b + 1)][0]:
                    best[(q + 1, b + 1)] = (c, cuts + [(a, b)])
    r = best.get((k, m))
    return (r[0] + (0.0 if AUTO else 1000.0 * abs(S - k)), r[1]) if r else None


def exactfit(syl, ALL):
    """the phrases chosen by the tool, every one whole and carrying his own number of syllables (one or two of his joined
    only where nothing else fits): the cheapest row of phrases that he joins this way, from his opening to his close"""
    inst = {}
    for x in ALL:
        inst.setdefault(x['shape'], []).append(x)
    inst = list(inst.values()); n = len(syl)
    kinds = {}
    for I in inst:
        kinds.setdefault(I[0]['name'], []).append(I)
    memo = {}
    def lay1(t, i0, k):
        if (t, i0, k) not in memo:
            best = None
            for I in kinds[t]:
                r = exact(syl, I, i0, k)
                if r and (best is None or r[0] < best[0]):
                    best = (r[0], I, r[1])
            memo[(t, i0, k)] = best
        return memo[(t, i0, k)]
    best = {(0, '', ''): (0.0, None, None)}
    for i in range(n):
        for (j, prev, used) in [k_ for k_ in best if k_[0] == i]:
            c0 = best[(j, prev, used)][0]
            for t in JOIN[prev]:
                S = sorted({sum(1 for x in I if x['sl']) for I in kinds[t]})
                for k in range(S[0] - 2, S[-1] + 2):
                    if k < 2 or i + k > n:
                        continue
                    r = lay1(t, i, k)
                    if not r:
                        continue
                    c = c0 + r[0] + SHAPECOST
                    u2 = ''.join(sorted(set(used) | ({t} & set(MUST)))); key = (i + k, t, u2)
                    if key not in best or c < best[key][0]:
                        best[key] = (c, (i, prev, used), r)
    full = ''.join(sorted(MUST))
    ends = [(best[(n, t, full)][0], t) for t in END if (n, t, full) in best]
    if not ends:
        sys.exit('no row of his phrases carries these %d syllables' % n)
    total, t = min(ends); key = (n, t, full); row = []
    while best[key][1] is not None:
        row.append(best[key][2]); key = best[key][1]
    N, C = [], []
    for hi, (_, I, cuts) in enumerate(row[::-1]):
        off = len(N); N += [dict(x, shape=hi) for x in I]; C += [(a + off, b + off) for a, b in cuts]
    return N, C, total


def planfit(syl, ALL, plan):
    """a layout written by hand (~/ison-singer/p23m/N.oplan.txt, as tools/lay.py reads plans: a shape letter and the words it
    carries on each line): each phrase is his, whole; of his two to four singings of that phrase the one that fits best"""
    inst = {}
    for x in ALL:
        inst.setdefault(x['shape'], []).append(x)
    N, C, total, prev = [], [], 0.0, ''
    for hi, (t, p0, p1, over, trail) in enumerate(plan):
        if t not in JOIN[prev]:
            print('   ! %s then %s is a join he never makes' % (prev, t))
        prev = t; bestc = None
        for I in inst.values():
            if I[0]['name'] != t:
                continue
            r = exact(syl, I, p0, p1 - p0) if EXACT else None
            if r and p1 - p0 == sum(1 for x in I if x['sl']):
                r = (r[0] - 1e6, r[1])                      # his own syllable count comes before any other fit
            r = r or inner(syl, I, p0).get(p1 - p0)
            if r and (bestc is None or r[0] < bestc[0]):
                bestc = (r[0], I, r[1])
        if bestc is None:
            sys.exit('line %d of the plan: %d syllables do not fit on %s' % (hi + 1, p1 - p0, t))
        off = len(N); N += [dict(x, shape=hi) for x in bestc[1]]; C += [(a + off, b + off) for a, b in bestc[2]]; total += bestc[0]
    return N, C, total


def main():
    global EXACT, HAND, AUTO
    args = [a for a in sys.argv[1:] if not a.startswith('--skip=') and not a.startswith('--mel=') and a not in ('--exact', '--auto')]
    skip = set()
    for a in sys.argv[1:]:
        if a.startswith('--skip='):                      # --skip=20-23 : leave those of his 26 shapes out (counted from 1)
            for part in a[7:].split(','):
                lo, _, hi = part.partition('-'); skip |= set(range(int(lo) - 1, int(hi or lo)))
    n = int(args[0]); name = args[1] if len(args) > 1 else '%dx' % n
    args = [a for a in args if a not in ('--free', '--plan', '--exact', '--auto') and not a.startswith('--pin=') and not a.startswith('--mel=')]
    pinspec = [a[6:] for a in sys.argv if a.startswith('--pin=')]      # --pin=mercy=H,ran=F,way#2=I : that word is sung on that shape
    n = int(args[0]); name = args[1] if len(args) > 1 else '%dx' % n
    for a in sys.argv:
        if a.startswith('--mel='):
            use(a[6:])
    AUTO = '--auto' in sys.argv
    syl, N = lay.read(n), melody(skip)
    pf = os.path.join(os.path.dirname(OUT), '%d.oplan.txt' % n)
    if '--plan' in sys.argv:
        HAND = True; EXACT = '--exact' in sys.argv
        import shutil, tempfile
        tmp = lay.PLAN % n; had = os.path.exists(tmp)
        if had:
            shutil.move(tmp, tmp + '.keep')
        shutil.copy(pf, tmp)
        try:
            plan = lay.fromplan(syl, n)
        finally:
            os.remove(tmp)
            if had:
                shutil.move(tmp + '.keep', tmp)
        N, cuts, total = planfit(syl, N, plan)
    elif '--auto' in sys.argv:
        EXACT = AUTO = True
        N, cuts, total = exactfit(syl, N)
    elif '--free' in sys.argv:
        hw = lay.HIGH.get(n); hi = next((i for i, s_ in enumerate(syl) if s_['w'] == hw and s_['st'] == 2), None)
        pins = {}
        df = os.path.expanduser('~/ison-singer/p23m/overlay.pins.txt')      # N: word=F  word#2=H  /word (a phrase begins there)  +word (no phrase begins there)
        for l in (open(df, encoding='utf-8') if os.path.exists(df) else []):
            if l.split(':')[0].strip() == str(n):
                pinspec += l.split(':', 1)[1].split('#!')[0].split()
        for tok in ','.join(pinspec).split(','):
            if tok:
                mark = tok[0] if tok[0] in '/+' else ''; tok = tok.lstrip('/+')
                w, _, t = tok.partition('='); w, _, occ = w.partition('#')
                where = [i for i, s_ in enumerate(syl) if s_['w'] == w.lower() and s_['k'] == 0]
                if len(where) < int(occ or 1):
                    sys.exit('stanza %d: no "%s"' % (n, tok))
                i0 = where[int(occ or 1) - 1]
                if t:
                    pins[i0] = t
                if mark and i0:
                    syl[i0 - 1]['cut'] = mark == '/'
        N, cuts, total = freefit(syl, N, hi, pins)
    else:
        cuts, total = fit(syl, N)
    fm = lambda x: ('%.2f' % x).rstrip('0').rstrip('.')
    out = ['# Psalm 118, stanza %d on the melody of %s exactly as the singer sings it: his notes, lengths and pauses; only the words are new.' % (n, os.path.basename(os.path.dirname(os.path.dirname(SCAN)))),
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
        inword = s['k'] != s['nk'] - 1
        if inword and R < BREATH:
            R = 0.0
        spec = []
        for j in range(a, b + 1):
            d = N[j]['d'] + (N[j]['gap'] if ((j < b or (inword and N[j]['gap'] < BREATH)) and N[j]['gap'] < BREATH) else 0.0)
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
    for i, (s, (a, b)) in enumerate(zip(syl, cuts)):
        D = sum(N[j]['d'] for j in range(a, b + 1)); last = N[b]; R = last['gap'] if last['gap'] >= BREATH else 0
        endw = s['k'] == s['nk'] - 1; little = s['w'] in lay.LITTLE and s['nk'] == 1; fin = (R and endw) or i == len(syl) - 1; f = []
        if D < 0.3: f.append('quick %.2f' % D)
        if s['st'] == 2 and D < 0.38: f.append('accent only %.2f' % D)
        if s['st'] == 0 and D > (0.95 if not fin else 2.2): f.append('weak syllable held %.2f' % D)
        if D > 1.5 and not (last['sh'] or i == len(syl) - 1): f.append('held %.2f' % D)
        if R and not endw: f.append('breath inside the word')
        if R and endw and little and not s['pu']: f.append('breath after a little word')
        if last['sh'] and endw and little and not (s['pu'] or s['hl']): f.append('phrase ends on a little word')
        if last['sh'] and endw and not (s['pu'] or s['hl']) and i + 1 < len(syl) and syl[i + 1]['w'] not in STARTERS: f.append('BREAK before "%s"' % syl[i + 1]['w'])
        if (R or last['sh']) and endw and s['w'] in STARTERS and not s['pu']: f.append('ENDS on "%s"' % s['w'])
        if endw and s['pu'] and s['pu'] in '.;?!' and not (R or last['sh']): f.append('no breath at "%s"' % s['pu'])
        if f: print('   ? %s (%s, %s): %s' % (s['s'], s['w'], N[a]['name'], '; '.join(f)))
    d = sorted(sum(N[j]['d'] for j in range(a, b + 1)) for a, b in cuts)
    if '--plan' not in sys.argv:                           # the layout as a plan, to correct by hand and run again with --plan
        with open(os.path.join(os.path.dirname(OUT), '%d.oplan.auto.txt' % n), 'w', encoding='utf-8') as f_:
            k = 0
            for t, cnt in form:
                ws = []
                for s_ in syl[k:k + cnt]:
                    if s_['k'] == 0:
                        ws.append(s_['w'])
                k += cnt; f_.write('%s  %s\n' % (t, ' '.join(ws)))
    print(''.join(f[0] for f in form), '%.1f s' % (sum(x['d'] + x['gap'] for x in N)))
    print('stanza %d: %d syllables on his %d notes, cost %.0f; quicker than 0.3 s: %d, longer than 1 s: %d; median %.2f s' % (n, len(syl), len(N), total, sum(x < 0.3 for x in d), sum(x > 1 for x in d), d[len(d) // 2]))


if __name__ == '__main__':
    main()
