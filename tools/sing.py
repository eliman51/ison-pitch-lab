#!/usr/bin/env python3
"""Sing a notes file from the Song Maker with a DiffSinger voice, on this computer.

    python3 tools/sing.py "song notes.mid"            -> "song sung.wav" (and .m4a on a Mac)

The notes file is the one the app saves from "1. Download the notes and words". The result goes
back into the app with "3. Bring in the sung recording". It starts exactly where the song starts
and every note sits on the app's own pitch, church tuning included.

Needs (kept OUTSIDE this public repository, see ~/ison-singer):
  * a Python with onnxruntime, numpy, pyyaml, cmudict   (~/ison-singer/venv)
  * a DiffSinger voice folder in the OpenUtau layout    (~/ison-singer/voices/<name>/bank)
Voice files have their own licences. Read them. None may be copied into this repository.

How it works, in the order the voice needs it:
  words -> sounds (CMU dictionary) -> one vowel per sung syllable, consonants just before the next note
  dur model     how long each consonant lasts
  pitch model   a natural pitch line (slides, vibrato), then every note is re-centred on its exact pitch
  acoustic      the voice itself, as a picture of the sound
  vocoder       the picture turned into sound
"""
import argparse, os, re, struct, subprocess, sys, time, wave

HOME = os.path.expanduser('~/ison-singer')
HEAD = 0.5          # seconds of lead-in the voice gets before each phrase
TAIL = 0.35         # seconds after a phrase for the last sound to die away
GAP = 0.12          # a silence longer than this between notes starts a new phrase
SAY = {'blessid': 'b l eh s ih d', 'belovid': 'b ih l ah v ih d', 'la': 'l aa'}


# ---------------------------------------------------------------- the notes file
def read_midi(path):
    """-> (notes [{t,d,m,ly}] with m a float MIDI pitch, seconds), reading lyrics and the app's exact tuning."""
    b = open(path, 'rb').read()
    if b[:4] != b'MThd':
        sys.exit('That is not a MIDI notes file.')
    ntr, div = struct.unpack('>HH', b[10:14])
    if div & 0x8000:
        sys.exit('This kind of MIDI timing is not supported.')
    pos, tempo, cents, raw = 14, [], None, []
    for _ in range(ntr):
        if b[pos:pos + 4] != b'MTrk':
            break
        end = pos + 8 + struct.unpack('>I', b[pos + 4:pos + 8])[0]
        i, tick, run, lyric, on = pos + 8, 0, 0, None, {}

        def vlq(i):
            v = 0
            while True:
                c = b[i]; i += 1; v = (v << 7) | (c & 127)
                if c < 128:
                    return v, i
        while i < end:
            dt, i = vlq(i); tick += dt; st = b[i]
            if st == 0xFF:
                ty = b[i + 1]; n, i = vlq(i + 2); data = b[i:i + n]; i += n
                if ty == 0x51:
                    tempo.append((tick, int.from_bytes(data, 'big')))
                elif ty == 0x05:
                    lyric = (tick, data.decode('utf-8', 'replace'))
                elif ty == 0x7F and data[:7] == b'\x7dison1:':
                    cents = [int(x) for x in data[7:].decode().split(',') if x.strip('-').isdigit()]
                continue
            if st in (0xF0, 0xF7):
                n, i = vlq(i + 1); i += n; continue
            if st & 0x80:
                run = st; i += 1
            k = run & 0xF0
            if k in (0xC0, 0xD0):
                i += 1; continue
            p, v = b[i], b[i + 1]; i += 2
            if k == 0x90 and v > 0:
                on[p] = (tick, lyric[1] if lyric and lyric[0] == tick else '-'); lyric = None
            elif k == 0x80 or (k == 0x90 and v == 0):
                if p in on:
                    raw.append((on[p][0], tick, p, on[p][1])); del on[p]
        pos = end
    tempo = sorted(tempo) or [(0, 500000)]
    if tempo[0][0] > 0:
        tempo.insert(0, (0, 500000))

    def sec(tick):
        s = 0.0
        for j, (tk, us) in enumerate(tempo):
            nx = tempo[j + 1][0] if j + 1 < len(tempo) else 1 << 60
            if tick <= tk:
                break
            s += (min(tick, nx) - tk) * us / 1e6 / div
        return s
    raw.sort()
    notes = []
    for j, (a, z, p, ly) in enumerate(raw):
        c = cents[j] if cents and len(cents) == len(raw) else 0
        notes.append({'t': sec(a), 'd': max(0.02, sec(z) - sec(a)), 'm': p + c / 100.0, 'ly': ly.strip()})
    return notes


