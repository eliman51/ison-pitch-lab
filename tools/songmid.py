#!/usr/bin/env python3
"""A built-in chant from the app -> a notes file (MIDI with words) that tools/sing.py can sing.

    python3 tools/songmid.py song-ourfather "Our Father notes.mid" [--shift -17] [--bpm 60]

The chant is read straight out of index.html, so the app's own notes are the only copy: the SONGS entry gives the
typed melody (Note:beats:word, the notation explained above parseTyped) and its beats a minute. --shift moves every
note by that many half steps, which is how a melody written for the choir's soprano is put where a man sings it.

The words are turned into what the singer wants (see "A real singing voice" in CLAUDE.md): the whole word on its
first note, + on the word's next syllable, - on a note the word is held over. So "Fa- ther," becomes Father and +,
and a note with no word of its own becomes -.
"""
import argparse, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, '..', 'index.html')
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def typed(song):
    """-> (the typed melody, beats a minute) of a built-in chant, read out of index.html"""
    s = open(APP, encoding='utf-8').read()
    m = re.search(r"'%s'\s*:\s*\{text:([A-Z_0-9]+),bpm:(\d+)" % re.escape(song), s)
    if not m:
        sys.exit('No built-in chant called "%s" in index.html.' % song)
    name, bpm = m.group(1), int(m.group(2))
    d = re.search(r"\nconst %s=\s*\n?((?:\s*'(?:[^'\\]|\\.)*'\s*\+?\s*)+);" % name, s)
    if not d:
        sys.exit('Could not read the notes of %s.' % name)
    parts = re.findall(r"'((?:[^'\\]|\\.)*)'", d.group(1))
    return ''.join(p.replace("\\'", "'") for p in parts), bpm


def notes(text, bpm, shift):
    out, t = [], 0.0
    beat = 60.0 / bpm
    for tok in text.split():
        p = tok.split(':')
        nm, b = p[0], p[1] if len(p) > 1 else '1'
        w = ':'.join(p[2:]) if len(p) > 2 else ''
        beats = float(b) if b else 1.0
        if nm.lower() == 'r':
            t += beats * beat; continue
        mm = re.match(r'^([A-Ga-g])([#b]?)(-?\d+)$', nm)
        if not mm:
            sys.exit('Could not read the note "%s".' % nm)
        midi = (int(mm.group(3)) + 1) * 12 + STEP[mm.group(1).upper()] + (1 if mm.group(2) == '#' else -1 if mm.group(2) == 'b' else 0)
        out.append(dict(t=t, d=beats * beat, m=midi + shift, w=w))
        t += beats * beat
    return out


def lyrics(ns):
    """the app's syllables -> the singer's words: a whole word, + for its next syllable, - for a held note"""
    i = 0
    while i < len(ns):
        w = ns[i]['w']
        if not w:
            ns[i]['ly'] = '-'; i += 1; continue
        # gather this word: syllables that end in a hyphen carry on into the next one
        parts, j = [w], i
        while ns[j]['w'].endswith('-') and j + 1 < len(ns):
            k = j + 1
            while k < len(ns) and not ns[k]['w']:
                k += 1
            if k >= len(ns) or not ns[k]['w']:
                break
            parts.append(ns[k]['w']); j = k
        word = re.sub(r"[^A-Za-z']", '', ''.join(parts))
        ns[i]['ly'] = word or 'la'
        for q in range(i + 1, j + 1):
            ns[q]['ly'] = '+' if ns[q]['w'] else '-'
        i = j + 1
    return ns


def vlq(v):
    b = [v & 127]; v >>= 7
    while v:
        b.append((v & 127) | 128); v >>= 7
    return bytes(reversed(b))


def write(ns, path, bpm, div=480):
    ev = []
    tick = lambda s: int(round(s * bpm / 60.0 * div))
    for n in ns:
        a, z = tick(n['t']), max(tick(n['t']) + 1, tick(n['t'] + n['d'] * 0.98))
        ev.append((a, 0, b'\xff\x05' + vlq(len(n['ly'].encode())) + n['ly'].encode()))
        ev.append((a, 1, bytes([0x90, int(round(n['m'])), 90])))
        ev.append((z, 2, bytes([0x80, int(round(n['m'])), 0])))
    cents = ','.join(str(int(round((n['m'] - round(n['m'])) * 100))) for n in ns).encode()
    body = b'\x00\xff\x51\x03' + struct.pack('>I', int(6e7 / bpm))[1:]
    body += b'\x00\xff\x7f' + vlq(len(b'\x7dison1:' + cents)) + b'\x7dison1:' + cents
    ev.sort(key=lambda x: (x[0], x[1]))
    last = 0
    for tk, _o, data in ev:
        body += vlq(tk - last) + data; last = tk
    body += vlq(240) + b'\xff\x2f\x00'
    head = b'MThd' + struct.pack('>IHHH', 6, 0, 1, div)
    open(path, 'wb').write(head + b'MTrk' + struct.pack('>I', len(body)) + body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('song'); ap.add_argument('out')
    ap.add_argument('--shift', type=int, default=0, help='move every note this many half steps')
    ap.add_argument('--bpm', type=float, default=0, help='override the chant\'s own beats a minute')
    a = ap.parse_args()
    text, bpm = typed(a.song)
    bpm = a.bpm or bpm
    ns = lyrics(notes(text, bpm, a.shift))
    write(ns, a.out, bpm)
    lo, hi = min(n['m'] for n in ns), max(n['m'] for n in ns)
    nm = lambda m: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][int(m) % 12] + str(int(m) // 12 - 1)
    print('%s: %d notes, %.0f seconds, %s to %s, %g a minute' % (a.song, len(ns), ns[-1]['t'] + ns[-1]['d'], nm(lo), nm(hi), bpm))
    print('words: ' + ' '.join((n['ly'] if n['ly'] not in '+-' else n['ly']) for n in ns[:14]) + ' ...')
    print('saved ' + a.out)


main()
