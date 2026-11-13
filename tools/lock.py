#!/usr/bin/env python3
"""Lock a private file so it can sit in this public repository: python3 tools/lock.py <in> <out.bin> <passphrase>
Same format the app's unlockPriv reads: "ISN1", 16 bytes salt, 12 bytes iv, AES-256-GCM (key: PBKDF2-SHA256, 150000 rounds)."""
import os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
src, dst, pw = sys.argv[1:4]
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=150000).derive(pw.strip().encode())
open(dst, 'wb').write(b'ISN1' + salt + iv + AESGCM(key).encrypt(iv, open(src, 'rb').read(), None))
print('locked', dst)
