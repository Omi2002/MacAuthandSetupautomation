import os

# Base directory of the installer project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")

SUPPORTED_FIREFOX_VERSION = "50.0.1"
SUPPORTED_JDK_VERSIONS    = ["1.7", "1.8"]

# Local installer paths (instead of internal-repo URLs)
FIREFOX_INSTALLER_PATH = os.path.join(RESOURCES_DIR, "Firefox Setup 50.0.1.exe")
JDK_INSTALLER_PATH = os.path.join(RESOURCES_DIR, "jdk-8u161-windows-i586.exe")

LOG_FILE_PATH = "cbs_setup.log"

# ── Module 5 — Config Creator ─────────────────────────────────
CONFIG_CREATOR_DIR     = os.path.join(RESOURCES_DIR, "Config_Creator")
CONFIG_CREATOR_JAR     = os.path.join(CONFIG_CREATOR_DIR, "configFileCreator.jar")
CONFIG_OUTPUT_DRIVE    = "D:\\"                          # config file saved here
CONFIG_OUTPUT_PATH     = os.path.join(CONFIG_OUTPUT_DRIVE, "config_cbs.dat")

# Dedicated Application URL — update once known
DEDICATED_APP_URL      = "http://PLACEHOLDER_URL"        # ← fill in later

# Firefox auto-update config path
FIREFOX_AUTOCONFIG_PATH = os.path.join(
    os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
    "Mozilla Firefox", "defaults", "pref"
)

# Java deployment properties path
JAVA_DEPLOY_PROPS = os.path.join(
    os.environ.get("USERPROFILE", ""),
    "AppData", "LocalLow", "Sun", "Java", "Deployment", "deployment.properties"
)