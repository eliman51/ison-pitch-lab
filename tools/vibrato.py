#!/usr/bin/env python3
"""Every spot in a recording where the singer's voice swings on one held note (the "Polish the vibrato" unit).

    ~/ison-singer/venv/bin/python -I tools/vibrato.py <recording> <scan.json> <phrases> > rows.js

<phrases> is the melody's shapes as "A8,B6,A9,..." (name and how many of his syllables each holds), the same list
tools/overlay.py keeps for Tone 3 and tools/p23t4.mel.json holds for Tone 4. It must add up to the scan's syllables.

How a spot is found. Pitch is measured every 2.5 ms through the whole file (Praat, through parselmouth). In every
note the deep scan (tools/scan.py) found that he holds for 0.32 s or more, a cubic is taken out first so a slide
does not count as a swing, then a smooth swing is fitted by least squares at every rate from 3.2 to 9.8 a second
and the best one kept. A spot is kept when that swing explains 55% or more of what is left, is 12 to 95 cents wide
and lasts at least 1.6 swings. Wider than that is a bend, not a swing, and the fit says so by coming out poor.

What it prints is the rows of VB_DAT in index.html:
  shape, phrase (1 to 26), cell, step from home, his pitch (MIDI), note start, note end, clip start, clip end,
  phrase start, phrase end, swings a second, width in cents, the word.
The clip is the note with a little of what comes before it, so the moment can be heard in its approach.
"""
import json, sys
import numpy as np
import librosa
import parselmouth

LO, HI = 3.2, 9.8          # swings a second worth looking for
MINW, MAXW = 12, 95        # cents, peak to peak
MINR2, MINCYC = 0.55, 1.6


def fit(T, cents, ok, a, b):
    """-> (swings a second, width in cents, how much of the wobble the swing explains)"""
    k = (T >= a) & (T < b) & ok
    if k.sum() < 60 or k.sum() * 0.0025 < 0.8 * (b - a):
        return None
    x = T[k] - a
    y = cents[k]
    M0 = np.vstack([x ** j for j in range(4)]).T                      # the slide, taken out
    var = float(np.var(y - M0 @ np.linalg.lstsq(M0, y, rcond=None)[0]))
    if var <= 0:
        return None
    best = None
    for r in np.arange(LO, HI + 0.01, 0.05):
        M = np.hstack([M0, np.cos(2 * np.pi * r * x)[:, None], np.sin(2 * np.pi * r * x)[:, None]])
        c = np.linalg.lstsq(M, y, rcond=None)[0]
        r2 = 1 - float(np.var(y - M @ c)) / var
        if best is None or r2 > best[0]:
            best = (r2, float(r), 2 * float(np.hypot(c[4], c[5])))
    return best[1], best[2], best[0]


def main():
    aud, scan, shapes = sys.argv[1], sys.argv[2], sys.argv[3]
    SH = [(s[0], int(s[1:])) for s in shapes.split(',')]
    y, sr = librosa.load(aud, sr=22050, mono=True)
    p = parselmouth.Sound(y.astype('float64'), sampling_frequency=sr).to_pitch_ac(
        time_step=0.0025, pitch_floor=60.0, pitch_ceiling=400.0, voicing_threshold=0.4, octave_cost=0.05)
    T = np.array(p.xs())
    f0 = p.selected_array['frequency']
    ok = f0 > 0
    cents = np.full(len(f0), np.nan)
    cents[ok] = 1200 * np.log2(f0[ok] / 55.0)

    d = json.load(open(scan))
    S = [s for L in d['lines'] for s in L['syl']]
    if len(S) != sum(k for _, k in SH):
        sys.exit('the shapes hold %d syllables, the scan has %d' % (sum(k for _, k in SH), len(S)))
    i, ph = 0, {}
    for pi, (nm, k) in enumerate(SH):
        for c in range(k):
            S[i]['shape'], S[i]['phrase'], S[i]['cell'] = nm, pi + 1, c + 1
            i += 1
        g = S[i - k:i]
        ph[pi + 1] = (round(g[0]['t0'], 2), round(g[-1]['t0'] + g[-1]['dur'], 2))

    rows = []
    for si, s in enumerate(S):
        t = s['t0']
        prev = S[si - 1]['t0'] + S[si - 1]['dur'] if si else 0.0
        nxt = S[si + 1]['t0'] if si + 1 < len(S) else 1e9
        for ni, n in enumerate(s['notes']):
            a0, b0 = t, t + n[1]
            t = b0
            if n[1] < 0.32:
                continue
            a, b = a0 + (0.10 if ni == 0 else 0.05), b0 - 0.04
            if b - a < 0.26:
                continue
            f = fit(T, cents, ok, a, b)
            if not f:
                continue
            rate, ext, r2 = f
            if r2 < MINR2 or not (MINW <= ext <= MAXW) or rate * (b - a) < MINCYC:
                continue
            c0 = max(prev + 0.02, (s['t0'] if ni == 0 else a0) - 0.30)
            c1 = min(nxt - 0.02, b0 + 0.22)
            rows.append("['%s',%d,%d,%d,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.1f,%d,'%s']" % (
                s['shape'], s['phrase'], s['cell'], n[0], n[2], a0, b0, c0, c1,
                ph[s['phrase']][0], ph[s['phrase']][1], rate, round(ext), s['word']))
    for j in range(0, len(rows), 3):
        print('  ' + ','.join(rows[j:j + 3]) + ',')
    print('  /* %d spots */' % len(rows), file=sys.stderr)


main()
