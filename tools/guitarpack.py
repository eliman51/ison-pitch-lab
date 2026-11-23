#!/usr/bin/env python3
"""Packs the guitar notes the Guitar lab plays into one small file for each guitar, and prints the table that goes
into index.html (GT_BANKS). Run with the singer's Python (it has soundfile and numpy):

    ~/ison-singer/venv/bin/python -I tools/guitarpack.py nylon <folder with the FreePats samples> <out folder>
    ~/ison-singer/venv/bin/python -I tools/guitarpack.py steel <folder with the FreePats samples> <out folder>

nylon: FreePats "Spanish classical guitar" (CC0), https://freepats.zenvoid.org/Guitar/acoustic-guitar.html
steel: FreePats "FSS Steel-String Acoustic Guitar" (GPL 3 or later with the FreePats exception; samples by Gary Campion,
       FlameStudios), https://freepats.zenvoid.org/Guitar/steel-acoustic-guitar.html , the loud layer (HV_*.wav)
Each note is cut to start at its pluck, kept to at most 4.2 seconds, set to the same loudness at the pluck as the
others, and its tuning is measured so the app can play it exactly in tune. Then: ffmpeg -i guitar-<name>.wav -c:a aac
-b:a 96k -ac 1 guitar-<name>.m4a
"""
import soundfile as sf, numpy as np, os, sys, json
SETS = {'nylon': ([40,43,45,48,50,52,55,57,59,62,64,67,69,72,74,77,79,81,83], lambda m: 'C C# D D# E F F# G G# A A# B'.split()[m % 12] + str(m // 12 - 1) + '.flac'),
        'steel': ([40,43,45,48,50,52,55,58,61,64,66,68,71,74,76,79,82], lambda m: 'HV_%d.wav' % m)}
name, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
WANT, fn = SETS[name]; SR = 44100; GAP = 0.25; MAXLEN = 4.2
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
table = []
for m in WANT:
    x, sr = sf.read(os.path.join(src, fn(m))); assert sr == SR
    if x.ndim > 1: x = x.mean(1)
    pk = np.abs(x).max(); on = int(np.argmax(np.abs(x) > 0.015 * pk)); x = x[max(0, on - int(0.002 * SR)):][:int(MAXLEN * SR)].copy()
    last = len(x) - 1 - int(np.argmax(np.abs(x)[::-1] > 0.0015 * pk)); x = x[:min(len(x), last + int(0.05 * SR))]
    f = int(0.25 * SR) if len(x) >= int(MAXLEN * SR) - 2 else int(0.04 * SR)
    x[-f:] *= np.linspace(1, 0, f) ** 2; x[:int(0.001 * SR)] *= np.linspace(0, 1, int(0.001 * SR))
    seg = x[int(0.12 * SR):int(min(0.9, len(x) / SR - 0.05) * SR)][:int(0.7 * SR)]; seg = seg * np.hanning(len(seg))
    ac = np.fft.irfft(np.abs(np.fft.rfft(seg, 1 << 17)) ** 2)
    def peak(tau0, w):
        a = int(tau0 * (1 - w)); k = a + int(np.argmax(ac[a:int(tau0 * (1 + w)) + 2])); y0, y1, y2 = ac[k - 1], ac[k], ac[k + 1]; return k + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    tau = peak(SR / hz(m), 0.04); tau = peak(tau * 4, 0.01) / 4
    table.append({'m': m, 'c': round(float(1200 * np.log2(SR / tau / hz(m))), 1), 'r': np.sqrt((x[:int(0.4 * SR)] ** 2).mean()), 'x': x})
tgt = np.median([t['r'] for t in table])
for t in table: t['x'] = t['x'] * (tgt / t['r'])
pk = max(np.abs(t['x']).max() for t in table); y = [np.zeros(int(0.3 * SR))]; pos = len(y[0]); T = []
for t in table:
    x = t['x'] * (0.92 / pk); T.append([t['m'], t['c'], round(pos / SR, 4), round(len(x) / SR, 4)]); y += [x, np.zeros(int(GAP * SR))]; pos += len(x) + int(GAP * SR)
    print(t['m'], 'cents %+.1f' % t['c'], 'len %.2f' % (len(x) / SR), 'peak %.2f' % np.abs(x).max())
y = np.concatenate(y); os.makedirs(out, exist_ok=True); sf.write(os.path.join(out, 'guitar-%s.wav' % name), y, SR, subtype='PCM_16')
print('total %.1f s' % (len(y) / SR)); print(json.dumps(T, separators=(',', ':')))