# ---------------------------------------------------------------- words to sounds
class Sounds:
    def __init__(self, bank):
        import yaml, cmudict
        d = yaml.safe_load(open(os.path.join(bank, 'dsdur', 'dsdict-en.yaml'), encoding='utf-8'))
        self.vowels = {str(s['symbol']) for s in d['symbols'] if s['type'] == 'vowel'} - {'AP', 'SP'}
        self.bank = {str(e['grapheme']).lower(): [str(p) for p in e['phonemes']] for e in d['entries']}
        self.cmu = cmudict.dict()
        self.unknown = []

    @staticmethod
    def arpa(pr):
        """CMU sounds -> this voice's: unstressed AH is the weak 'ax', t between vowels softens, tr and dr are one sound."""
        out, V = [], lambda x: x[-1].isdigit()
        for i, p in enumerate(pr):
            q = p.rstrip('012').lower()
            if p == 'AH0':
                q = 'ax'
            if p == 'T' and 0 < i < len(pr) - 1 and V(pr[i - 1]) and pr[i + 1][-1] == '0':
                q = 'dx'
            out.append(q)
        s = ' '.join(out)
        s = re.sub(r'\bt r\b', 'tr', s); s = re.sub(r'\bd r\b', 'dr', s)
        return s.split()

    def say(self, word, want):
        """All the sounds of a word; of several ways to say it, the one with `want` vowels if there is one."""
        w = re.sub(r"[^a-z']", '', word.lower()).strip("'")
        if w in SAY:
            return SAY[w].split()
        c = [self.arpa(p) for p in self.cmu.get(w, [])]
        if not c and w.endswith("'s"):
            c = [self.arpa(p) + ['z'] for p in self.cmu.get(w[:-2], [])]
        if not c and w in self.bank:
            c = [self.bank[w]]
        if not c:
            self.unknown.append(word); return self.spell(w)
        for p in c:
            if sum(x in self.vowels for x in p) == want:
                return p
        return c[0]

    def spell(self, w):
        """Last resort for a word in no dictionary: a rough reading letter by letter."""
        m = {'a': 'ae', 'e': 'eh', 'i': 'ih', 'o': 'ow', 'u': 'ah', 'y': 'iy', 'c': 'k', 'q': 'k', 'x': 'k s', 'j': 'jh', 'h': 'hh'}
        out = []
        for ch in re.sub(r'(.)\1', r'\1', w.replace('th', 'T').replace('sh', 'S').replace('ch', 'C')):
            out += {'T': ['th'], 'S': ['sh'], 'C': ['ch']}.get(ch, m.get(ch, ch).split())
        return [p for p in out if p.isalpha()] or ['l', 'aa']


def syllables(notes, snd):
    """-> [{t, end, on:[consonants before the vowel], v:vowel, co:[consonants after], brk}] one per sung vowel."""
    groups, cur = [], None
    for n in notes:
        if n['ly'] in ('-', '') and cur:
            cur['seat'][-1].append(n)
        elif n['ly'] == '+' and cur:
            cur['seat'].append([n])
        else:
            cur = {'word': n['ly'] if n['ly'] not in ('+', '-', '') else 'la', 'seat': [[n]]}; groups.append(cur)
    out = []
    for g in groups:
        ph = snd.say(g['word'], len(g['seat']))
        vi = [i for i, p in enumerate(ph) if p in snd.vowels]
        if not vi:
            ph = ph + ['ax']; vi = [len(ph) - 1]
        seats = [(s[0]['t'], s[-1]['t'] + s[-1]['d']) for s in g['seat']]
        if len(vi) < len(seats):                      # more seats than vowels: the last vowel is held over the rest
            seats = seats[:len(vi) - 1] + [(seats[len(vi) - 1][0], seats[-1][1])]
        elif len(vi) > len(seats):                    # more vowels than seats: the last seat is shared out evenly
            a, z = seats[-1]; k = len(vi) - len(seats) + 1
            seats = seats[:-1] + [(a + (z - a) * j / k, a + (z - a) * (j + 1) / k) for j in range(k)]
        for j, (a, z) in enumerate(seats):
            lo = 0 if j == 0 else vi[j - 1] + 1
            hi = len(ph) if j == len(seats) - 1 else vi[j]
            out.append({'t': a, 'end': z, 'on': ph[lo:vi[j]], 'v': ph[vi[j]], 'co': ph[vi[j] + 1:hi] if j == len(seats) - 1 else []})
    return out


