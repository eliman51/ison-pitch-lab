#!/usr/bin/env python3
"""Make the Claude artifact copy of the app from index.html.

The GitHub site (index.html) is the real app. The artifact copy is the same page with the
artifact's own <head> (tools/artifact-head.html) in place of the site's head lines, and
without the site's final newline. Output: dist/artifact/index.html (+ the mp3 files).

  python3 tools/artifact.py
"""
import os, re, shutil
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
page = open(os.path.join(root, 'index.html'), 'rb').read()
head = open(os.path.join(root, 'tools', 'artifact-head.html'), 'rb').read().rstrip(b'\n')
end = page.index(b'</head><body>\n') + len(b'</head><body>\n')
body = page[end:]
assert body.endswith(b'</body></html>\n'), 'index.html must end with </body></html>'
out = head + b'\n' + body[:-len(b'</body></html>\n')] + b'\n</body></html>'
d = os.path.join(root, 'dist', 'artifact'); os.makedirs(d, exist_ok=True)
open(os.path.join(d, 'index.html'), 'wb').write(out)
for f in os.listdir(root):
    if f.endswith('.mp3'):
        shutil.copy2(os.path.join(root, f), d)
print(f'built dist/artifact/index.html ({len(out):,} bytes)')
