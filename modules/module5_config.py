"""
Module 5 - Configuration creation and machine identification.

Everything the client / connected support person needs to decide is asked
interactively. Press Enter to accept the value shown in [brackets].
"""
import datetime
import ipaddress
import json
import os
import platform
import re
import socket
import subprocess
import uuid

import config as cfg
from modules.config_file import write_config, read_config

IS_WINDOWS = platform.system() == "Windows"


def _cfg(name, default):
    return getattr(cfg, name, default)


# ── defaults (all can be overridden in config.py) ────────────────────────────
def _default_server_ip():   return _cfg("DEFAULT_SERVER_IP", "202.54.101.10")
def _default_drive():       return _cfg("DEFAULT_LOCAL_DRIVE", "D:\\")
def _default_app_url():     return _cfg("DEDICATED_APP_URL", "https://netwinv2uat.netwincbs.in:15344")
def _output_dir():          return _cfg("CONFIG_OUTPUT_DIR", os.path.join(_cfg("LOG_DIR", "."), "output"))
def _jar():                 return _cfg("CONFIG_CREATOR_JAR", "")
def _sample_dat():          return _cfg("CONFIG_SAMPLE_DAT",
                                        os.path.join(os.path.dirname(_jar()), "config.dat"))
def _deploy_props():
    return _cfg("JAVA_DEPLOY_PROPS", os.path.join(
        os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", "Sun", "Java",
        "Deployment", "deployment.properties"))


# ── input helpers ────────────────────────────────────────────────────────────

def ask(label, default=None, validator=None):
    """Prompt with an editable default. Enter = accept the default."""
    while True:
        hint = f" [{default}]" if default else ""
        value = input(f"  {label}{hint}: ").strip()
        if not value and default is not None:
            value = default
        if not value:
            print("     This value is required.")
            continue
        if validator:
            error = validator(value)
            if error:
                print(f"     {error}")
                continue
        return value


def _v_code(v):
    return None if re.fullmatch(r"[A-Za-z0-9_-]{1,20}", v) else "Use letters, digits, - or _ only (max 20)."


def _v_ip(v):
    try:
        ipaddress.ip_address(v)
        return None
    except ValueError:
        return "Enter a valid IP address, e.g. 192.168.1.10"


def _v_url(v):
    return None if re.fullmatch(r"https?://[^\s/]+(:\d+)?(/\S*)?", v) else "Enter a full URL, e.g. https://host:15344"


def normalize_drive(v):
    """'d', 'D:', 'D:\\' -> 'D:\\'   (returns None if not a drive)"""
    m = re.fullmatch(r"([A-Za-z]):?[\\/]?", v.strip())
    return f"{m.group(1).upper()}:\\" if m else None


def _v_drive(v):
    return None if normalize_drive(v) else "Enter a drive letter such as D or D:\\"


def get_system_ip():
    """Auto-detect this PC's IPv4 address (user can edit it)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))           # no traffic is sent, only picks the route
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
            return "" if ip.startswith("127.") else ip
        except Exception:
            return ""


def collect_inputs():
    """Ask for every value. Returns a dict; loops until the user confirms."""
    while True:
        print("\n  ── Client configuration (Enter = accept value in [ ]) ───────")
        bank = ask("Customer (Bank) Code", validator=_v_code).upper()
        branch = ask("Branch Code", validator=_v_code).upper()
        system_ip = ask("System IP (auto-detected, editable)",
                        default=get_system_ip() or None, validator=_v_ip)
        server_ip = ask("Server IP", default=_default_server_ip(), validator=_v_ip)
        local_ip = ask("Local Server IP", default=server_ip, validator=_v_ip)
        drive = normalize_drive(ask("Local Drive", default=_default_drive(), validator=_v_drive))
        app_url = ask("Application URL (for Java exception list)",
                      default=_default_app_url(), validator=_v_url)
        out_dir = ask("Save config file in folder", default=_output_dir())

        print("\n  ── Please confirm ───────────────────────────────────────────")
        print(f"  Customer (Bank) Code : {bank}")
        print(f"  Branch Code          : {branch}")
        print(f"  System IP            : {system_ip}")
        print(f"  Server IP            : {server_ip}")
        print(f"  Local Server IP      : {local_ip}")
        print(f"  Local Drive          : {drive}   (common path {drive}{bank}\\{branch})")
        print(f"  Application URL      : {app_url}")
        print(f"  Config file          : {os.path.join(out_dir, f'config_{branch}.dat')}")
        if IS_WINDOWS and not os.path.exists(drive):
            print(f"  NOTE: drive {drive} does not exist on this PC.")
        if input("\n  Proceed with these values? [Y/n]: ").strip().lower() in ("", "y", "yes"):
            return {"bank": bank, "branch": branch, "system_ip": system_ip,
                    "server_ip": server_ip, "local_ip": local_ip, "drive": drive,
                    "app_url": app_url, "out_dir": out_dir}


# ── Java deployment.properties helpers ───────────────────────────────────────

def _read_props(path):
    props = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f.read().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, v = line.split("=", 1)
                    props[k.strip()] = v.strip()
    return props


def _set_props(path, updates):
    """Replace existing keys or append new ones; every other line is kept."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
    pending, out = dict(updates), []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line else None
        if key in pending:
            out.append(f"{key}={pending.pop(key)}")
        else:
            out.append(line)
    out += [f"{k}={v}" for k, v in pending.items()]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def _java_escape(path):
    return path.replace("\\", "\\\\").replace(":", "\\:")


def _java_unescape(value):
    return value.replace("\\:", ":").replace("\\\\", "\\")