# ---------------------------------------------------------------- the voice
class Voice:
    def __init__(self, bank, mode, threads):
        import numpy as np, onnxruntime as ort, yaml
        self.np = np
        ort.set_default_logger_severity(3)
        o = ort.SessionOptions(); o.intra_op_num_threads = threads
        cfg = yaml.safe_load(open(os.path.join(bank, 'dsconfig.yaml'), encoding='utf-8'))
        self.sr, self.hop = 44100, 512
        self.depth = float(cfg.get('max_depth', 0.6))
        P = lambda *a: os.path.join(bank, *a)
        L = lambda p: ort.InferenceSession(p, o, providers=['CPUExecutionProvider'])
        ids = lambda p: {s: i for i, s in enumerate(open(p, encoding='utf-8').read().split('\n')) if s}
        self.tok = {'dur': ids(P('dsdur', 'files', 'phonemes.txt')), 'pitch': ids(P('dspitch', 'files', 'phonemes.txt')), 'ac': ids(P('dsacoustic', 'phonemes.txt'))}
        modes = sorted(f[:-4] for f in os.listdir(P('dsacoustic')) if f.endswith('.emb'))
        pick = [m for m in modes if m == mode or m.endswith('_' + mode)]
        if not pick:
            sys.exit('This voice has no mode "%s". It has: %s' % (mode, ', '.join(m.split('_')[-1] for m in modes)))
        e = lambda *a: np.fromfile(P(*a, pick[0] + '.emb'), dtype=np.float32)
        self.emb = {'dur': e('dsdur', 'files'), 'pitch': e('dspitch', 'files'), 'ac': e('dsacoustic')}
        self.lin_d, self.dur = L(P('dsdur', 'files', 'linguistic.onnx')), L(P('dsdur', 'files', 'dur.onnx'))
        self.lin_p, self.pit = L(P('dspitch', 'files', 'linguistic.onnx')), L(P('dspitch', 'files', 'pitch.onnx'))
        self.ac = L(P('dsacoustic', 'acoustic.onnx'))
        vc = yaml.safe_load(open(P('dsvocoder', 'vocoder.yaml'), encoding='utf-8'))
        self.voc = L(P('dsvocoder', vc['model']))

    def spk(self, which, n):
        return self.np.tile(self.emb[which][None, None, :], (1, n, 1)).astype(self.np.float32)

    def durations(self, ph, wdiv, wdur, midi):
        np = self.np; i64 = lambda a: np.array([a], dtype=np.int64)
        enc, mask = self.lin_d.run(None, {'tokens': i64([self.tok['dur'][p] for p in ph]), 'word_div': i64(wdiv), 'word_dur': i64(wdur)})
        return self.dur.run(None, {'encoder_out': enc, 'x_masks': mask, 'ph_midi': i64(midi), 'spk_embed': self.spk('dur', len(ph))})[0][0]

    def pitch(self, ph, phd, nmidi, nrest, ndur, base, expr, steps):
        np = self.np; i64 = lambda a: np.array([a], dtype=np.int64); n = int(sum(phd))
        enc, _ = self.lin_p.run(None, {'tokens': i64([self.tok['pitch'].get(p, self.tok['pitch']['SP']) for p in ph]), 'ph_dur': i64(phd)})
        return self.pit.run(None, {'encoder_out': enc, 'ph_dur': i64(phd), 'note_midi': np.array([nmidi], dtype=np.float32), 'note_rest': np.array([nrest], dtype=bool),
                                   'note_dur': i64(ndur), 'pitch': base[None].astype(np.float32), 'expr': np.full((1, n), expr, dtype=np.float32), 'retake': np.ones((1, n), dtype=bool),
                                   'spk_embed': self.spk('pitch', n), 'steps': np.array(steps, dtype=np.int64)})[0][0]

    def sound(self, ph, phd, midi, steps, gender):
        np = self.np; i64 = lambda a: np.array([a], dtype=np.int64); n = int(sum(phd))
        f0 = (440.0 * 2 ** ((midi - 69) / 12)).astype(np.float32)[None]
        mel = self.ac.run(None, {'tokens': i64([self.tok['ac'][p] for p in ph]), 'durations': i64(phd), 'f0': f0, 'gender': np.full((1, n), gender, dtype=np.float32),
                                 'velocity': np.ones((1, n), dtype=np.float32), 'spk_embed': self.spk('ac', n), 'depth': np.array(self.depth, dtype=np.float32), 'steps': np.array(steps, dtype=np.int64)})[0]
        return self.voc.run(None, {'mel': mel, 'f0': f0})[0][0]


