from modules.module1_validate import validate_environment
from utils.logger import write_log

def final_verify():
    result = validate_environment()   # re-run after installs

    all_pass = result["firefox"]["ok"] and result["jdk"]["ok"]

    status = {
        "Firefox installed":           result["firefox"]["installed"],
        "Firefox version valid (50.0)": result["firefox"]["ok"],
        "JDK installed":               result["jdk"]["installed"],
        "JDK version valid (7 or 8)":  result["jdk"]["ok"],
        "JAVA_HOME set":               bool(result["jdk"]["java_home"]),
    }

    write_log(status, success=all_pass)

    if all_pass:
        print("✅ All validations passed. Proceeding to authentication.")
    else:
        print("❌ Validation failed. Check cbs_setup.log for details.")

    return all_pass, result