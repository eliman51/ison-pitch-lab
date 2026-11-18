#!/usr/bin/env python3
"""Write a stanza on the Psalm 23 (Tone 3) melody shape by shape; this turns it into a score for tools/heart.py.

    python3 tools/shapes.py <stanza.s.txt> <stanza.txt>      then      heart.py <stanza.txt> N <out> --unit 0.25 --home 51 --scale p23 --set r118p --sing

The nine shapes (A B C D E H I F G, see CLAUDE.md) are the singer's own, measured from the recording: each is a row of
cells, a cell being the notes he puts on one syllable. A line of the shape score names a shape and lays the words on it:

    A   My/c1 soul/c2 ear/c3-nest/c4-ly/0:1 longs/c5 for/c6a Your/c6b sal/c7*.7-va/c8-tion/c9 |
    D!  tes/r-ti/q-mo/c1a-nies/c1b of/c2 Your/c3 mouth/c4

  c3        all the notes of cell 3            c6a c6b c4cd   only that note (a = first) or those notes of the cell
  c8+c9     two cells on one syllable          *.7            that cell a little shorter (or longer)
  r q h     a recited home note: 2, 1 or 1.5 units           anything else is a note written out as heart.py reads it
  ~x        a silence. The singer's own lifts and breaths are put in by themselves after the cell that carries them,
            unless a ~ is written there (write ~0 for none). When the cell ends in the middle of a word the lift is
            left out, unless the file has the line  #! singer-pauses  (then every pause is the singer's own, measured,
            a word is broken where his melody pauses, as he breaks "shep-herd" and "bri-dal", and a shorter pause
            written by hand inside a shape gives way to his); list/c7~1 writes such a lift by hand, list/c7~0 forbids it
  D!        the last close of a stanza (longer, no breath after). Fs is the climb F with one syllable to a note.
  nan/c9-   a word that runs on into the next shape; the next line then starts with  -ces/c1
  |         end of a line of the words (for reading)         # a comment         {t1.06} and the like pass through

  B@1.2     that whole line 1.2 times slower (rarely the right cure: a crowded line wants another shape, and the tool
            says so when a line runs quicker than 2.3 syllables a second).

Loud and soft follow the singer: H soft, B and D a little soft, the rest level. It warns when a syllable is shorter
than 0.8 unit (a fifth of a second), when a cell of the shape was left out, and when two shapes are joined in a way the
singer never joins them. It also writes <stanza.txt>.form, the shapes with their syllable counts (A9 B5 ...).
"""
import re, sys

S = {
    'A': [[(-4, 2.4)], [(-4, 2.2)], [(0, 2)], [(0, 1.8)], [(-1, 1.2), (0, 1)], [(-2, 1.1), (-1, 1)], [(0, 2.5)], [(1, .9), (0, 1.2)], [(-1, 1.9), (-2, 1.1)]],
    'B': [[(-1, 1.8)], [(-2, 1.1), (-1, 1)], [(0, .8), (1, .4), (0, .6), (-1, 1.6)], [(-2, 1), (-3, 1.05), (-2, .95), (-1, .8)], [(-4, 2.6)]],
    'C': [[(0, 1.8)], [(1, 1.1), (0, .8)], [(-1, 2.3)], [(0, 2.1), (1, 1)], [(1, .7), (2, .8), (1, 1.6)], [(0, 1.4)], [(0, 2.2)], [(-1, .8), (0, .9)], [(0, 2.1)]],
    'D': [[(1, 1.8), (0, .85)], [(-1, 2.2)], [(2, .4), (1, 1.2)], [(0, 2.2), (1, .75), (-1, 1.1), (0, 1.75)]],
    'E': [[(-2, 2)], [(-1, 2.2)], [(0, 1.8)], [(0, 2.1)], [(0, 1.1), (2, .7)], [(1, 1.05), (0, .8)], [(-1, .8), (-2, 1.1)]],
    'H': [[(-1, 1.8)], [(0, .85), (-1, .8)], [(-2, .85), (-3, 1)], [(-2, 1.9), (-1, .7)], [(-2, .9), (-1, .75)], [(-2, .6), (-3, .55), (-4, 1.3)], [(-4, 1.8)]],
    'I': [[(-1, .8), (0, 3)], [(1, 1.8), (0, .85)], [(-1, 2.2)], [(2, .35), (1, .9), (0, .5)], [(0, 1.5)], [(-1, .8), (0, 1)], [(0, 2)]],
    'F': [[(-2, 2)], [(-1, .65), (-2, .35), (-1, 1)], [(0, 1.1), (1, .65)], [(0, 1.1), (1, 1)], [(2, 1), (3, 1.3)]],
    'Fs': [[(-2, 1.8)], [(-1, 1.1)], [(-2, .8)], [(-1, 1)], [(0, .9)], [(1, 1.4)], [(0, .8)], [(0, .6), (1, .9)], [(2, 1), (3, 1.3)]],
    'G': [[(2, .85), (1, .75)], [(0, 1.75)], [(1, .8), (2, 1.9), (1, 1.45)], [(0, 2)], [(1, 2)], [(2, 1.5)], [(2, .8), (0, 1.2)], [(0, 2)]],
}
REST = {'A': {7: 1.2, 9: .5}, 'B': {3: .6, 5: 2.2}, 'C': {4: 1, 9: .3}, 'D': {1: 1.2, 4: 2.2}, 'E': {7: .3}, 'H': {4: 1, 7: 2.2}, 'I': {2: 1, 7: .3}, 'F': {}, 'Fs': {}, 'G': {2: .4, 6: .5, 8: .3}}
# the singer's pauses exactly as measured (18 November 2026), in quarter seconds, used when the file has the line  #! singer-pauses :
# after A's held home note 0.38 s every time (twice inside a word: shep-herd, e-nemies) and 0.3 s after A; nothing after B's
# turn (be-fore, a-noint are sung through); in C 0.21 s after cell 4 and 0.24 s after cell 7; in D 0.35 s after the +1 0
# every time (fol-low, bri-dal) and half a second after the close; in H 0.37 s after cell 4; in I 0.27 s after cell 2 and
# 0.18 s after cell 5; in G 0.2 s after cells 2 and 6 (com-fort); none in E or F
REST2 = {'A': {7: 1.45, 9: 1.0}, 'B': {5: 2.0}, 'C': {4: .8, 7: .9, 9: .3}, 'D': {1: 1.3, 4: 2.0}, 'E': {7: .2}, 'H': {4: 1.4, 7: 2.0},
         'I': {2: 1.0, 5: .7, 7: .5}, 'F': {}, 'Fs': {}, 'G': {2: .6, 6: .7, 8: .3}}
