import os, subprocess, socket, platform, uuid
import winreg
from config import (
    CONFIG_CREATOR_JAR, CONFIG_CREATOR_DIR, CONFIG_OUTPUT_PATH,
    DEDICATED_APP_URL, FIREFOX_AUTOCONFIG_PATH, JAVA_DEPLOY_PROPS
)

# ── Helper: get machine details ───────────────────────────────

def get_system_ip():
    """Get local machine IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())


def get_mac_id():
    """Get MAC address of primary network adapter."""
    try:
        result = subprocess.run(
            ["getmac", "/fo", "csv", "/nh"],
            capture_output=True, text=True
        )
        line = result.stdout.strip().splitlines()[0]
        mac = line.split(",")[0].strip().strip('"').replace("-", ":")
        return mac
    except Exception:
        # Fallback using uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                        for i in range(0, 48, 8)][::-1])
        return mac


def get_harddisk_id():
    """Get primary hard disk serial number."""
    try:
        result = subprocess.run(
            ["wmic", "diskdrive", "get", "SerialNumber"],
            capture_output=True, text=True
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines()
                 if l.strip() and "SerialNumber" not in l]
        return lines[0] if lines else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def get_processor_id():
    """Get CPU processor ID."""
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "ProcessorId"],
            capture_output=True, text=True
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines()
                 if l.strip() and "ProcessorId" not in l]
        return lines[0] if lines else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


# ── Step 1: Get user inputs ───────────────────────────────────

def get_client_inputs():
    """Prompt user for Customer Code and Branch Code."""
    print()
    print("  ── Client Configuration Input ──────────────────────")
    customer_code = input("  Enter Customer Code : ").strip().upper()
    branch_code   = input("  Enter Branch Code   : ").strip().upper()

    if not customer_code:
        raise ValueError("Customer Code cannot be empty.")
    if not branch_code:
        raise ValueError("Branch Code cannot be empty.")

    return customer_code, branch_code


# ── Step 2: Disable Firefox Auto Update ──────────────────────

def disable_firefox_autoupdate():
    """
    Disable Firefox auto-update by creating autoconfig files
    in the Firefox installation directory.
    """
    try:
        ff_dirs = [
            r"C:\Program Files (x86)\Mozilla Firefox",
            r"C:\Program Files\Mozilla Firefox"
        ]

        ff_dir = next((d for d in ff_dirs if os.path.exists(d)), None)
        if not ff_dir:
            print("  ⚠️  Firefox directory not found — skipping auto-update disable.")
            return False

        # 1. Create mozilla.cfg in Firefox root
        cfg_path = os.path.join(ff_dir, "mozilla.cfg")
        cfg_content = (
            "// Mozilla config - Auto update disabled by CBS V2 Setup\n"
            'lockPref("app.update.auto", false);\n'
            'lockPref("app.update.enabled", false);\n'
            'lockPref("app.update.silent", false);\n'
        )
        with open(cfg_path, "w") as f:
            f.write(cfg_content)

        # 2. Create local-settings.js in defaults/pref
        pref_dir = os.path.join(ff_dir, "defaults", "pref")
        os.makedirs(pref_dir, exist_ok=True)
        local_settings_path = os.path.join(pref_dir, "local-settings.js")
        local_settings_content = (
            'pref("general.config.obscure_value", 0);\n'
            'pref("general.config.filename", "mozilla.cfg");\n'
        )
        with open(local_settings_path, "w") as f:
            f.write(local_settings_content)

        print("  ✓ Firefox auto-update disabled.")
        return True

    except Exception as e:
        print(f"  ⚠️  Could not disable Firefox auto-update: {e}")
        return False


# ── Step 3: Add URL to Java Security Exception List ──────────

def add_java_security_exception(url):
    """Add application URL to Java Security Exception Site List."""
    try:
        deploy_dir = os.path.dirname(JAVA_DEPLOY_PROPS)
        os.makedirs(deploy_dir, exist_ok=True)

        # Read existing properties
        existing = ""
        if os.path.exists(JAVA_DEPLOY_PROPS):
            with open(JAVA_DEPLOY_PROPS, "r") as f:
                existing = f.read()

        # Add exception site list property if not present
        exception_file = os.path.join(deploy_dir, "exception.sites")

        if "deployment.user.security.exception.sites" not in existing:
            with open(JAVA_DEPLOY_PROPS, "a") as f:
                f.write(f"\ndeployment.user.security.exception.sites="
                        f"{exception_file.replace(chr(92), '/')}\n")

        # Write URL to exception.sites file
        existing_sites = ""
        if os.path.exists(exception_file):
            with open(exception_file, "r") as f:
                existing_sites = f.read()

        if url not in existing_sites and url != "http://PLACEHOLDER_URL":
            with open(exception_file, "a") as f:
                f.write(f"\n{url}\n")
            print(f"  ✓ URL added to Java Security Exception List.")
        elif url == "http://PLACEHOLDER_URL":
            print("  ⏳ App URL not configured yet — skipping exception list.")
        else:
            print("  ✓ URL already in Java Security Exception List.")

        return True

    except Exception as e:
        print(f"  ⚠️  Could not update Java Security Exception List: {e}")
        return False


# ── Step 4: Enable Java Console ──────────────────────────────

def enable_java_console():
    """Enable Java console via deployment.properties."""
    try:
        deploy_dir = os.path.dirname(JAVA_DEPLOY_PROPS)
        os.makedirs(deploy_dir, exist_ok=True)

        existing = ""
        if os.path.exists(JAVA_DEPLOY_PROPS):
            with open(JAVA_DEPLOY_PROPS, "r") as f:
                existing = f.read()

        changes = {
            "deployment.console.startup.mode": "SHOW",
            "deployment.trace":                "true",
            "deployment.log":                  "true",
        }

        for key, value in changes.items():
            if key not in existing:
                with open(JAVA_DEPLOY_PROPS, "a") as f:
                    f.write(f"\n{key}={value}\n")

        print("  ✓ Java Console settings enabled.")
        return True

    except Exception as e:
        print(f"  ⚠️  Could not enable Java Console: {e}")
        return False


# ── Step 5: Launch Config Creator ────────────────────────────

def launch_config_creator(customer_code, branch_code, system_ip):
    """
    Launch Config Creator JAR.
    User fills in the form and clicks Create.
    Script waits for config file to be generated on D drive.
    """
    if not os.path.exists(CONFIG_CREATOR_JAR):
        raise FileNotFoundError(
            f"Config Creator JAR not found: {CONFIG_CREATOR_JAR}"
        )

    java_exe = _find_java()
    if not java_exe:
        raise EnvironmentError("Java not found. Run Modules 1-3 first.")

    print()
    print("  ── Config Creator ──────────────────────────────────")
    print(f"  Customer Code : {customer_code}")
    print(f"  Branch Code   : {branch_code}")
    print(f"  System IP     : {system_ip}")
    print()
    print("  Opening Config Creator application...")
    print("  Please fill in the form and click CREATE.")
    print("  Config file will be saved to D:\\ drive.")
    print()

    # Launch the JAR
    subprocess.Popen(
        [java_exe, "-jar", CONFIG_CREATOR_JAR],
        cwd=CONFIG_CREATOR_DIR
    )

    # Wait for user to complete and config file to appear
    import time
    print("  Waiting for config file to be generated on D:\\ ...")
    timeout = 120   # 2 minutes
    elapsed = 0
    while elapsed < timeout:
        # Check for any config_*.dat file on D drive
        try:
            files = [f for f in os.listdir("D:\\")
                     if f.startswith("config_") and f.endswith(".dat")]
            if files:
                config_file = os.path.join("D:\\", files[0])
                print(f"  ✓ Config file detected: {config_file}")
                return config_file
        except Exception:
            pass
        time.sleep(3)
        elapsed += 3
        print(f"  Still waiting... ({elapsed}s)", end="\r")

    print("\n  ⚠️  Config file not detected after 2 minutes.")
    return None


def _find_java():
    """Find java.exe from JAVA_HOME or PATH."""
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidate = os.path.join(java_home, "bin", "java.exe")
        if os.path.exists(candidate):
            return candidate

    import shutil
    return shutil.which("java")


# ── Step 6: Capture Machine IDs ──────────────────────────────

def capture_machine_ids():
    """Collect all machine identifiers."""
    print("  Collecting machine identifiers...")
    ids = {
        "MAC_ID":       get_mac_id(),
        "HARDDISK_ID":  get_harddisk_id(),
        "PROCESSOR_ID": get_processor_id(),
        "SYSTEM_IP":    get_system_ip(),
    }
    for k, v in ids.items():
        print(f"  {k:<14}: {v}")
    return ids


# ── Main Module 5 Entry Point ─────────────────────────────────

def run_module5():
    """Full Module 5 execution."""
    print("\n  [Module 5] Configuration & Machine Identification...")
    print()

    results = {
        "customer_code":         None,
        "branch_code":           None,
        "system_ip":             None,
        "firefox_autoupdate":    False,
        "java_exception_url":    False,
        "java_console":          False,
        "config_file_generated": False,
        "machine_ids":           {},
    }

    # ── Step 1: Get inputs
    try:
        customer_code, branch_code = get_client_inputs()
        system_ip = get_system_ip()
        results["customer_code"] = customer_code
        results["branch_code"]   = branch_code
        results["system_ip"]     = system_ip
        print(f"  ✓ System IP auto-detected: {system_ip}")
    except ValueError as e:
        print(f"  ❌ Input error: {e}")
        return False, results

    # ── Step 2: Disable Firefox auto-update
    print()
    print("  [Step 2] Disabling Firefox auto-update...")
    results["firefox_autoupdate"] = disable_firefox_autoupdate()

    # ── Step 3: Java Security Exception URL
    print()
    print("  [Step 3] Configuring Java Security Exception URL...")
    results["java_exception_url"] = add_java_security_exception(DEDICATED_APP_URL)

    # ── Step 4: Java Console
    print()
    print("  [Step 4] Enabling Java Console settings...")
    results["java_console"] = enable_java_console()

    # ── Step 5: Launch Config Creator
    print()
    print("  [Step 5] Launching Config Creator...")
    config_file = launch_config_creator(customer_code, branch_code, system_ip)
    results["config_file_generated"] = config_file is not None

    # ── Step 6: Machine IDs
    print()
    print("  [Step 6] Capturing machine identifiers...")
    results["machine_ids"] = capture_machine_ids()

    # ── Summary
    print()
    all_ok = (
        results["firefox_autoupdate"] and
        results["java_console"] and
        results["config_file_generated"]
    )

    if all_ok:
        print("  ✅ Module 5 complete.")
    else:
        print("  ⚠️  Module 5 completed with some warnings.")
        print("      Check items marked ⚠️ above.")

    return all_ok, results