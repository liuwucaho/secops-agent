import json
from pathlib import Path


def analyze_nginx_log(log_path="/var/log/nginx/error.log", max_lines=100):
    path = Path(log_path)

    result = {
        "log_path": log_path,
        "total_lines": 0,
        "critical": 0,
        "error": 0,
        "warning": 0,
        "notice": 0,
        "status": "normal",
        "recent_abnormal_logs": []
    }

    if not path.exists():
        result["status"] = "error"
        result["message"] = "log file not found"
        return result

    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-max_lines:]

        result["total_lines"] = len(lines)

        for line in lines:
            lower_line = line.lower()

            if "[crit]" in lower_line or "[alert]" in lower_line or "[emerg]" in lower_line:
                result["critical"] += 1
                result["recent_abnormal_logs"].append(line.strip())

            elif "[error]" in lower_line:
                result["error"] += 1
                result["recent_abnormal_logs"].append(line.strip())

            elif "[warn]" in lower_line:
                result["warning"] += 1
                result["recent_abnormal_logs"].append(line.strip())

            elif "[notice]" in lower_line:
                result["notice"] += 1

        if result["critical"] > 0:
            result["status"] = "critical"
        elif result["error"] > 0:
            result["status"] = "error"
        elif result["warning"] > 0:
            result["status"] = "warning"

        result["recent_abnormal_logs"] = result["recent_abnormal_logs"][-10:]

    except PermissionError:
        result["status"] = "error"
        result["message"] = "permission denied"

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)

    return result


if __name__ == "__main__":
    data = analyze_nginx_log()
    print(json.dumps(data, indent=2, ensure_ascii=False))

