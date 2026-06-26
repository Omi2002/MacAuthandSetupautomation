import subprocess, shutil, os, platform

def check_firefox():
    """Returns (installed: bool, version: str or None)"""
    # Windows: check registry path
    if platform.system() == "Windows":
        path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    else:
        path = shutil.which("firefox")

    if not path or not os.path.exists(path):
        return False, None

    try:
        out = subprocess.check_output(
            [path, "--version"], stderr=subprocess.STDOUT
        ).decode().strip()
        # Output: "Mozilla Firefox 50.0"
        version = out.split()[-1]
        return True, version
    except Exception:
        return True, None


def check_jdk():
    """Returns (installed: bool, version: str or None, java_home: str or None)"""
    java_home = os.environ.get("JAVA_HOME")
    java_exe  = shutil.which("java")

    if not java_exe and java_home:
        java_exe = os.path.join(java_home, "bin", "java")

    if not java_exe or not os.path.exists(java_exe):
        return False, None, java_home

    try:
        # java -version prints to stderr
        result = subprocess.run(
            [java_exe, "-version"],
            stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        version_line = result.stderr.decode().splitlines()[0]
        # e.g. 'java version "1.8.0_202"'
        version = version_line.split('"')[1]   # "1.8.0_202"
        return True, version, java_home
    except Exception:
        return True, None, java_home


def validate_environment():
    """
    Returns dict with validation status for both Firefox and JDK.
    Also returns flags indicating what Module 2 needs to do.
    """
    from config import SUPPORTED_FIREFOX_VERSION, SUPPORTED_JDK_VERSIONS

    ff_installed, ff_version = check_firefox()
    jdk_installed, jdk_version, java_home = check_jdk()

    # Firefox check
    ff_ok = ff_installed and ff_version == SUPPORTED_FIREFOX_VERSION
    ff_action = None
    if not ff_installed:
        ff_action = "install"
    elif ff_version != SUPPORTED_FIREFOX_VERSION:
        ff_action = "upgrade"  # or "downgrade" if higher

    # JDK check — version starts with 1.7 or 1.8
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