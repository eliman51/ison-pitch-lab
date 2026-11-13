#!/usr/bin/env python3
"""Turn a recording of one singer into a reusable Song Maker melody.

    python3 tools/melody.py recording.mp3 words.txt "Name of the melody"  ->  "<name>.melody.json"

words.txt holds the words exactly as they are sung (line breaks do not matter). The tool finds where every
letter falls in the recording, measures the singer's pitch, cuts it into notes, and writes the melody as the
app's own notation: one "seat" per sung syllable, with every note the singer put on that syllable, his own
tuning, his note lengths and his breaths. The app can then lay any other words on the same melody.

Needs ~/ison-singer/venv (torch, torchaudio, librosa, cmudict). Runs on this Mac only.
"""
import json, os, re, subprocess, sys, tempfile, wave

V = set('aeiouy')


def load(path, sr):
    t = tempfile.mktemp(suffix='.wav')
    subprocess.run(['afconvert', '-f', 'WAVE', '-d', 'LEI16@%d' % sr, '-c', '1', path, t], check=True)
    import numpy as np
    w = wave.open(t); x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32) / 32768; w.close(); os.remove(t)
    return x


def letters(x16, words):
    """-> for every word, [start, end] seconds of each of its letters."""
    import torch, torchaudio
    b = torchaudio.pipelines.MMS_FA; model = b.get_model(); tok = b.get_tokenizer(); al = b.get_aligner()
    with torch.inference_mode():
        em, _ = model(torch.tensor(x16)[None])
    r = len(x16) / 16000 / em.shape[1]
    return [[(s.start * r, s.end * r) for s in sp] for sp in al(em[0], tok(words))]


def nuclei(word, k):
    """Where in the spelling each of the word's k sung vowels starts."""
    g = [m.start() for m in re.finditer(r'[aeiouy]+', word) if not (m.start() == 0 and word[0] == 'y' and len(word) > 1 and m.end() == 1)]
    if len(g) > k and word.endswith('e') and len(g) > 1 and not re.search(r'[^aeiouy]le$', word):
        g = g[:-1]
    if len(g) > k and re.search(r'[^aeiouy]es$|[^aeiouytd]ed$', word):
        g = g[:-1]
    while len(g) > k:
        g.pop(1 if len(g) > 2 else -1)
    return g or [0]


