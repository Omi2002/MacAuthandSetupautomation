import subprocess, os, platform, glob
from config import FIREFOX_INSTALLER_PATH, JDK_INSTALLER_PATH

import winreg, ctypes
ENV_KEY = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
def install_firefox():
    if not os.path.exists(FIREFOX_INSTALLER_PATH):
        raise FileNotFoundError(f"Installer not found: {FIREFOX_INSTALLER_PATH}")

    # Kill running Firefox first — NSIS silent install no-ops if Firefox is running
    subprocess.run(["taskkill", "/F", "/IM", "firefox.exe"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run([FIREFOX_INSTALLER_PATH, "/S"], check=True)
    print("Firefox installation complete.")


def install_jdk():
    if not os.path.exists(JDK_INSTALLER_PATH):
        raise FileNotFoundError(f"Installer not found: {JDK_INSTALLER_PATH}")

    subprocess.run([JDK_INSTALLER_PATH, "/s"], check=True)
    _set_java_home_windows()
    print("JDK installation complete.")


def _find_jdk8_path():
    """Scan all common locations for any JDK 1.8 installation."""
    search_patterns = [
        r"C:\Program Files\Java\jdk1.8*",
        r"C:\Program Files (x86)\Java\jdk1.8*",
        r"C:\Program Files\OpenLogic\jdk-8*",        # OpenLogic JDK 8
        r"C:\Program Files\Eclipse Adoptium\jdk-8*", # Adoptium/Temurin JDK 8
        r"C:\Program Files\Microsoft\jdk-8*",         # Microsoft JDK 8
    ]
    for pattern in search_patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return None


def _set_java_home_windows():
    jdk_path = _find_jdk8_path()
    if not jdk_path:
        print("JDK 8 folder not found - JAVA_HOME not set.")
        return
    jdk_bin = os.path.join(jdk_path, "bin")
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ENV_KEY, 0,
                         winreg.KEY_READ | winreg.KEY_WRITE)
    winreg.SetValueEx(key, "JAVA_HOME", 0, winreg.REG_SZ, jdk_path)
    current, _ = winreg.QueryValueEx(key, "Path")
    parts = [p for p in current.split(";")
             if p and p.lower().rstrip("\\") != jdk_bin.lower().rstrip("\\")]
    parts.insert(0, jdk_bin)
    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(parts))
    winreg.CloseKey(key)
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x1A, 0, "Environment", 2, 5000, None)
    os.environ["JAVA_HOME"] = jdk_path
    os.environ["PATH"] = jdk_bin + ";" + os.environ.get("PATH", "")
    print(f"JAVA_HOME set to: {jdk_path}")

def run_installations(validation_result):
    ff  = validation_result["firefox"]
    jdk = validation_result["jdk"]

    if ff["action"] in ("install", "upgrade"):
        print(f"Firefox action required: {ff['action']}")
        install_firefox()

    if jdk["action"] in ("install", "upgrade"):
        print(f"JDK action required: {jdk['action']}")
        install_jdk()

    # Always attempt to set JAVA_HOME if it's missing,
    # even if JDK action was None (already installed but HOME not set)
    if not os.environ.get("JAVA_HOME"):
        print("JAVA_HOME not set — attempting to locate and set JDK 8...")
        _set_java_home_windows()