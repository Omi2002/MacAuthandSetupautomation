from modules.module1_validate import validate_environment, check_firefox, check_jdk
from modules.module2_install  import run_installations
from modules.module3_verify   import final_verify
import os, platform

def main():
    print("=== CBS V2 Auto Authentication Setup ===\n")
    print(f"Platform: {platform.system()}")
    print(f"JAVA_HOME at startup: {os.environ.get('JAVA_HOME', 'NOT SET')}")
    print()

    # ── Module 1 ──────────────────────────────────────────────────
    print("[Module 1] Checking environment...")
    validation = validate_environment()

    ff  = validation["firefox"]
    jdk = validation["jdk"]

    print(f"  Firefox installed : {ff['installed']}")
    print(f"  Firefox version   : {ff['version']}")
    print(f"  Firefox ok        : {ff['ok']}")
    print(f"  Firefox action    : {ff['action']}")
    print()
    print(f"  JDK installed     : {jdk['installed']}")
    print(f"  JDK version       : {jdk['version']}")
    print(f"  JDK ok            : {jdk['ok']}")
    print(f"  JDK action        : {jdk['action']}")
    print(f"  JAVA_HOME         : {jdk['java_home']}")
    print()

    # ── Firefox path probe ────────────────────────────────────────
    ff_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ]
    print("Firefox path probe:")
    for p in ff_paths:
        print(f"  {p} → exists={os.path.exists(p)}")
    print()

    # ── JDK path probe ────────────────────────────────────────────
    import glob, shutil
    print("JDK path probe:")
    print(f"  shutil.which('java') → {shutil.which('java')}")
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidate = os.path.join(java_home, "bin", "java.exe")
        print(f"  JAVA_HOME candidate → {candidate} exists={os.path.exists(candidate)}")
    jdk8_matches = glob.glob(r"C:\Program Files\Java\jdk1.8*")
    print(f"  JDK 8 folders found → {jdk8_matches}")
    print()

    # ── Module 2 ──────────────────────────────────────────────────
    needs_install = not ff["ok"] or not jdk["ok"]
    if needs_install:
        print("[Module 2] Running auto-installation...")
        run_installations(validation)
    else:
        print("[Module 2] No installation needed.")

    print()

    # ── Post-install probe ────────────────────────────────────────
    print("Post-install environment check:")
    print(f"  JAVA_HOME now     : {os.environ.get('JAVA_HOME', 'NOT SET')}")
    print(f"  java via which    : {shutil.which('java')}")
    for p in ff_paths:
        print(f"  {p} → exists={os.path.exists(p)}")
    print()

    # ── Module 3 ──────────────────────────────────────────────────
    print("[Module 3] Final verification...")
    passed, _ = final_verify()

    if passed:
        print("\n✅ Setup complete. Ready for CBS V2 authentication.")
    else:
        print("\n❌ Setup incomplete. Please check the log and retry.")
        exit(1)

if __name__ == "__main__":
    main()