def notes_of(x, sr):
    """The singer's pitch cut into notes: [start, end, midi]."""
    import numpy as np, librosa
    from scipy.signal import medfilt
    f0, vo, _ = librosa.pyin(x, fmin=70, fmax=600, sr=sr, frame_length=2048, hop_length=220, fill_na=np.nan)
    hop = 220 / sr; p = 69 + 12 * np.log2(f0 / 440); ok = ~np.isnan(p)
    q = p.copy(); q[ok] = medfilt(p[ok], 5)
    out, i, n = [], 0, len(q)
    while i < n:
        if not ok[i]:
            i += 1; continue
        j = i
        while j < n and ok[j]:
            j += 1
        if j - i >= 6:
            a = i
            while a < j:                                # grow one note until the pitch has clearly moved away and stayed away
                b = a + 1
                while b < j:
                    med = np.median(q[a:b])
                    if b - a >= 5 and b + 5 <= j and np.all(np.abs(q[b:b + 5] - med) > 0.6) and abs(np.median(q[b:b + 8]) - med) > 0.6:
                        break
                    b += 1
                out.append([a * hop, b * hop, float(np.median(q[a + (b - a) // 5:b - (b - a) // 5] if b - a > 6 else q[a:b]))]); a = b
        i = j
    # a very short note between two others is the slide between them, not a note of its own
    k = 0
    while k < len(out):
        s = out[k]
        if s[1] - s[0] < 0.09:
            L = out[k - 1] if k > 0 and abs(out[k - 1][1] - s[0]) < 0.03 else None
            R = out[k + 1] if k + 1 < len(out) and abs(out[k + 1][0] - s[1]) < 0.03 else None
            if L and (not R or abs(L[2] - s[2]) <= abs(R[2] - s[2])):
                L[1] = s[1]; out.pop(k); continue
            if R:
                R[0] = s[0]; out.pop(k); continue
            if s[1] - s[0] < 0.06:
                out.pop(k); continue
        k += 1
    # a blip that jumps far from both neighbours for an instant is the meter slipping (a consonant, a breath), not a sung note
    k = 0
    while k < len(out):
        s = out[k]; L = out[k - 1] if k > 0 and abs(out[k - 1][1] - s[0]) < 0.03 else None; R = out[k + 1] if k + 1 < len(out) and abs(out[k + 1][0] - s[1]) < 0.03 else None
        far = lambda o: o is None or abs(o[2] - s[2]) > 3.4
        if s[1] - s[0] < 0.2 and (L or R) and far(L) and far(R):
            if L:
                L[1] = s[1]
            else:
                R[0] = s[0]
            out.pop(k); continue
        k += 1
    return out, (np.arange(n) * hop, q)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    audio, wfile, name = sys.argv[1:4]
    import numpy as np, cmudict
    cmu = cmudict.dict()
    raw = open(wfile, encoding='utf-8').read().split()
    words = [re.sub(r"[^a-z']", '', t.lower().replace('’', "'")) for t in raw]
    words = [w for w in words if w]
    L = letters(load(audio, 16000), words)
    nts, track = notes_of(load(audio, 22050), 22050)
    # every sung syllable: when it starts, and whether the word's accent is on it
    syl = []
    for w, sp in zip(words, L):
        pr = cmu.get(w.strip("'"), [None])[0]
        st = [p[-1] for p in pr if p[-1].isdigit()] if pr else ['1'] * max(1, len(re.findall(r'[aeiouy]+', w)))
        g = nuclei(w, len(st))
        for j, ci in enumerate(g):
            c0 = 0 if j == 0 else max(ci - 1, g[j - 1] + 1)
            syl.append({'t': sp[min(c0, len(sp) - 1)][0], 'acc': st[j] == '1' if j < len(st) else False, 'w': w, 'j': j, 'k': len(g), 'end': sp[-1][1]})
    # a syllable starts where a note starts if one is near; otherwise the held note is cut there (the same note sung again)
    for s in syl:
        near = min(nts, key=lambda q: abs(q[0] - s['t']))
        if abs(near[0] - s['t']) <= 0.14:
            s['t'] = near[0]
    for a, b in zip(syl, syl[1:]):
        if b['t'] <= a['t'] + 0.05:
            b['t'] = a['t'] + 0.05
    nts = [q for q in nts if q[1] > syl[0]['t'] - 0.05]
    for s in syl[1:]:
        for i, q in enumerate(nts):
            if q[0] + 0.07 < s['t'] < q[1] - 0.07:
                nts[i:i + 1] = [[q[0], s['t'], q[2]], [s['t'], q[1], q[2]]]; break
    # the singer's own ladder of pitches
    allp = sorted((q[2], q[1] - q[0]) for q in nts); cl = [[allp[0]]]
    for p in allp[1:]:
        if p[0] - cl[-1][-1][0] > 0.34 and p[0] - np.average([a for a, _ in cl[-1]], weights=[b for _, b in cl[-1]]) > 0.5:
            cl.append([p])
        else:
            cl[-1].append(p)
    cen = [float(np.average([a for a, _ in c], weights=[b for _, b in c])) for c in cl]
    wt = [sum(b for _, b in c) for c in cl]
    keep = [i for i in range(len(cen)) if wt[i] >= 0.25]          # a pitch touched for less than a quarter second in the whole song is a slip
    cen = [cen[i] for i in keep]
    deg = lambda m: int(np.argmin([abs(m - c) for c in cen]))
    home = deg(nts[-1][2])
    # seats
    seats = []
    for i, s in enumerate(syl):
        t1 = syl[i + 1]['t'] if i + 1 < len(syl) else 1e9
        mine = [q for q in nts if s['t'] - 0.02 <= q[0] < t1 - 0.02]
        if not mine:
            prev = seats[-1]['n'][-1] if seats else [home, 0.3]
            seats.append({'n': [[prev[0], 0.25]], 't': s['t'], 'end': s['t'] + 0.25, 's': s, 'guess': True}); continue
        n = []
        for q in mine:
            d = deg(q[2])
            if n and n[-1][0] == d:
                n[-1][1] += q[1] - q[0]
            else:
                n.append([d, q[1] - q[0]])
        seats.append({'n': n, 't': mine[0][0], 'end': mine[-1][1], 's': s})
    one = sorted(sum(x[1] for x in z['n']) for z in seats if len(z['n']) == 1)
    beat = one[len(one) // 2] if one else 0.5
    rq = lambda sec, step=0.25: max(step, round(sec / beat / step) * step)
    fm = lambda x: ('%g' % x).replace('0.', '.')
    tok = []
    for i, z in enumerate(seats):
        gap = seats[i + 1]['t'] - z['end'] if i + 1 < len(seats) else 9
        t = '_'.join('%d%s' % (d - home, '' if rq(sec) == 1 else ':' + fm(rq(sec))) for d, sec in z['n'])
        tok.append(('>' if z['s']['acc'] and z['s']['k'] > 1 or (z['s']['acc'] and len(z['s']['w']) > 3) else '') + t)
        if i + 1 == len(seats):
            tok.append('//')
        elif gap > 0.3 and z['s']['j'] == z['s']['k'] - 1:
            tok.append('/' + fm(rq(gap, 0.5)))
    M = {'id': 'rec:' + re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-'), 'g': 'From a recording', 'n': name,
         'd': 'Taken note by note from a recording of one singer: his notes, his tuning, his note lengths and his breaths.',
         'sc': 'major', 'bpm': round(60 / beat), 'home': round(cen[home], 2), 'tun': {'lo': -home, 'v': [round(c - cen[home], 2) for c in cen]}, 'm': ' '.join(tok),
         'words': ' '.join(raw), 'syl': [[round(z['t'], 3), round(z['end'], 3), z['s']['w'], z['s']['j']] for z in seats]}
    out = name + '.melody.json'
    json.dump(M, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print('syllables %d, notes %d, ladder %s (home = step 0 at MIDI %.2f), beat %.2f s' % (len(seats), sum(len(z['n']) for z in seats), M['tun']['v'], cen[home], beat))
    print('syllables with no clear note of their own (guessed):', [z['s']['w'] for z in seats if z.get('guess')])
    print(M['m']); print('Saved: ' + out)


if __name__ == '__main__':
    main()
