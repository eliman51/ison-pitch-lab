#!/usr/bin/env python3
"""Make sure every script in index.html still parses (needs node). Run before every push."""
import os, re, subprocess, sys, tempfile
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(root, 'index.html'), encoding='utf8').read()
ok = True
for n, (a, c) in enumerate(re.findall(r'<script(\s[^>]*)?>(.*?)</script>', html, re.S)):
    a = a or ''
    t = re.search(r'type=["\']?([^"\'\s>]+)', a)
    if 'src=' in a or not c.strip() or (t and t.group(1) not in ('module', 'text/javascript', 'application/javascript')):
        continue
    f = tempfile.NamedTemporaryFile('w', suffix='.mjs' if 'module' in a else '.js', delete=False, encoding='utf8')
    f.write(c); f.close()
    r = subprocess.run(['node', '--check', f.name], capture_output=True, text=True); os.unlink(f.name)
    if r.returncode:
        ok = False; print(f'script {n + 1}: SYNTAX ERROR\n{r.stderr}')
print('OK: every script parses' if ok else 'FAILED: do not push')
sys.exit(0 if ok else 1)
