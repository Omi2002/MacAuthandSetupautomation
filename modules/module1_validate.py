"""Module 1 - detect the installed Firefox and JDK and decide what to do."""
import os
import platform
import shutil
import subprocess

IS_WINDOWS = platform.system() == "Windows"


def version_matches(installed, supported):
    """'50.0.1' matches '50.0' (same release line); '139.0.4' and '50.1' do not."""
    if not installed:
        return False
    return installed == supported or installed.startswith(supported + ".")


def check_firefox():
    """Returns (installed: bool, version: str or None)"""
    if IS_WINDOWS:
        candidates = [r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",   # 32-bit Firefox 50 goes here
                      r"C:\Program Files\Mozilla Firefox\firefox.exe"]
        path = next((p for p in candidates if os.path.exists(p)), None)
    else:
        path = shutil.which("firefox")
    if not path:
        return False, None
    try:
        out = subprocess.check_output([path, "--version"], stderr=subprocess.STDOUT).decode().strip()
        return True, out.split()[-1]                    # "Mozilla Firefox 50.0.1" -> "50.0.1"
    except Exception:
        return True, None


def check_jdk():
    """Returns (installed: bool, version: str or None, java_home: str or None)"""
    java_home = os.environ.get("JAVA_HOME")
    java_exe = None
    if java_home:                                       # trust JAVA_HOME before PATH
        candidate = os.path.join(java_home, "bin", "java.exe" if IS_WINDOWS else "java")
        if os.path.exists(candidate):
            java_exe = candidate
    if not java_exe:
        java_exe = shutil.which("java")
    if not java_exe or not os.path.exists(java_exe):
        return False, None, java_home
    try:
        result = subprocess.run([java_exe, "-version"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        line = result.stderr.decode(errors="ignore").splitlines()[0]
        return True, line.split('"')[1], java_home      # 'java version "1.8.0_161"' -> "1.8.0_161"
    except Exception:
        return True, None, java_home


def validate_environment():
    from config import SUPPORTED_FIREFOX_VERSION, SUPPORTED_JDK_VERSIONS

    ff_installed, ff_version = check_firefox()
    jdk_installed, jdk_version, java_home = check_jdk()

    ff_ok = ff_installed and version_matches(ff_version, SUPPORTED_FIREFOX_VERSION)
    ff_action = None if ff_ok else ("install" if not ff_installed else "upgrade")

    jdk_ok = jdk_installed and any(version_matches(jdk_version, v) for v in SUPPORTED_JDK_VERSIONS)
    jdk_action = None if jdk_ok else ("install" if not jdk_installed else "upgrade")

    return {
        "firefox": {"installed": ff_installed, "version": ff_version, "ok": ff_ok, "action": ff_action},
        "jdk": {"installed": jdk_installed, "version": jdk_version, "java_home": java_home,
                "ok": jdk_ok, "action": jdk_action},
    }
