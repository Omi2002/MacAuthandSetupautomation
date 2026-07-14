import subprocess, os, platform, glob
from config import FIREFOX_INSTALLER_PATH, JDK_INSTALLER_PATH

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
        print("⚠️  JDK 8 folder not found anywhere — JAVA_HOME not set.")
        return

    print(f"Found JDK 8 at: {jdk_path}")

    # Set machine-wide JAVA_HOME
    subprocess.run(["setx", "JAVA_HOME", jdk_path, "/M"], check=True)

    # Prepend JDK 8 bin to PATH so it wins over Oracle redirector and JDK 17/21
    jdk_bin = os.path.join(jdk_path, "bin")
    current_path = os.environ.get("PATH", "")
    subprocess.run(
        ["setx", "PATH", f"{jdk_bin};{current_path}", "/M"],
        check=True
    )

    # Update current process immediately so Module 3 sees it without new terminal
    os.environ["JAVA_HOME"] = jdk_path
    os.environ["PATH"] = f"{jdk_bin};{current_path}"

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