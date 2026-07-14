import subprocess, shutil, os, platform

def check_firefox():
    """Returns (installed: bool, version: str or None)"""
    if platform.system() == "Windows":
        # Check both 64-bit and 32-bit install locations
        candidates = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ]
        path = next((p for p in candidates if os.path.exists(p)), None)
    else:
        path = shutil.which("firefox")

    if not path:
        return False, None

    try:
        out = subprocess.check_output(
            [path, "--version"], stderr=subprocess.STDOUT
        ).decode().strip()
        version = out.split()[-1]   # "Mozilla Firefox 50.0" → "50.0"
        return True, version
    except Exception:
        return True, None   # exists but version unreadable


def check_jdk():
    """Returns (installed: bool, version: str or None, java_home: str or None)"""
    java_home = os.environ.get("JAVA_HOME")

    # Prefer JAVA_HOME-based java.exe — avoids picking up JDK 17/21 from PATH
    java_exe = None
    if java_home:
        candidate = os.path.join(
            java_home, "bin",
            "java.exe" if platform.system() == "Windows" else "java"
        )
        if os.path.exists(candidate):
            java_exe = candidate

    # Fallback: scan PATH
    if not java_exe:
        java_exe = shutil.which("java")

    if not java_exe or not os.path.exists(java_exe):
        return False, None, java_home

    try:
        result = subprocess.run(
            [java_exe, "-version"],
            stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        version_line = result.stderr.decode().splitlines()[0]
        version = version_line.split('"')[1]   # 'java version "1.8.0_161"' → "1.8.0_161"
        return True, version, java_home
    except Exception:
        return True, None, java_home


def validate_environment():
    from config import SUPPORTED_FIREFOX_VERSION, SUPPORTED_JDK_VERSIONS

    ff_installed, ff_version       = check_firefox()
    jdk_installed, jdk_version, java_home = check_jdk()

    ff_ok = ff_installed and ff_version == SUPPORTED_FIREFOX_VERSION
    ff_action = None
    if not ff_installed:
        ff_action = "install"
    elif not ff_ok:
        ff_action = "upgrade"

    jdk_ok = False
    if jdk_installed and jdk_version:
        for v in SUPPORTED_JDK_VERSIONS:
            if jdk_version.startswith(v):
                jdk_ok = True
                break

    jdk_action = None
    if not jdk_installed:
        jdk_action = "install"
    elif not jdk_ok:
        jdk_action = "upgrade"

    return {
        "firefox": {"installed": ff_installed, "version": ff_version,
                    "ok": ff_ok, "action": ff_action},
        "jdk":     {"installed": jdk_installed, "version": jdk_version,
                    "java_home": java_home, "ok": jdk_ok, "action": jdk_action},
    }