def smooth(x, w, np):
    if w < 2:
        return x
    k = np.hanning(w + 2)[1:-1]; k /= k.sum(); p = w // 2
    return np.convolve(np.pad(x, (p, w - 1 - p), mode='edge'), k, mode='valid')


def phrase(V, notes, syl, a):
    """Sing one phrase. notes and syl are this phrase's; -> (samples, seconds before the first note that they start, report)."""
    np = V.np; fs = V.sr / V.hop; F = lambda s: int(round(s * fs))
    t0, t1 = notes[0]['t'], notes[-1]['t'] + notes[-1]['d']
    head = min(HEAD, a.room) if a.room is not None else HEAD
    breath = a.breath and a.gap >= 0.3 and head >= 0.45
    ph, wdiv, wdur, midi = ['SP'], [1], [0], [int(round(notes[0]['m']))]

    def note_at(t):
        for n in notes:
            if t < n['t'] + n['d'] - 1e-6:
                return int(round(n['m']))
        return int(round(notes[-1]['m']))
    on0 = syl[0]['on']
    if breath:
        B = min(0.42, a.gap - 0.05)
        wdur[0] = F(head - B); ph.append('AP'); wdiv.append(1); wdur.append(F(B)); midi.append(midi[0])
    ph += on0; wdiv[-1] += len(on0); midi += [midi[0]] * len(on0)
    caps = []                                          # the most room each syllable's closing consonants may take: part of the note they fall in, so the note is still heard

    def last_note(t):
        for q in notes:
            if q['t'] - 1e-6 <= t < q['t'] + q['d'] - 1e-6:
                return q['d']
        return notes[-1]['d']
    for j, s in enumerate(syl):
        nxt = syl[j + 1] if j + 1 < len(syl) else None
        tail = s['co'] + (nxt['on'] if nxt else [])
        ph += [s['v']] + tail; wdiv.append(1 + len(tail))
        caps.append(F(max(0.10, a.cons * last_note((nxt['t'] if nxt else t1) - 0.01))) if nxt else 1e9)
        wdur.append(F((nxt['t'] if nxt else t1) - t0) - F(s['t'] - t0)); midi += [note_at(s['t'])] * (1 + len(tail))
    if not breath:
        wdur[0] = F(head)
    ph.append('SP'); wdiv.append(1); wdur.append(F(TAIL)); midi.append(midi[-1])
    caps.append(1e9)
    wdur = [max(1, w) for w in wdur]
    pred = np.maximum(V.durations(ph, wdiv, wdur, midi), 0.5)
    # line the sounds up: the vowel of every syllable lands on its note; consonants keep the length the voice wants, squeezed only if they must be
    pos = np.zeros(len(ph) + 1); k = 0; edge = 0.0
    for w, (cnt, frames) in enumerate(zip(wdiv, wdur)):
        seg = pred[k:k + cnt].astype(float)
        if w < (2 if breath else 1):                   # lead-in: the consonants are not stretched, the silence or breath takes what is left
            cons = seg[1:].sum(); lim = min(frames * 0.6, caps[w - (2 if breath else 1)])
            if cons > lim:
                seg[1:] *= lim / cons
            seg[0] = frames - seg[1:].sum()
        else:                                          # a sung syllable: its consonants keep their own length and the vowel fills the note, however long
            cons = seg[1:].sum(); lim = min(frames * 0.6, caps[w - (2 if breath else 1)])
            if cons > lim:
                seg[1:] *= lim / cons
            seg[0] = frames - seg[1:].sum()
        for x in seg:
            pos[k + 1] = pos[k] + x; k += 1
    phd = np.diff(np.round(pos)).astype(int)
    if os.environ.get('SING_DEBUG'):
        print('   ', ' '.join('%s:%.0f>%d' % (p, q, r) for p, q, r in zip(ph, pred, phd)))
    for i in range(len(phd)):                          # nothing may be shorter than one frame
        if phd[i] < 1:
            j = int(np.argmax(phd)); phd[j] -= 1 - phd[i]; phd[i] = 1
    n = int(phd.sum()); hf = int(sum(wdur[:2 if breath else 1]))
    # the notes as the pitch model wants them: a rest for the lead-in, the notes, a rest for the tail
    nm, nr, nd, c = [notes[0]['m']], [True], [hf], hf
    for i, q in enumerate(notes):
        e = hf + F((notes[i + 1]['t'] if i + 1 < len(notes) else t1) - t0)
        nm.append(q['m']); nr.append(False); nd.append(max(1, e - c)); c += nd[-1]
    nm.append(notes[-1]['m']); nr.append(True); nd.append(max(1, n - c))
    if sum(nd) != n:
        nd[-2] += n - sum(nd)
    step = np.repeat(np.array(nm, dtype=float), nd)[:n]
    base = smooth(step, 9, np)
    if a.plain:
        cur = base.copy()
    else:
        cur = V.pitch(ph, [int(x) for x in phd], nm, nr, nd, base, a.expr, a.pitch_steps).astype(float)
        # re-centre every note on its exact pitch: the natural shape stays, the middle of the note is made true
        if a.wobble > 0:                                # the voice may lean and waver this far from the note and no further; slides between notes stay
            cur = base + a.wobble * np.tanh((cur - base) / a.wobble)
        off = []
        for rnd in range(3):
            sh, c = [], hf
            for q, d in zip(notes, nd[1:-1]):
                lo, hi = c + int(d * 0.25), c + max(int(d * 0.25) + 1, int(d * 0.92)); c += d
                sh.append(float(np.clip(q['m'] - np.median(cur[lo:hi]), -1.0, 1.0)))
            if rnd == 0:
                off = sh
            cur = cur + smooth(np.repeat(np.array([sh[0]] + sh + [sh[-1]]), nd)[:n], 7, np) * a.true
        if a.steady < 1:                                # less wobble: pull the line toward the plain notes
            cur = base + (cur - base) * a.steady
    y = V.sound(ph, [int(x) for x in phd], cur.astype(np.float32), a.steps, a.gender)
    f = int(0.004 * V.sr); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    dev = [abs(o) * 100 for o in (off if not a.plain else [0])]
    return y, hf * V.hop / V.sr, {'ph': ph, 'phd': phd, 'pitch': cur, 'hf': hf, 'dev': dev}


