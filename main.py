from modules.module1_validate import validate_environment
from modules.module2_install  import run_installations
from modules.module3_verify   import final_verify

def main():
    print("=== CBS V2 Auto Authentication Setup ===\n")

    # Module 1 — validate
    print("[Module 1] Checking environment...")
    validation = validate_environment()
    print(f"  Firefox : {validation['firefox']['version']} — {'OK' if validation['firefox']['ok'] else 'ACTION NEEDED'}")
    print(f"  JDK     : {validation['jdk']['version']}  — {'OK' if validation['jdk']['ok'] else 'ACTION NEEDED'}")

    # Module 2 — install if needed
    needs_install = not validation["firefox"]["ok"] or not validation["jdk"]["ok"]
    if needs_install:
        print("\n[Module 2] Running auto-installation...")
        run_installations(validation)
    else:
        print("\n[Module 2] No installation needed.")

    # Module 3 — final verify
    print("\n[Module 3] Final verification...")
    passed, _ = final_verify()

    if passed:
        print("\n✅ Setup complete. Ready for CBS V2 authentication.")
        # TODO: hand off to Module 4 (version upgrade check) and auth flow
    else:
        print("\n❌ Setup incomplete. Please check the log and retry.")
        exit(1)

if __name__ == "__main__":
    main()