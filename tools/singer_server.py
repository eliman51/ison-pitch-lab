#!/usr/bin/env python3
"""The singer, waiting on this Mac for the app to ask: the app's "Sing it with the real singer" button sends the
song's notes and words here and gets the sung recording back. Only this computer can reach it (127.0.0.1).

    ~/ison-singer/venv/bin/python -I tools/singer_server.py        (or double-click "Start the singer" in ~/ison-singer)
"""
import http.server, os, subprocess, sys, tempfile, threading

BUSY = threading.Lock()   # one song at a time; a second request waits its turn, and a quick 'are you there' is always answered

PORT = 8765
ALLOW = ('https://eliman51.github.io', 'http://127.0.0.1:8766', 'http://localhost:8766')
SING = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sing.py')


class H(http.server.BaseHTTPRequestHandler):
    def cors(self):
        o = self.headers.get('Origin', '')
        if o in ALLOW:
            self.send_header('Access-Control-Allow-Origin', o)
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Private-Network', 'true')

    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()

    def do_GET(self):
        self.send_response(200); self.cors(); self.send_header('Content-Type', 'text/plain'); self.end_headers(); self.wfile.write(b'singer busy' if BUSY.locked() else b'singer ready')

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        if self.headers.get('Origin', '') not in ALLOW or not 0 < n < 2_000_000:
            self.send_response(403); self.end_headers(); return
        d = tempfile.mkdtemp(); mid = os.path.join(d, 'song notes.mid'); open(mid, 'wb').write(self.rfile.read(n))
        print('Singing a song of %d bytes of notes...' % n, flush=True)
        with BUSY:
            r = subprocess.run([sys.executable, '-I', SING, mid], capture_output=True, text=True, cwd='/')
        out = os.path.join(d, 'song sung.m4a')
        if r.returncode or not os.path.exists(out):
            print(r.stdout[-400:], r.stderr[-800:], flush=True)
            self.send_response(500); self.cors(); self.end_headers(); self.wfile.write((r.stderr or 'failed')[-300:].encode()); return
        b = open(out, 'rb').read(); print(r.stdout.strip().split('\n')[-3], flush=True)
        self.send_response(200); self.cors(); self.send_header('Content-Type', 'audio/mp4'); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)

    def log_message(self, *a):
        pass


print('The singer is ready. Leave this window open while you use the app in this Mac\'s browser. Close it to stop.', flush=True)
http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
