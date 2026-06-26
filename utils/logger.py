import json, datetime

def write_log(status: dict, success: bool):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "success":   success,
        "checks":    status,
    }
    with open("cbs_setup.log", "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Log written → cbs_setup.log")