def add_java_security_exception(url):
    """Add the application URL to Java's Exception Site List."""
    try:
        props_path = _deploy_props()
        key = "deployment.user.security.exception.sites"
        existing = _read_props(props_path).get(key)
        if existing:
            sites_file = _java_unescape(existing)
        else:
            sites_file = os.path.join(os.path.dirname(props_path), "security", "exception.sites")
            _set_props(props_path, {key: _java_escape(sites_file)})

        os.makedirs(os.path.dirname(sites_file), exist_ok=True)
        current = []
        if os.path.exists(sites_file):
            with open(sites_file, "r", encoding="utf-8", errors="ignore") as f:
                current = [l.strip() for l in f.read().splitlines() if l.strip()]
        if url.rstrip("/") in [c.rstrip("/") for c in current]:
            print("  ✓ URL already in Java Exception Site List.")
        else:
            current.append(url)
            with open(sites_file, "w", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(current) + "\n")
            print(f"  ✓ Added to Java Exception Site List: {url}")
        return True
    except Exception as e:
        print(f"  ⚠️  Could not update Java Exception Site List: {e}")
        return False


def enable_java_console():
    try:
        _set_props(_deploy_props(), {
            "deployment.console.startup.mode": "SHOW",
            "deployment.trace": "true",
            "deployment.log": "true",
        })
        print("  ✓ Java Console enabled.")
        return True
    except Exception as e:
        print(f"  ⚠️  Could not enable Java Console: {e}")
        return False


# ── Firefox auto-update ──────────────────────────────────────────────────────

def disable_firefox_autoupdate():
    """Needs Administrator rights (writes into the Firefox install folder)."""
    try:
        ff_dir = next((d for d in (r"C:\Program Files (x86)\Mozilla Firefox",
                                   r"C:\Program Files\Mozilla Firefox") if os.path.exists(d)), None)
        if not ff_dir:
            print("  ⚠️  Firefox folder not found - skipping auto-update disable.")
            return False
        with open(os.path.join(ff_dir, "mozilla.cfg"), "w") as f:
            f.write('// CBS V2 setup - auto update disabled\n'
                    'lockPref("app.update.auto", false);\n'
                    'lockPref("app.update.enabled", false);\n'
                    'lockPref("app.update.silent", false);\n')
        pref_dir = os.path.join(ff_dir, "defaults", "pref")
        os.makedirs(pref_dir, exist_ok=True)
        with open(os.path.join(pref_dir, "local-settings.js"), "w") as f:
            f.write('pref("general.config.obscure_value", 0);\n'
                    'pref("general.config.filename", "mozilla.cfg");\n')
        print("  ✓ Firefox auto-update disabled.")
        return True
    except PermissionError:
        print("  ⚠️  Permission denied - run as Administrator.")
        return False
    except Exception as e:
        print(f"  ⚠️  Could not disable Firefox auto-update: {e}")
        return False


# ── config file ──────────────────────────────────────────────────────────────

def create_config_file(v):
    """Generate config_<Branch>.dat from the entered values and verify it."""
    try:
        path, key = write_config(v["out_dir"], v["bank"], v["branch"], v["server_ip"],
                                 v["local_ip"], v["drive"], _jar(), _sample_dat())
        stored = read_config(path, key)
        expected = {"branch": v["branch"], "branch.server.ip": v["server_ip"],
                    "local.server.ip": v["local_ip"],
                    "common_path": f"{v['drive']}{v['bank']}\\{v['branch']}"}
        if stored != expected:
            print("  ⚠️  Config file written but verification failed.")
            return None
        print(f"  ✓ Config file created and verified: {path}")
        return path
    except Exception as e:
        print(f"  ⚠️  Could not create config file: {e}")
        return None


# ── machine details (informational) ──────────────────────────────────────────

def _ps(command):
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", command],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def capture_machine_ids(system_ip):
    mac = ":".join(f"{(uuid.getnode() >> i) & 0xff:02X}" for i in range(40, -8, -8))
    ids = {"SYSTEM_IP": system_ip, "MAC_ID": mac, "HARDDISK_ID": "N/A", "PROCESSOR_ID": "N/A"}
    if IS_WINDOWS:
        ids["HARDDISK_ID"] = _ps("(Get-CimInstance Win32_DiskDrive | Select -First 1).SerialNumber")
        ids["PROCESSOR_ID"] = _ps("(Get-CimInstance Win32_Processor | Select -First 1).ProcessorId")
    for k, val in ids.items():
        print(f"  {k:<13}: {val}")
    return ids


def _write_log(inputs, results):
    try:
        entry = {"timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                 "machine": socket.gethostname(), "user": os.environ.get("USERNAME", ""),
                 "inputs": inputs, "results": results}
        with open(os.path.join(_cfg("LOG_DIR", "."), "cbs_module5.log"), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# ── entry point ──────────────────────────────────────────────────────────────

def run_module5():
    print("\n  [Module 5] Configuration & Machine Identification")
    v = collect_inputs()
    results = {"firefox_autoupdate": False, "java_exception_url": False,
               "java_console": False, "config_file": None, "machine_ids": {}}

    print("\n  [Step 1] Firefox auto-update");   results["firefox_autoupdate"] = disable_firefox_autoupdate()
    print("\n  [Step 2] Java exception site");   results["java_exception_url"] = add_java_security_exception(v["app_url"])
    print("\n  [Step 3] Java console");          results["java_console"] = enable_java_console()
    print("\n  [Step 4] Config file");           results["config_file"] = create_config_file(v)
    print("\n  [Step 5] Machine details");       results["machine_ids"] = capture_machine_ids(v["system_ip"])

    _write_log(v, results)
    ok = (results["firefox_autoupdate"] and results["java_exception_url"]
          and results["java_console"] and results["config_file"] is not None)
    print("\n  ✅ Module 5 complete." if ok else "\n  ⚠️  Module 5 finished with warnings (see ⚠️ above).")
    return ok, results
