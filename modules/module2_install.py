import subprocess, os
from config import FIREFOX_INSTALLER_PATH, JDK_INSTALLER_PATH

def install_firefox():
    if not os.path.exists(FIREFOX_INSTALLER_PATH):
        raise FileNotFoundError(f"Installer not found: {FIREFOX_INSTALLER_PATH}")
    subprocess.run([FIREFOX_INSTALLER_PATH, "/S"], check=True)  # /S = silent install

def install_jdk():
    if not os.path.exists(JDK_INSTALLER_PATH):
        raise FileNotFoundError(f"Installer not found: {JDK_INSTALLER_PATH}")
    subprocess.run([JDK_INSTALLER_PATH, "/s"], check=True)  # silent flag varies by installer

def run_installations(validation_result):
    """Calls install functions only where Module 1 flagged an action."""
    ff = validation_result["firefox"]
    jdk = validation_result["jdk"]

    if ff["action"] in ("install", "upgrade"):
        print(f"Firefox action required: {ff['action']}")
        install_firefox()

    if jdk["action"] in ("install", "upgrade"):
        print(f"JDK action required: {jdk['action']}")
        install_jdk()