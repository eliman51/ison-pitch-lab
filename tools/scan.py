#!/usr/bin/env python3
"""The deep scan of one singer's recording: every word, letter, syllable and note, with loud and soft.

    ~/ison-singer/venv/bin/python -I tools/scan.py <recording> <words.txt> <out folder> [--spoken "tone three"]
                                                                                       [--ladder 48.72,50.7,...] [--home 55.82]

words.txt holds the sung words, one line of the song per line (the lines only shape the report). --spoken gives words
that are said, not sung, before the song starts, so they are not mistaken for the first sung words.

What it does, in order:
  1. Pitch, measured twice (Praat's autocorrelation through parselmouth, and librosa's pyin) every 5 ms. Praat is the
     main meter; pyin fills its short gaps and tells how much to trust it (the report says how often they agree).
  2. The singer's own ladder: the pitches he keeps returning to (peaks of where his voice spends its time).
  3. Notes: the pitch line is laid on the ladder (a note changes only when the voice has clearly moved and stayed),
     slides shorter than 70 ms are joined to their neighbours, the low creak at the start of a breath is kept as a
     "scoop", and a short dip under a consonant is dropped.
  4. Letters: torchaudio's MMS forced aligner says where every letter of the words falls. A syllable's vowel is taken
     from its vowel letter when the aligner is sure of it, otherwise just after the consonant before it.
  5. Each syllable gets the notes that start in it; a held note with two syllables on it is cut at the second vowel.
  6. Loud and soft (Praat intensity over the sung part of each syllable), vibrato on long notes, and an emphasis mark
     (# to #####) from loudness, length and number of notes against the rest of its line.

It writes <out>/scan.txt (the report to read) and <out>/scan.json (the same for programs). Needs ~/ison-singer/venv
with praat-parselmouth, librosa, torch, torchaudio and cmudict. Claude cannot hear: this is measurement.
"""
import json, os, re, sys


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    skip = [opt(k) for k in ('--spoken', '--ladder', '--home') if opt(k) is not None]
    a = [x for x in a if x not in skip]
    if len(a) < 3:
        sys.exit(__doc__)
    audio, wfile, out = a[:3]; os.makedirs(out, exist_ok=True)
    import numpy as np, librosa, parselmouth, cmudict, importlib.util as iu
    from scipy.signal import find_peaks
    sp = iu.spec_from_file_location('mel', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'melody.py')); mel = iu.module_from_spec(sp); sp.loader.exec_module(mel)
    dt = 0.005
    # 1. pitch, twice
    x44 = mel.load(audio, 44100); snd = parselmouth.Sound(x44.astype('float64'), 44100)
    pt = snd.to_pitch_ac(time_step=dt, pitch_floor=75, pitch_ceiling=450, very_accurate=True)
    f = pt.selected_array['frequency']; t = pt.xs(); f[f == 0] = np.nan
    x22 = librosa.resample(x44, orig_sr=44100, target_sr=22050)
    f2 = librosa.pyin(x22, fmin=75, fmax=450, sr=22050, frame_length=2048, hop_length=110, fill_na=np.nan)[0]; t2 = np.arange(len(f2)) * 110 / 22050
    g = np.interp(t, t2, np.nan_to_num(f2)); g[np.interp(t, t2, (~np.isnan(f2)).astype(float)) <= 0.5] = np.nan
    with np.errstate(divide='ignore', invalid='ignore'):
        m = 69 + 12 * np.log2(f / 440); m2 = 69 + 12 * np.log2(g / 440)
    both = ~np.isnan(m) & ~np.isnan(m2); agree = float(np.mean(np.abs(m - m2)[both] < 0.3))
    it = snd.to_intensity(minimum_pitch=75, time_step=dt); db = np.interp(t, it.xs(), it.values[0])
    nan = np.isnan(m); i = 0
    while i < len(m):                                    # short gaps in the main meter, filled from the second one
        if nan[i]:
            j = i
            while j < len(m) and nan[j]:
                j += 1
            if 0 < i and j < len(m) and j - i <= 16 and np.all(~np.isnan(m2[i:j])) and abs(np.nanmedian(m2[i:j]) - m[i - 1]) < 2.5:
                m[i:j] = m2[i:j]
            i = j
        else:
            i += 1
    ok = ~np.isnan(m)
    # 2. the ladder
    if opt('--ladder'):
        LAD = np.array([float(v) for v in opt('--ladder').split(',')])
    else:
        grid = np.arange(36, 72, 0.02); h, _ = np.histogram(m[ok], bins=np.append(grid - 0.01, grid[-1] + 0.01))
        k = np.convolve(h, np.exp(-0.5 * (np.arange(-40, 41) * 0.02 / 0.12) ** 2), mode='same')
        pk, _ = find_peaks(k, prominence=k.max() * 0.012, distance=30); LAD = grid[pk]
    HOME = int(np.argmin(np.abs(LAD - float(opt('--home'))))) if opt('--home') else None

    # 3. notes
    def quant(p, K=25.0, sig=0.35):
        n, S = len(p), len(LAD); em = (p[:, None] - LAD[None, :]) ** 2 / (2 * sig * sig)
        em[np.min(np.abs(p[:, None] - LAD[None, :]), axis=1) > 1.3] = 0          # far from every step: a scoop or a slip, it joins its neighbour
        c = em[0].copy(); bk = np.zeros((n, S), int)
        for q in range(1, n):
            arg = c.argmin(); sw = c[arg] + K; use = c <= sw
            bk[q] = np.where(use, np.arange(S), arg); c = np.where(use, c, sw) + em[q]
        s = np.zeros(n, int); s[-1] = c.argmin()
        for q in range(n - 1, 0, -1):
            s[q - 1] = bk[q][s[q]]
        return s
    notes = []; i = 0
    while i < len(m):
        if not ok[i]:
            i += 1; continue
        j = i
        while j < len(m) and ok[j]:
            j += 1
        if j - i >= 8:
            s = quant(m[i:j]); a0 = 0
            for b in range(1, len(s) + 1):
                if b == len(s) or s[b] != s[a0]:
                    seg = m[i + a0:i + b]; near = np.abs(seg - LAD[s[a0]]) < 1.3; core = seg[near] if near.sum() > 3 else seg
                    core = core[len(core) // 5:len(core) - len(core) // 5] if len(core) > 8 else core
                    low = int(np.argmax(near)) if near.any() and a0 == 0 else 0
                    notes.append({'t0': float(t[i + a0]), 't1': float(t[i + b - 1] + dt), 'k': int(s[a0]), 'raw': float(np.median(core)), 'run': i,
                                  'scoop': round(low * dt, 3) if (low >= 6 and np.nanmedian(seg[:low]) < LAD[s[a0]]) else 0}); a0 = b
        i = j
    k = 0
    while k < len(notes):                                # a very short note between two others is the slide between them
        q = notes[k]
        if q['t1'] - q['t0'] < 0.07:
            L = notes[k - 1] if k > 0 and notes[k - 1]['run'] == q['run'] else None; R = notes[k + 1] if k + 1 < len(notes) and notes[k + 1]['run'] == q['run'] else None
            if L and R:
                if L['k'] == R['k']:
                    L['t1'] = R['t1']; del notes[k:k + 2]; continue
                mid = (q['t0'] + q['t1']) / 2; L['t1'] = mid; R['t0'] = mid; del notes[k]; continue
            if L:
                L['t1'] = q['t1']; del notes[k]; continue
            if R:
                R['t0'] = q['t0']; del notes[k]; continue
            if q['t1'] - q['t0'] < 0.05:
                del notes[k]; continue
        k += 1
    k = 0
    while k < len(notes):                                # a short dip well under both neighbours is a consonant, or the voice falling away
        q = notes[k]; d = q['t1'] - q['t0']
        L = notes[k - 1] if k > 0 and abs(notes[k - 1]['t1'] - q['t0']) < 0.02 else None; R = notes[k + 1] if k + 1 < len(notes) and abs(notes[k + 1]['t0'] - q['t1']) < 0.02 else None
        low = lambda o: o is None or o['k'] - q['k'] >= 2
        if d < 0.15 and (L or R) and low(L) and low(R):
            if L and R and L['k'] == R['k']:
                L['t1'] = R['t1']; del notes[k:k + 2]; continue
            if L and not R:
                del notes[k]; continue
            if R:
                R['t0'] = q['t0']; R['scoop'] = max(R.get('scoop', 0), d); del notes[k]; continue
        k += 1
    # 4. letters and syllables
    lines = [l.split() for l in open(wfile, encoding='utf-8').read().strip().split('\n') if l.strip()]
    norm = lambda w: re.sub(r"[^a-z']", '', w.lower().replace('’', "'"))
    spoken = [norm(w) for w in (opt('--spoken') or '').split()]
    words = spoken + [norm(w) for l in lines for w in l]
    import torch, torchaudio
    b = torchaudio.pipelines.MMS_FA; model = b.get_model(); tok = b.get_tokenizer(); al = b.get_aligner()
    x16 = mel.load(audio, 16000)
    with torch.inference_mode():
        em, _ = model(torch.tensor(x16)[None])
    r = len(x16) / 16000 / em.shape[1]
    LT = [[(q.start * r, q.end * r, float(q.score)) for q in w] for w in al(em[0], tok([w.replace("'", '') for w in words]))]
    cmu = cmudict.dict(); syl = []; wi = len(spoken)
    for li, l in enumerate(lines):
        for w0 in l:
            w = words[wi]; sp_ = LT[wi]; wi += 1
            pr = (cmu.get(w.strip("'")) or [None])[0]; lw = w.replace("'", '')
            st = [p[-1] for p in pr if p[-1].isdigit()] if pr else ['1'] * max(1, len(re.findall(r'[aeiouy]+', lw)))
            gq = mel.nuclei(lw, len(st))
            for j, ci in enumerate(gq):
                c0 = min(0 if j == 0 else max(ci - 1, gq[j - 1] + 1), len(sp_) - 1); ci = min(ci, len(sp_) - 1)
                vt = sp_[ci][0] - 0.02 if (sp_[ci][2] >= 0.5 or ci == c0) else sp_[ci - 1][0] + 0.07
                if ci > c0 and vt < sp_[ci - 1][0] + 0.03:
                    vt = sp_[ci - 1][0] + 0.05
                syl.append({'t': sp_[c0][0], 'v': vt, 'st': int(st[j]) if j < len(st) else 0, 'w': w0, 'j': j, 'line': li, 'ph': ' '.join(pr) if pr and j == 0 else '',
                            'txt': lw[c0:(max(gq[j + 1] - 1, ci + 1) if j + 1 < len(gq) else len(lw))], 'sure': round(sp_[c0][2], 2)})
    notes = [q for q in notes if q['t1'] > syl[0]['t'] - 0.1]
    # 5. notes onto syllables
    for s in syl:
        cand = [q['t0'] for q in notes if min(s['t'], s['v']) - 0.08 <= q['t0'] <= s['v'] + 0.12]
        s['b'] = min(cand, key=lambda z: abs(z - s['v'])) if cand else None
    for p, q in zip(syl, syl[1:]):
        if q['b'] is not None and p['b'] is not None and q['b'] <= p['b']:
            q['b'] = None
    for s in syl:
        if s['b'] is None:
            for i, q in enumerate(notes):
                if q['t0'] + 0.06 < s['v'] < q['t1'] - 0.06:
                    n2 = dict(q); q['t1'] = s['v']; n2['t0'] = s['v']; n2['scoop'] = 0; notes.insert(i + 1, n2); break
            s['b'] = s['v']
    for i, s in enumerate(syl):
        nb = syl[i + 1]['b'] if i + 1 < len(syl) else 1e9
        s['n'] = [q for q in notes if s['b'] - 0.011 <= q['t0'] < nb - 0.011]
    if HOME is None:
        last = [s for s in syl if s['n']][-1]['n'][-1]['k']; HOME = last

    # 6. loud and soft, vibrato, emphasis; the report
    def dbm(p, q):
        kk = (t >= p) & (t < q) & ok; return float(10 * np.log10(np.mean(10 ** (db[kk] / 10)))) if kk.any() else 0.0

    def vib(p, q):
        kk = (t >= p + 0.08) & (t < q - 0.03) & ok
        if kk.sum() < 50:
            return None
        y = m[kk]; y = y - np.polyval(np.polyfit(np.arange(len(y)), y, 2), np.arange(len(y)))
        return float(np.percentile(y, 95) - np.percentile(y, 5)) / 2, len(np.where(np.diff(np.sign(y)) != 0)[0]) / 2 / (len(y) * dt)
    dev = np.array([q['raw'] - LAD[q['k']] for q in notes]); wt = np.array([q['t1'] - q['t0'] for q in notes])
    R = ['DEEP SCAN of ' + os.path.basename(audio), '',
         'Pitch measured two ways every 5 ms; the two agree within 0.3 of a half step %.0f%% of the time.' % (100 * agree),
         '%d notes, %.1f seconds of singing. Notes sit on average %.0f cents from their ladder step.' % (len(notes), wt.sum(), 100 * np.average(np.abs(dev), weights=wt)),
         '', 'THE LADDER (step 0 is the home note; piano note numbers, 60 = middle C)']
    for kk in range(len(LAD)):
        on = [i for i, q in enumerate(notes) if q['k'] == kk]
        R.append('   step %+d   %.2f   (%+.2f half steps from home)   %5.1f s in %d notes' % (kk - HOME, LAD[kk], LAD[kk] - LAD[HOME], sum(wt[i] for i in on), len(on)))
    R += ['', 'Each syllable: * = the word\'s accent; when it starts; how long; louder or softer than its line; emphasis; its notes as step:seconds.']
    J = {'ladder': [round(float(v), 2) for v in LAD], 'home': HOME, 'agree': round(agree, 3), 'lines': []}
    for li, l in enumerate(lines):
        S = [s for s in syl if s['line'] == li and s['n']]; miss = [s['txt'] for s in syl if s['line'] == li and not s['n']]
        if not S:
            continue
        a0 = S[0]['n'][0]['t0']; b0 = S[-1]['n'][-1]['t1']; prev = [s for s in syl if s['line'] == li - 1 and s['n']]
        gap = a0 - prev[-1]['n'][-1]['t1'] if prev else 0
        dbs = [dbm(s['n'][0]['t0'], s['n'][-1]['t1']) for s in S]; med = float(np.median(dbs)); durs = [s['n'][-1]['t1'] - s['n'][0]['t0'] for s in S]; dmed = float(np.median(durs))
        R += ['', 'LINE %d   %.2f to %.2f s (%.1f s)   breath before: %.2f s   %d syllables, %.1f a second   lowest %+d, highest %+d, ends on %+d' % (
            li + 1, a0, b0, b0 - a0, max(0, gap), len(S), len(S) / (b0 - a0), min(q['k'] for s in S for q in s['n']) - HOME, max(q['k'] for s in S for q in s['n']) - HOME, S[-1]['n'][-1]['k'] - HOME),
            '   "' + ' '.join(l) + '"']
        JL = {'text': ' '.join(l), 't0': round(a0, 3), 't1': round(b0, 3), 'breath': round(max(0, gap), 3), 'syl': []}
        for s, d, du in zip(S, dbs, durs):
            ex = []
            if s['n'][0].get('scoop'):
                ex.append('scoops up from below')
            lg = max(s['n'], key=lambda q: q['t1'] - q['t0'])
            if lg['t1'] - lg['t0'] >= 0.45:
                v = vib(lg['t0'], lg['t1'])
                if v and v[0] > 0.25:
                    ex.append('vibrato %.0f cents, %.1f a second' % (v[0] * 100, v[1]))
            if s['sure'] < 0.4:
                ex.append('letters uncertain')
            emph = (d - med) / 2.5 + float(np.log2(max(du, 0.05) / dmed)) + (len(s['n']) - 1) * 0.4
            R.append('   %-11s %s %7.2f  %4.2fs  %+5.1f dB  %-5s  %-46s %s' % (('' if s['j'] == 0 else '-') + s['txt'], '*' if s['st'] == 1 else ' ', s['n'][0]['t0'], du, d - med,
                     '#' * max(0, min(5, int(round(emph + 1)))), ' '.join('%+d:%.2f' % (q['k'] - HOME, q['t1'] - q['t0']) for q in s['n']), '; '.join(ex)))
            JL['syl'].append({'s': s['txt'], 'word': s['w'], 'first': s['j'] == 0, 'accent': s['st'] == 1, 'sounds': s['ph'], 't0': round(s['n'][0]['t0'], 3), 'dur': round(du, 3), 'db': round(d - med, 1), 'emph': round(emph, 2),
                              'notes': [[q['k'] - HOME, round(q['t1'] - q['t0'], 3), round(q['raw'], 2)] for q in s['n']], 'scoop': bool(s['n'][0].get('scoop'))})
        if miss:
            R.append('   (no note found for: ' + ', '.join(miss) + ')')
        J['lines'].append(JL)
    open(os.path.join(out, 'scan.txt'), 'w', encoding='utf-8').write('\n'.join(R) + '\n')
    json.dump(J, open(os.path.join(out, 'scan.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('\n'.join(R[:14 + len(LAD)])); print('...'); print('Saved: ' + os.path.join(out, 'scan.txt') + ' and scan.json')


if __name__ == '__main__':
    main()
