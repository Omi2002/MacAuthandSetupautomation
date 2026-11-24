"""
Creates the encrypted config_<Branch>.dat file in the same format as
Config Creator (configFileCreator.jar).

The encryption key is read from the bundled JAR at run time (and verified
against the bundled sample config.dat), so it is not stored in our source.
Requires: pip install pycryptodome
"""
import base64
import os
import struct
import zipfile

from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad

# keys written to the file, in the order Config Creator writes them
KEY_BRANCH = "branch"
KEY_SERVER_IP = "branch.server.ip"
KEY_LOCAL_IP = "local.server.ip"
KEY_COMMON_PATH = "common_path"


# ── key discovery ────────────────────────────────────────────────────────────

def _utf8_constants(data):
    """Minimal Java .class constant-pool reader: returns all string constants."""
    pos = 8
    count = struct.unpack(">H", data[pos:pos + 2])[0]
    pos += 2
    out, i = [], 1
    while i < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            n = struct.unpack(">H", data[pos:pos + 2])[0]
            pos += 2
            out.append(data[pos:pos + n].decode("utf-8", "ignore"))
            pos += n
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            pos += 4
        elif tag in (5, 6):
            pos += 8
            i += 1
        elif tag in (7, 8, 16, 19, 20):
            pos += 2
        elif tag == 15:
            pos += 3
        else:
            raise ValueError(f"Unknown constant tag {tag}")
        i += 1
    return out


def _cipher(key_text):
    return DES3.new(key_text.encode("utf-8")[:24], DES3.MODE_ECB)


def _enc(text, key_text):
    raw = _cipher(key_text).encrypt(pad(text.encode("utf-8"), 8))
    return base64.b64encode(raw).decode("ascii")


def _dec(b64, key_text):
    raw = _cipher(key_text).decrypt(base64.b64decode(b64))
    return unpad(raw, 8).decode("utf-8")


def find_key(jar_path, sample_dat_path):
    """Find the key in the JAR and prove it using the bundled sample config.dat."""
    with open(sample_dat_path, "r", errors="ignore") as f:
        first = next(l for l in f.read().splitlines() if ";;" in l)
    sample_key_enc = first.split(";;")[0]            # encrypted text of 'branch'

    with zipfile.ZipFile(jar_path) as z:
        for name in z.namelist():
            if not name.endswith(".class"):
                continue
            for cand in _utf8_constants(z.read(name)):
                if len(cand) >= 24 and cand.isascii():
                    try:
                        if _dec(sample_key_enc, cand) == KEY_BRANCH:
                            return cand
                    except Exception:
                        continue
    raise RuntimeError("Could not verify the Config Creator key from the bundled JAR.")


# ── build / write / verify ───────────────────────────────────────────────────

def common_path(drive, bank_code, branch_code):
    """drive is like 'D:\\' -> 'D:\\MAHESH\\MBR02'"""
    return f"{drive}{bank_code}\\{branch_code}"


def build_lines(bank_code, branch_code, server_ip, local_server_ip, drive, key_text):
    pairs = [
        (KEY_BRANCH, branch_code),
        (KEY_SERVER_IP, server_ip),
        (KEY_LOCAL_IP, local_server_ip),
        (KEY_COMMON_PATH, common_path(drive, bank_code, branch_code)),
    ]
    return [f"{_enc(k, key_text)};;{_enc(v, key_text)}" for k, v in pairs]


def write_config(out_dir, bank_code, branch_code, server_ip, local_server_ip,
                 drive, jar_path, sample_dat_path):
    """Writes <out_dir>/config_<branch>.dat and returns its full path."""
    key_text = find_key(jar_path, sample_dat_path)
    lines = build_lines(bank_code, branch_code, server_ip, local_server_ip, drive, key_text)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"config_{branch_code}.dat")
    with open(out_path, "w", newline="") as f:      # same layout as Config Creator
        f.write("\r\n" + "\r\n".join(lines))
    return out_path, key_text


def read_config(path, key_text):
    values = {}
    with open(path, "r", errors="ignore") as f:
        for line in f.read().splitlines():
            if ";;" in line:
                k, v = line.split(";;")
                values[_dec(k, key_text)] = _dec(v, key_text)
    return values
