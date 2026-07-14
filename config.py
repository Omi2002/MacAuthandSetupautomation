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