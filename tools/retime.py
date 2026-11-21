"""Re-time a song from the recording it was taken from: every note the length the singer sings it, every pause
where he pauses. Written for the Byzantine "Blessed art Thou" and the *Ncense recording.

Run with the singer's Python (it needs librosa and numpy):
    ~/ison-singer/venv/bin/python -I tools/retime.py

What it does. The melody moves and the ison stands still, so the drone's own harmonics are taken out of the
spectrum first and what is left is scored for a singing voice at every pitch from 150 to 700 Hz. That gives a
pitch line and a loudness line every 11.6 ms. The song's 615 notes are then laid along that line by a Viterbi
pass through states "note 1, rest, note 2, rest, ..." where a note costs the distance from its written pitch
(octaves folded, because a tracker hears a voice an octave out now and then) and a rest costs the opposite: it
is free where nothing is singing and dear where something is. The result is one start and end per note, so the
pauses are not hunted for separately: they are whatever is left between the notes.

Writes retimed.json next to the recording and prints how well it did.
"""
import json, os, re, sys, numpy as np, librosa

NC = os.path.expanduser('~/ison-singer/ncense/')
APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
SR, HOP, NFFT = 22050, 256, 2048
MINREST = 0.10          # anything shorter is a consonant, not a pause

# ---- the recording: a pitch line and a loudness line for the melody alone
y, _ = librosa.load(NC + 'ncense.wav', sr=SR, mono=True)
S = np.abs(librosa.stft(y, n_fft=NFFT, hop_length=HOP))
freqs = librosa.fft_frequencies(sr=SR, n_fft=NFFT)
T = librosa.frames_to_time(np.arange(S.shape[1]), sr=SR, hop_length=HOP)
D = json.load(open(NC + 'drone.json'))
dt = np.array(D['t'], float); dm = np.array([np.nan if x is None else x for x in D['m']], float); ok = ~np.isnan(dm)
drone = 440 * 2 ** ((np.interp(T, dt[ok], dm[ok]) - 69) / 12)
bw = freqs[1]
for h in range(1, 13):
    f = drone * h
    for k in (-2, -1, 0, 1, 2):
        idx = np.round(f / bw).astype(int) + k
        m = (idx > 0) & (idx < len(freqs))
        S[idx[m], np.arange(S.shape[1])[m]] = 0
cands = 150 * 2 ** (np.arange(0, 12 * np.log2(700 / 150) * 5) / 60.)
W = np.array([1, .85, .7, .55, .4])
sal = np.zeros((len(cands), S.shape[1]), np.float32)
for i, f0 in enumerate(cands):
    a = 0
    for h, w in enumerate(W, 1):
        lo = int(round(f0 * h * .985 / bw)); hi = int(round(f0 * h * 1.015 / bw)) + 1
        if hi >= len(freqs): break
        a = a + w * S[lo:hi].max(axis=0)
    sal[i] = a
loud = sal.max(axis=0)
pitch = 69 + 12 * np.log2(cands[sal.argmax(axis=0)] / 440.0)
k = 3
loudS = np.convolve(loud, np.ones(k) / k, 'same')
lev = np.percentile(loudS, 75)
voiced = loudS > lev * 0.20
print('%d frames of %.1f ms, %.0f%% of them have a voice in them' % (len(T), HOP / SR * 1000, 100 * voiced.mean()))

# ---- the song's notes, straight out of the app
s = open(APP, encoding='utf-8').read()
d = re.search(r"\nconst EVLOGITARIA_BYZ=\s*\n?((?:\s*'(?:[^'\\]|\\.)*'\s*\+?\s*)+);", s)
toks = ''.join(p.replace("\\'", "'") for p in re.findall(r"'((?:[^'\\]|\\.)*)'", d.group(1))).split()
A = json.load(open(NC + 'align2.json'))['notes']
assert len(A) == len(toks)
ST = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
notes = []      # (index into toks, written midi or None for a rest)
for i, t in enumerate(toks):
    p = t.split(':')
    if p[0] == 'r': notes.append((i, None)); continue
    mm = re.match(r'([A-G])([#b]?)(-?\d)', p[0])
    midi = (int(mm.group(3)) + 1) * 12 + ST[mm.group(1)] + (1 if mm.group(2) == '#' else -1 if mm.group(2) == 'b' else 0)
    notes.append((i, midi))