SOMETIMES = {('G', 2)}                                   # a pause he makes only some of the time: ~0 after it is obeyed
LOUD = {'A': 'mf', 'B': 'mp', 'C': 'mf', 'D': 'mp', 'E': 'mf', 'H': 'p', 'I': 'mf', 'F': 'mf', 'Fs': 'mf', 'G': 'mf'}
JOIN = {'A': 'B', 'B': 'AC', 'C': 'D', 'D': 'AEF', 'E': 'H', 'H': 'I', 'I': 'D', 'F': 'G', 'G': 'D'}
PICKUP = {'B': [(-2, 1)]}                                 # c0
SHORT = {'r': [(0, 2)], 'q': [(0, 1)], 'h': [(0, 1.5)]}
fm = lambda x: ('%.2f' % x).rstrip('0').rstrip('.')


def main():
    src, dst = sys.argv[1:3]; out = []; warn = 0; form = []; carry = None; tempo = 1.0
    FAST = 2.3                                           # syllables a second: a line quicker than this is called crowded
    fmt = lambda syls: '-'.join(x[0] + '/' + '_'.join('%d:%s' % (d, fm(u)) for d, u in x[1]) + ('~' + fm(x[2]) if x[2] else '') for x in syls)
    INWORD = any(l.startswith('#! singer-pauses') for l in open(src, encoding='utf-8'))
    for ln, line in enumerate(open(src, encoding='utf-8'), 1):
        raw = line.rstrip('\n'); body = raw.split('#')[0].split()
        if not body:
            out.append(raw); continue
        if body[0][0] == '{':
            for t in body:
                if re.fullmatch(r'\{t\d*\.?\d+\}', t):
                    tempo = float(t[2:-1])
            out.append(raw); continue
        sh, _, force = body[0].partition('@'); final = sh.endswith('!'); sh = sh.rstrip('!')
        if sh not in S:
            sys.exit('line %d: no shape called "%s"' % (ln, sh))
        cells = [list(c) for c in S[sh]]; rest = dict((REST2 if INWORD else REST)[sh])
        if final:
            cells[-1] = [(0, 3), (1, .75), (-1, 1.35), (0, 2.8)]; rest.pop(len(cells), None)
        used = set(); toks = body[1:]; items = []; nsyl = 0           # items: ['w', syllables, head, tail] | ['r', units] | ['|']
        his = 0                                          # the singer's pause after the cell just sung, when it is one he always makes
        for ti, tok in enumerate(toks):
            if tok == '|':
                items.append(['|']); continue
            if tok[0] == '~':
                r = max(float(tok[1:]), his) if INWORD else float(tok[1:])      # his pause wins over a shorter one written by hand
                if r:
                    items.append(['r', r])
                his = 0; continue
            his = 0
            head = tok.startswith('-'); tail = tok.endswith('-'); tok = tok.strip('-')      # a word that runs over from one shape into the next:  nan/c9-   then   -ces/c1
            parts = re.split(r'-(?=[A-Za-z])', tok); word = []; pend = None; lastk = None; nsyl += len(parts)
            for pi, p in enumerate(parts):
                if '/' not in p:
                    sys.exit('line %d: no notes on "%s"' % (ln, p))
                syl, spec = p.split('/', 1); notes = []; pend = None
                spec, tilde, own = spec.partition('~')         # list/c7~1 : a lift written by hand after this syllable
                for q in spec.split('+'):
                    m = re.fullmatch(r'c(\d)([a-d]*)(?:\*(\d*\.?\d+))?', q)
                    if m:
                        k = int(m.group(1)); c = PICKUP.get(sh) if k == 0 else (cells[k - 1] if 1 <= k <= len(cells) else None)
                        if c is None:
                            sys.exit('line %d: shape %s has no cell %d' % (ln, sh, k))
                        idx = ['abcd'.index(ch) for ch in m.group(2)] or list(range(len(c)))
                        if max(idx) >= len(c):
                            sys.exit('line %d: cell %d of %s has only %d notes' % (ln, k, sh, len(c)))
                        f = float(m.group(3)) if m.group(3) else 1.0
                        notes += [(c[i][0], c[i][1] * f) for i in idx]; used.add(k)
                        pend = rest.get(k) if idx[-1] == len(c) - 1 else None; lastk = k
                    elif q in SHORT:
                        notes += SHORT[q]; pend = None
                    else:
                        for z in q.split('_'):
                            m2 = re.fullmatch(r"(-?\d+)(?::(\d*\.?\d+))?", z)
                            if not m2:
                                sys.exit('line %d: cannot read "%s" in "%s"' % (ln, z, tok))
                            notes.append((int(m2.group(1)), float(m2.group(2) or 1)))
                        pend = None
                inside = pi < len(parts) - 1 or tail            # the melody's lift falls inside the word: the singer lifts there all the same
                word.append([syl, notes, float(own) if tilde else (pend if (INWORD and inside and pend) else 0)])
                if tilde:
                    pend = None
            items.append(['w', word, head, tail])
            his = pend if (pend and lastk is not None and lastk < len(cells) and (sh, lastk) not in SOMETIMES) else 0
            nxt = toks[ti + 1] if ti + 1 < len(toks) else ''
            if pend and not nxt.startswith('~') and not tail:
                items.append(['r', pend])
        # a crowded line is slowed down: its notes and the lifts inside it, not the breath after it
        last = max([i for i, it in enumerate(items) if it[0] == 'w'], default=-1)
        units = sum(u for it in items[:last + 1] if it[0] == 'w' for _, n, _r in it[1] for _, u in n) + sum(it[1] for it in items[:last + 1] if it[0] == 'r') + sum(x[2] for it in items[:last + 1] if it[0] == 'w' for x in it[1])
        rate = nsyl / (units * 0.25 * tempo) if units else 0
        f = float(force) if force else 1.0              # only when asked: crowding is cured by giving the words another shape, not by slowing down
        if not force and rate > FAST:
            print('line %d (%s): %d syllables in %.1f s is crowded; give it another shape' % (ln, sh, nsyl, units * 0.25 * tempo))
        if f != 1.0:
            for i, it in enumerate(items[:last + 1]):
                if it[0] == 'w':
                    it[1] = [[s_, [(d, u * f) for d, u in n], r_ * f] for s_, n, r_ in it[1]]
                elif it[0] == 'r':
                    it[1] *= f
            if not force:
                print('line %d (%s, %d syllables): slowed %.2f times' % (ln, sh, nsyl, f))
        res = ['{%s}' % LOUD[sh]]
        for it in items:
            if it[0] == '|':
                res.append('|'); continue
            if it[0] == 'r':
                res.append('~' + fm(it[1])); continue
            _, word, head, tail = it
            for syl, notes, _r in word:
                if sum(u for _, u in notes) < 0.8:
                    print('line %d: "%s" is very short (%s units)' % (ln, syl, fm(sum(u for _, u in notes)))); warn += 1
            if head != (carry is not None):
                sys.exit('line %d: a word carried over needs "-" at the end of one line and at the start of the next' % ln)
            w = fmt(word)
            if head:
                w = carry + '-' + w; carry = None
            if tail:
                carry = w; continue
            res.append(w)
        miss = [k for k in range(1, len(cells) + 1) if k not in used]
        if miss:
            print('line %d (%s): cells left out: %s' % (ln, sh, ' '.join(map(str, miss))))
        out.append(' '.join(res)); form.append('%s%d' % (sh[0], nsyl))
    open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n'); open(dst + '.form', 'w').write(' '.join(form) + '\n')
    seq = [f[0] for f in form]                           # only joins the singer himself makes
    for x, y in zip(seq, seq[1:]):
        if y not in JOIN[x]:
            print('join %s to %s is not one the singer makes' % (x, y))
    if seq and (seq[0] != 'A' or seq[-1] != 'D'):
        print('a stanza starts on A and ends on D; this one runs %s ... %s' % (seq[0], seq[-1]))
    print('Wrote %s%s' % (dst, ' (%d warnings)' % warn if warn else ''))


if __name__ == '__main__':
    main()
