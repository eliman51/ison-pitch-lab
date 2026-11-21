"""Where the *Ncense singers actually stop for breath.

The melody moves and the ison stands still, so the lead is found by harmonic salience with the drone's own
harmonics taken out first. Frames with no melody left are a pause. Everything is measured, nothing is assumed
from the score; the score alignment is only used at the end to say which note each pause falls before.

    ~/ison-singer/venv/bin/python -I pauses.py            -> pauses.json + a printed table
"""
import json, os, sys, numpy as np, librosa

NC = os.path.expanduser('~/ison-singer/ncense/')
SR = 22050
HOP = 128                      # 5.8 ms
NFFT = 2048

y, _ = librosa.load(NC + 'ncense.wav', sr=SR, mono=True)
S = np.abs(librosa.stft(y, n_fft=NFFT, hop_length=HOP, window='hann'))
freqs = librosa.fft_frequencies(sr=SR, n_fft=NFFT)
T = librosa.frames_to_time(np.arange(S.shape[1]), sr=SR, hop_length=HOP)
print('%.1f s, %d frames' % (len(y) / SR, S.shape[1]))

# --- the drone, measured every 20 ms when the recording was first taken apart
D = json.load(open(NC + 'drone.json'))
dt = np.array(D['t'], dtype=float); dm = np.array(D['m'], dtype=float)
drone = 440.0 * 2 ** ((np.interp(T, dt, dm) - 69) / 12.0)
print('drone %.0f to %.0f Hz' % (np.nanmin(drone[drone > 0]), np.nanmax(drone)))

# --- take the drone's harmonics out of the spectrum
Sm = S.copy()
binw = freqs[1]
for h in range(1, 13):
    f = drone * h
    for k in (-2, -1, 0, 1, 2):
        idx = np.round(f / binw).astype(int) + k
        ok = (idx > 0) & (idx < len(freqs))
        Sm[idx[ok], np.arange(S.shape[1])[ok]] = 0.0

# --- melody salience: the strongest harmonic stack left, 150 to 700 Hz
cands = 150 * 2 ** (np.arange(0, 12 * np.log2(700 / 150) * 5) / 60.0)   # 20 cents apart
W = np.array([1.0, 0.85, 0.7, 0.55, 0.4])
sal = np.zeros((len(cands), S.shape[1]), dtype=np.float32)
for ci, f0 in enumerate(cands):
    acc = 0
    for h, w in enumerate(W, start=1):
        lo = int(round(f0 * h * 0.985 / binw)); hi = int(round(f0 * h * 1.015 / binw)) + 1
        if hi >= len(freqs): break
        acc = acc + w * Sm[lo:hi].max(axis=0)
    sal[ci] = acc
mel = sal.max(axis=0)
melf = cands[sal.argmax(axis=0)]

# --- smooth a little, then call a frame empty when the lead is far below its own normal level
k = int(round(0.03 * SR / HOP)) | 1
mels = np.convolve(mel, np.ones(k) / k, mode='same')
loud = np.percentile(mels, 75)
thr = loud * 0.20
on = mels > thr
# bridge single-frame dropouts
mn = int(round(0.05 * SR / HOP))
i = 0
while i < len(on):
    if not on[i]:
        j = i
        while j < len(on) and not on[j]: j += 1
        if j - i < mn: on[i:j] = True
        i = j
    else: i += 1

runs = []
i = 0
while i < len(on):
    if not on[i]:
        j = i
        while j < len(on) and not on[j]: j += 1
        runs.append((T[i], T[min(j, len(T) - 1)]))
        i = j
    else: i += 1
MIN = 0.12
gaps = [(a, b) for a, b in runs if b - a >= MIN and a > 1.0 and b < len(y) / SR - 0.5]
print('threshold %.3f of a typical %.3f; %d gaps of %.2f s or more' % (thr, loud, len(gaps), MIN))

# --- which note each gap falls before, and the words either side
A = json.load(open(NC + 'align2.json'))
N = [n for n in A['notes'] if 't0' in n]
def words_before(t, n=5):
    out, cur = [], ''
    for x in N:
        w = (x.get('w') or '')
        if not w: continue
        if w.endswith('-'): cur += w[:-1]
        else:
            cur += w
            if x['t1'] <= t + 0.08: out.append(cur)
            cur = ''
    return ' '.join(out[-n:])
def note_after(t):
    for i, x in enumerate(N):
        if x['t0'] >= t - 0.02: return i
    return None

rows = []
prev = N[0]['t0']
for a, b in gaps:
    i = note_after(b)
    rows.append(dict(t=round(a, 3), d=round(b - a, 3), note=i, sang=round(a - prev, 1), after=words_before(a)))
    prev = b
for r in rows:
    print('  %6.2f s  pause %.2f s  (sang %4.1f s)  note %-4s after: ...%s' % (r['t'], r['d'], r['sang'], r['note'], r['after']))
json.dump(rows, open(os.path.dirname(os.path.abspath(__file__)) + '/pauses.json', 'w'), indent=0)
print('%d pauses, median %.2f s, longest run of singing %.0f s' %
      (len(rows), np.median([r['d'] for r in rows]), max(r['sang'] for r in rows)))
