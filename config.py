import os
import sys

# ── Folders ───────────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):                       # running as the built .exe
    BUNDLE_DIR = sys._MEIPASS                           # files packed inside the exe (read-only, temporary)
    APP_DIR = os.path.dirname(sys.executable)           # folder the .exe sits in (logs / output go here)
else:                                                   # running as python main.py
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BUNDLE_DIR

BASE_DIR = BUNDLE_DIR                                   # kept for older code
RESOURCES_DIR = os.path.join(BUNDLE_DIR, "resources")
LOG_DIR = APP_DIR

# ── Supported versions (Modules 1-3) ──────────────────────────────────────────
SUPPORTED_FIREFOX_VERSION = "50.0"
SUPPORTED_JDK_VERSIONS = ["1.7", "1.8"]

FIREFOX_INSTALLER_PATH = os.path.join(RESOURCES_DIR, "Firefox Setup 50.0.1.exe")
JDK_INSTALLER_PATH = os.path.join(RESOURCES_DIR, "jdk-8u161-windows-i586.exe")
LOG_FILE_PATH = os.path.join(LOG_DIR, "cbs_setup.log")

# ── Module 5 (defaults shown at the prompts - the user can edit every one) ────
CONFIG_CREATOR_DIR = os.path.join(RESOURCES_DIR, "Config_Creator")
CONFIG_CREATOR_JAR = os.path.join(CONFIG_CREATOR_DIR, "configFileCreator.jar")
CONFIG_OUTPUT_DIR = os.path.join(APP_DIR, "output")

DEDICATED_APP_URL = "https://netwinv2uat.netwincbs.in:15344"   # confirm the production URL
DEFAULT_SERVER_IP = "202.54.101.10"
DEFAULT_LOCAL_DRIVE = "D:\\"
