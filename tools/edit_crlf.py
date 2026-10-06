"""Exact string replacement that preserves CRLF line endings.

    python3 tools/edit_crlf.py FILE  (reads JSON [[old, new], ...] on stdin)
Each `old` must occur exactly once (written with \n; matched against the
file with its \r\n converted).
"""
import json, sys
path = sys.argv[1]
raw = open(path, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")
for old, new in json.load(sys.stdin):
    n = text.count(old)
    if n != 1:
        sys.exit(f"{path}: expected 1 match, found {n}: {old[:70]!r}")
    text = text.replace(old, new)
open(path, "wb").write((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
print("edited", path)
