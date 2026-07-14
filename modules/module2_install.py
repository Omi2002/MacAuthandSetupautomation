import subprocess, os, platform
from config import FIREFOX_INSTALLER_PATH, JDK_INSTALLER_PATH

# ── Firefox ────────────────────────────────────────────────────────────────────

def install_firefox():
    if not os.path.exists(FIREFOX_INSTALLER_PATH):
        raise FileNotFoundError(f"Installer not found: {FIREFOX_INSTALLER_PATH}")

    # Kill any running Firefox before silent install — otherwise NSIS no-ops silently
    subprocess.run(["taskkill", "/F", "/IM", "firefox.exe"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run([FIREFOX_INSTALLER_PATH, "/S"], check=True)
    print("Firefox installation complete.")

# ── JDK ────────────────────────────────────────────────────────────────────────

def install_jdk():
    if not os.path.exists(JDK_INSTALLER_PATH):
        raise FileNotFoundError(f"Installer not found: {JDK_INSTALLER_PATH}")

    subprocess.run([JDK_INSTALLER_PATH, "/s"], check=True)
    _set_java_home_windows()
    print("JDK installation complete.")


def _set_java_home_windows():
    """Set JAVA_HOME and prepend JDK bin to PATH so it wins over older JDKs."""
    jdk_path = r"C:\Program Files\Java\jdk1.8.0_161"

    # Confirm the folder actually exists after install
    if not os.path.exists(jdk_path):
        # Fallback: scan for any jdk1.8* folder in Program Files
        import glob
        matches = glob.glob(r"C:\Program Files\Java\jdk1.8*")
        if not matches:
            print("⚠️  JDK 8 install folder not found — JAVA_HOME not set.")
            return
        jdk_path = matches[0]

    # Set machine-wide JAVA_HOME
    subprocess.run(["setx", "JAVA_HOME", jdk_path, "/M"], check=True)

    # Prepend JDK bin to system PATH so it takes priority over jdk-17/jdk-21
    new_path_entry = os.path.join(jdk_path, "bin")
    current_path = os.environ.get("PATH", "")
    subprocess.run(
        ["setx", "PATH", f"{new_path_entry};{current_path}", "/M"],
        check=True
    )

    # Also update current process environment so Module 3 sees it immediately
    os.environ["JAVA_HOME"] = jdk_path
    os.environ["PATH"] = f"{new_path_entry};{current_path}"

    print(f"JAVA_HOME set to: {jdk_path}")

# ── Entry point ────────────────────────────────────────────────────────────────

def run_installations(validation_result):
    """Calls install functions only where Module 1 flagged an action."""
    ff  = validation_result["firefox"]
    jdk = validation_result["jdk"]

    if ff["action"] in ("install", "upgrade"):
        print(f"Firefox action required: {ff['action']}")
        install_firefox()

    if jdk["action"] in ("install", "upgrade"):
        print(f"JDK action required: {jdk['action']}")
        install_jdk()