sung = [(i, m) for i, m in notes if m is not None]
print('%d notes to place' % len(sung))

# the choir sits under A and drifts; take their own measured offset per note where there is one
tun = np.array([ (A[i].get('tun') or 0.0) for i, m in sung ], dtype=float)
want = np.array([ m for i, m in sung ], dtype=float) + tun

# ---- lay the notes along the line: note, rest, note, rest, ... each able to hold for as long as it likes
# A note is not scored by asking a tracker what pitch it hears (that tracker is wrong about a third of the time
# on a choir); it is scored by asking how much of the sound at that moment is sitting on the note as written.
N = len(sung)
NS = 2 * N + 1
BIG = 1e9
ADV = 0.12                       # a small price for moving on, so notes are not skipped through
cents = (np.log2(cands / 440.0) * 12 + 69)
row = np.clip(np.searchsorted(cents, want), 1, len(cents) - 1)
lo = cents[row - 1]; hi = cents[row]
wlo = (hi - want) / np.maximum(1e-9, hi - lo)
norm = np.maximum(loud, 1e-6)
cost_note = np.empty((len(T), N), np.float32)
for j in range(N):
    v = sal[row[j] - 1] * wlo[j] + sal[row[j]] * (1 - wlo[j])
    cost_note[:, j] = 1.0 - np.clip(v / norm, 0, 1)
cost_rest = np.clip(loudS / (lev * 0.5), 0, 2.0).astype(np.float32) + 0.05

prev = np.full(NS, BIG, np.float32); prev[0] = 0.0; prev[1] = 0.0
back = np.zeros((len(T), NS), np.uint8)       # 0 = stayed, 1 = came from the state before
for t in range(len(T)):
    stay = prev
    adv = np.empty(NS, np.float32); adv[0] = BIG; adv[1:] = prev[:-1]
    adv = adv + ADV
    take = adv < stay
    cur = np.where(take, adv, stay)
    e = np.empty(NS, np.float32)
    e[0::2] = cost_rest[t]
    e[1::2] = cost_note[t]
    prev = cur + e
    back[t] = take
# finish in the last note or the last rest, whichever is cheaper
st = NS - 1 if prev[NS - 1] <= prev[NS - 2] else NS - 2
path = np.empty(len(T), np.int32)
for t in range(len(T) - 1, -1, -1):
    path[t] = st
    if back[t, st]: st -= 1
spans = {}
for t, st in enumerate(path):
    if st not in spans: spans[st] = [t, t]
    else: spans[st][1] = t

out = []
for j in range(N):
    sp = spans.get(2 * j + 1)
    out.append(None if sp is None else (T[sp[0]], T[sp[1]] + HOP / SR))
missing = sum(1 for x in out if x is None)
print('%d notes placed, %d never got a frame' % (N - missing, missing))

# ---- how well did it do? the measured pitch inside each note against what is written
good = tot = 0
for j, sp in enumerate(out):
    if sp is None: continue
    m = (T >= sp[0] + (sp[1] - sp[0]) * .3) & (T <= sp[0] + (sp[1] - sp[0]) * .8) & voiced
    if m.sum() < 2: continue
    e = np.median(pitch[m]) - want[j]
    while e > 6: e -= 12
    while e < -6: e += 12
    tot += 1; good += abs(e) <= 0.5
print('CHECK: %d%% of notes have the right note sounding in them (the old timing gave 57%%)' % (100 * good / max(1, tot)))

got=[x for x in out if x]
first = got[0][0]; last = max(x[1] for x in got)
print('music from %.2f s to %.2f s = %.1f s' % (first, last, last - first))
rests = []
for j in range(N - 1):
    if out[j] and out[j + 1]:
        g = out[j + 1][0] - out[j][1]
        if g >= MINREST: rests.append((j, g))
print('%d pauses of %.2f s or more between notes, %.1f s of pause in all, median %.2f s'
      % (len(rests), MINREST, sum(g for _, g in rests), np.median([g for _, g in rests]) if rests else 0))
json.dump(dict(idx=[i for i, m in sung], span=[list(x) if x else None for x in out],
               first=first, last=last), open(NC + 'retimed.json', 'w'))
print('saved ' + NC + 'retimed.json')