def main():
    ap = argparse.ArgumentParser(description='Sing a Song Maker notes file with a DiffSinger voice.')
    ap.add_argument('midi'); ap.add_argument('-o', '--out')
    ap.add_argument('--voice', default=os.path.join(HOME, 'voices', 'tiger', 'bank'), help='the voice folder')
    ap.add_argument('--mode', default='vinyl', help='which of the voice\'s colours to use')
    ap.add_argument('--steps', type=int, default=20, help='more is slower and a little cleaner')
    ap.add_argument('--pitch-steps', type=int, default=10)
    ap.add_argument('--expr', type=float, default=1.0, help='0 to 1: how much the voice shapes the pitch on its own')
    ap.add_argument('--steady', type=float, default=1.0, help='0 to 1: 1 keeps the natural slides and vibrato, 0 is perfectly flat notes')
    ap.add_argument('--wobble', type=float, default=0.3, help='how far, in semitones, the voice may waver from a note (0 = no limit)')
    ap.add_argument('--true', type=float, default=1.0, help='0 to 1: how firmly each note is centred on its exact pitch')
    ap.add_argument('--gender', type=float, default=0.0, help='-1 to 1: makes the voice sound bigger (below 0) or smaller')
    ap.add_argument('--cons', type=float, default=0.4, help='the most of a note that the consonants leading to the next note may take')
    ap.add_argument('--plain', action='store_true', help='skip the pitch model: flat notes with smooth joins')
    ap.add_argument('--no-breath', dest='breath', action='store_false', help='no breath sounds between phrases')
    ap.add_argument('--until', type=float, help='only sing the first so many seconds')
    ap.add_argument('--threads', type=int, default=0)
    a = ap.parse_args()
    import numpy as np
    notes = read_midi(a.midi)
    if a.until:
        notes = [n for n in notes if n['t'] < a.until]
    if not notes:
        sys.exit('There are no notes in that file.')
    for i in range(len(notes) - 1):                    # tiny gaps and overlaps inside a phrase are closed
        g = notes[i + 1]['t'] - (notes[i]['t'] + notes[i]['d'])
        if g < GAP:
            notes[i]['d'] = notes[i + 1]['t'] - notes[i]['t']
    snd = Sounds(a.voice); syl = syllables(notes, snd)
    V = Voice(a.voice, a.mode, a.threads)
    total = notes[-1]['t'] + notes[-1]['d'] + TAIL + 0.1
    out = np.zeros(int(total * V.sr) + V.hop, dtype=np.float32)
    cuts = [0] + [i + 1 for i in range(len(notes) - 1) if notes[i + 1]['t'] - (notes[i]['t'] + notes[i]['d']) >= GAP] + [len(notes)]
    t_start, devs, log = time.time(), [], []
    for c in range(len(cuts) - 1):
        ns = notes[cuts[c]:cuts[c + 1]]; t0, t1 = ns[0]['t'], ns[-1]['t'] + ns[-1]['d']
        ss = [s for s in syl if t0 - 1e-6 <= s['t'] < t1 - 1e-6]
        if not ss:
            continue
        prev_end = notes[cuts[c] - 1]['t'] + notes[cuts[c] - 1]['d'] if c else None
        a.gap = t0 - prev_end if prev_end is not None else 0.0
        a.room = None
        lead = 0.0
        if t0 < HEAD:                                  # the song starts here: there is no time before it, so the first vowel waits for its consonants
            lead = min(0.2, 0.07 * len(ss[0]['on']))
            if lead:
                ss = [dict(ss[0], t=ss[0]['t'] + lead)] + ss[1:]
                ns = [dict(ns[0], t=ns[0]['t'] + lead, d=ns[0]['d'] - lead)] + ns[1:]
        y, pre, rep = phrase(V, ns, ss, a)
        at = int(round((ns[0]['t'] - pre) * V.sr)); src = max(0, -at); at = max(0, at); m = min(len(y) - src, len(out) - at)
        if m > 0:
            out[at:at + m] += y[src:src + m]
        devs += rep['dev']; log.append((ns[0]['t'] - pre, rep['pitch']))
        print('  %5.1f s  %s' % (t0, ' '.join(p for p in rep['ph'] if p != 'SP')[:100]), flush=True)
    pk = float(np.abs(out).max())
    if pk > 0:
        out *= 0.89 / pk
    base = a.out or re.sub(r'\s*notes$', '', os.path.splitext(a.midi)[0]) + ' sung.wav'
    w = wave.open(base, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(V.sr); w.writeframes((out * 32767).astype('<i2').tobytes()); w.close()
    print('Sung %d notes, %.0f seconds of song, in %.0f seconds.' % (len(notes), total, time.time() - t_start))
    if devs:
        print('Before centring, the voice sat %.0f cents from the exact notes on average (largest %.0f).' % (sum(devs) / len(devs), max(devs)))
    if snd.unknown:
        print('Words in no dictionary, read letter by letter (check how they sound): ' + ', '.join(sorted(set(snd.unknown))))
    print('Saved: ' + base)
    if os.environ.get('SING_DEBUG'):                   # the pitch line that was asked for, to compare with what a pitch meter hears
        np.savez(os.path.splitext(base)[0] + '.pitch.npz', t=np.array([x[0] for x in log]), **{'p%d' % i: x[1] for i, x in enumerate(log)})
    if sys.platform == 'darwin':
        m4a = os.path.splitext(base)[0] + '.m4a'
        if subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', '128000', base, m4a], capture_output=True).returncode == 0:
            print('Saved: ' + m4a + '  (smaller, for the phone)')


if __name__ == '__main__':
    main()
