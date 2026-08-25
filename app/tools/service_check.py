import json
import subprocess


def check_service(service_name: str):
    result = {
        "service": service_name,
        "status": "unknown"
    }

    try:
        process = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True,
            timeout=5
        )

        status = process.stdout.strip()

        if status == "active":
            result["status"] = "active"
        else:
            result["status"] = status or "inactive"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


if __name__ == "__main__":
    data = check_service("nginx")
    print(json.dumps(data, indent=2, ensure_ascii=False))
