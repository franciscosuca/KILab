#!/usr/bin/env python3
"""Print the text of an Apple Pages (.pages) document. Usage: pages_text.py <file.pages>
Decodes Index/Document.iwa (snappy-framed protobuf) and prints the longest readable text runs.
Also: `unzip -p file.pages preview.jpg > preview.jpg` gives a page preview image."""
import re, sys, zipfile


def snappy(b: bytes) -> bytes:
    i = 0
    while b[i] & 0x80:  # skip varint uncompressed length
        i += 1
    i += 1
    out = bytearray()
    while i < len(b):
        t = b[i]; i += 1; k = t & 3
        if k == 0:
            n = t >> 2
            if n >= 60:
                nb = n - 59; n = int.from_bytes(b[i:i + nb], "little"); i += nb
            n += 1
            out += b[i:i + n]; i += n
        else:
            if k == 1:
                n = ((t >> 2) & 7) + 4; off = ((t >> 5) << 8) | b[i]; i += 1
            elif k == 2:
                n = (t >> 2) + 1; off = int.from_bytes(b[i:i + 2], "little"); i += 2
            else:
                n = (t >> 2) + 1; off = int.from_bytes(b[i:i + 4], "little"); i += 4
            for _ in range(n):
                out.append(out[-off])
    return bytes(out)


def main(path: str):
    d = zipfile.ZipFile(path).read("Index/Document.iwa")
    p, raw = 0, b""
    while p < len(d):
        n = int.from_bytes(d[p + 1:p + 4], "little"); p += 4
        raw += snappy(d[p:p + n]); p += n
    for m in re.finditer(rb"(?:[\x20-\x7e\n\t]|[\xc2-\xf4][\x80-\xbf]+){40,}", raw):
        txt = m.group().decode("utf8", "replace")
        if len(set(txt)) > 12:  # drop binary noise
            print(txt)


if __name__ == "__main__":
    main(sys.argv[1]) if len(sys.argv) == 2 else sys.exit(__doc__)
