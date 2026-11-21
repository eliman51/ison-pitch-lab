"""Put a recording's own pauses into a song's melody in index.html (written for the Byzantine Blessed art Thou).

pauses.py measured where the *Ncense melody actually stops. This maps each one to its note (the app's melody and
the aligned recording are the same 618 tokens, checked note for note) and writes the melody again with a rest
there. Where the choir sings on for longer than one breath (they stagger their breathing, so the sound never
stops), a breath is added at the best punctuation inside that stretch.

    python3 apply.py  ->  byz_br2.txt  and a printed table
"""
import json, re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.expanduser('~/ison-pitch-lab/index.html')
BPM = 211.0
BEAT = 60.0 / BPM
MERGE = 0.35        # two gaps closer than this are one breath
MIN_REST = 0.45     # short enough to stay musical, long enough to breathe
MAX_REST = 1.10
LONG_RUN = 7.5      # a stretch of singing longer than this gets a breath of its own
ADD_REST = 0.50

s = open(APP, encoding='utf-8').read()
d = re.search(r"\nconst EVLOGITARIA_BYZ=\s*\n?((?:\s*'(?:[^'\\]|\\.)*'\s*\+?\s*)+);", s)
toks = ''.join(p.replace("\\'", "'") for p in re.findall(r"'((?:[^'\\]|\\.)*)'", d.group(1))).split()
ev = []
for t in toks:
    p = t.split(':')
    ev.append(dict(nm=p[0], b=float(p[1]), w=':'.join(p[2:])))

A = json.load(open(os.path.expanduser('~/ison-singer/ncense/align2.json')))['notes']
assert len(A) == len(ev)

# which notes begin a word, and the whole word that ends on each note
starts, ends, cur, st = set(), {}, '', None
for i, e in enumerate(ev):
    if e['nm'] == 'r': continue
    w = e['w']
    if w:
        if st is None: st = i; starts.add(i)
        if w.endswith('-'): cur += w[:-1]
        else:
            cur += w; ends[i] = cur; cur = ''; st = None
if st is not None: starts.add(st)

P = json.load(open(HERE + '/pauses.json'))
# 1. merge the flickers into one breath each
M = []
for p in P:
    if M and p['t'] - (M[-1]['t'] + M[-1]['d']) < MERGE:
        M[-1]['d'] = p['t'] + p['d'] - M[-1]['t']
    else:
        M.append(dict(p))
last_t1 = max(n['t1'] for n in A if 't1' in n)
M = [m for m in M if m['t'] < last_t1 - 1.0]

# 2. each pause -> the note it comes before, snapped to the start of a word
def note_after(t):
    # the rests carry no time at all, so they are stepped over rather than treated as "later than everything"
    for i, n in enumerate(A):
        t0 = n.get('t0')
        if t0 is not None and t0 >= t - 0.02: return i
    return None
plan = {}     # note index -> rest in seconds
moved = 0
for m in M:
    i = note_after(m['t'])
    if i is None: continue
    if i not in starts:
        near = [j for j in range(max(0, i - 3), min(len(ev), i + 4)) if j in starts]
        if near:
            j = min(near, key=lambda x: abs(x - i))
            if j != i: moved += 1
            i = j
    plan[i] = max(plan.get(i, 0), min(MAX_REST, max(MIN_REST, m['d'])))
print('%d gaps measured -> %d breaths (%d snapped to the start of a word)' % (len(P), len(plan), moved))

# 3. anywhere they sing on past one breath, add one at the best punctuation
STRONG, WEAK = '.:;?!', ','
def runs_of(plan):
    out, t, start = [], 0.0, 0.0
    for i, e in enumerate(ev):
        if i in plan:
            out.append((start, t, i)); t += plan[i]; start = t
        t += e['b'] * BEAT
    out.append((start, t, len(ev)))
    return out
added = 0
while True:
    long = [r for r in runs_of(plan) if r[1] - r[0] > LONG_RUN]
    if not long: break
    a, b, upto = max(long, key=lambda r: r[1] - r[0])
    # candidate notes inside this run, by how good the break is and how near the middle
    t, best = 0.0, None
    for i, e in enumerate(ev):
        if i in plan: t += plan[i]
        t += e['b'] * BEAT
        if not (a + 2.0 < t < b - 2.0): continue
        nxt = i + 1
        if nxt not in starts or nxt in plan: continue
        w = ends.get(i)
        if not w: continue
        c = w.strip()[-1:]
        rank = 0 if c in STRONG else 1 if c in WEAK else 2
        score = (rank, abs(t - (a + b) / 2))
        if best is None or score < best[0]: best = (score, nxt)
    if best is None: break
    plan[best[1]] = ADD_REST; added += 1
print('%d more added where they sing through one breath' % added)

# 4. write the melody again
out, t, rows = [], 0.0, []
for i, e in enumerate(ev):
    if i in plan:
        out.append('r:%g' % round(plan[i] / BEAT, 2)); rows.append((t, plan[i], ends.get(i - 1, '') or '', i in set()))
        t += plan[i]
    out.append(e['nm'] + ':' + ('%g' % e['b']) + ((':' + e['w']) if e['w'] else ''))
    t += e['b'] * BEAT
open(HERE + '/byz_br2.txt', 'w').write(' '.join(out))
R = runs_of(plan)
sings = [r[1] - r[0] for r in R if r[1] - r[0] > 0.01]
print('%d breaths, %.0f s added, song %.0f s; singing runs: longest %.1f s, median %.1f s' %
      (len(plan), sum(plan.values()), t, max(sings), sorted(sings)[len(sings) // 2]))
# a readable table
tt = 0.0
for i, e in enumerate(ev):
    if i in plan:
        back = ' '.join([ends[j] for j in sorted(ends) if j < i][-6:])
        print('  %6.1f s  breath %.2f s  after: ...%s' % (tt, plan[i], back))
        tt += plan[i]
    tt += e['b'] * BEAT
