import os
import sys
import traceback


def _console():
    """UTF-8 console so the check marks display; harmless if unsupported."""
    if sys.platform == "win32":
        os.system("chcp 65001 >nul")
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_console()

import config                                              # noqa: E402
from modules.module1_validate import validate_environment  # noqa: E402
from modules.module2_install import run_installations      # noqa: E402
from modules.module3_verify import final_verify            # noqa: E402
from modules.module5_config import run_module5             # noqa: E402

LINE = "=" * 60


def _pause():
    if sys.platform == "win32":
        os.system("pause")


def _fail(message, exc=None):
    print(f"\n  ❌ {message}")
    if exc is not None:
        try:
            with open(os.path.join(config.LOG_DIR, "cbs_error.log"), "a", encoding="utf-8") as f:
                f.write(traceback.format_exc() + "\n")
            print(f"     Details saved in {os.path.join(config.LOG_DIR, 'cbs_error.log')}")
        except Exception:
            pass
    print("     Please contact your IT administrator.\n")
    _pause()
    sys.exit(1)


def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(LINE)
    print("       CBS V2 AUTO AUTHENTICATION SETUP")
    print("       Version 1.0  |  IT Department")
    print(LINE)

    # Step 1 - check
    print("\n  [Step 1/4] Checking Firefox and Java...")
    validation = validate_environment()
    ff, jdk = validation["firefox"], validation["jdk"]
    print(f"             Firefox : {ff['version'] or 'not found'}  {'OK' if ff['ok'] else 'needs update'}")
    print(f"             Java    : {jdk['version'] or 'not found'}  {'OK' if jdk['ok'] else 'needs update'}")

    # Step 2 - install if needed
    if not ff["ok"] or not jdk["ok"]:
        print("\n  [Step 2/4] Installing required software - please wait, do not close this window...")
        try:
            run_installations(validation)
        except Exception as e:
            _fail(f"Installation failed: {e}", e)
    else:
        print("\n  [Step 2/4] Software is already correct.")

    # Step 3 - verify
    print("\n  [Step 3/4] Verifying installation...")
    try:
        passed, _ = final_verify()
    except Exception as e:
        _fail(f"Verification failed: {e}", e)
    if not passed:
        _fail("Installation could not be verified (see cbs_setup.log).")

    # Step 4 - configuration
    print("\n  [Step 4/4] Machine configuration...")
    try:
        m5_ok, _ = run_module5()
    except KeyboardInterrupt:
        _fail("Cancelled by user.")
    except Exception as e:
        _fail(f"Configuration failed: {e}", e)

    print("\n" + LINE)
    if m5_ok:
        print("  ✅ SETUP COMPLETE - this machine is configured for CBS V2.")
    else:
        print("  ⚠️  SETUP FINISHED WITH WARNINGS - review the lines marked ⚠️ above.")
    print(LINE + "\n")
    _pause()


if __name__ == "__main__":
    main()
