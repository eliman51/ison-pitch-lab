#!/usr/bin/env python3
"""Pack finished Psalm 118 songs for the app: python3 tools/pack118.py <folder with s118-N.json and s118-N.m4a> <passphrase> [prefix]
prefix s118 (default) = the 22 finished songs; prefix r118 = the review set (JSON from window.isonSongRec: notes, words, contour).
Each s118/N.bin is locked (see tools/lock.py) and holds: 4 bytes = length of the JSON, the JSON {name,text,set,dur}, the recording."""
import json, os, struct, subprocess, sys, tempfile
src, pw = sys.argv[1:3]; pre = sys.argv[3] if len(sys.argv) > 3 else 's118'
here = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(here, '..', pre); os.makedirs(out, exist_ok=True)
for n in range(1, 23):
    j, a = os.path.join(src, '%s-%d.json' % (pre, n)), os.path.join(src, '%s-%d.m4a' % (pre, n))
    if not (os.path.exists(j) and os.path.exists(a)):
        continue
    J = json.load(open(j, encoding='utf-8')); J.pop('notes', None) if not isinstance(J.get('notes'), list) else None
    jb = json.dumps(J, ensure_ascii=False).encode()
    t = tempfile.mktemp(); open(t, 'wb').write(struct.pack('>I', len(jb)) + jb + open(a, 'rb').read())
    subprocess.run([sys.executable, '-I', os.path.join(here, 'lock.py'), t, os.path.join(out, '%d.bin' % n), pw], check=True, capture_output=True); os.remove(t)
    print('packed stanza', n, J.get('name', pre), J.get('dur'))
