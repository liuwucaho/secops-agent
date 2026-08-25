import json
import psutil


def get_status(value, warning, critical):
    if value >= critical:
        return "critical"
    elif value >= warning:
        return "warning"
    else:
        return "normal"


def check_system_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    result = {
        "cpu": {
            "usage_percent": cpu_percent,
            "status": get_status(cpu_percent, 70, 90)
        },
        "memory": {
            "total_gb": round(memory.total / 1024**3, 2),
            "used_gb": round(memory.used / 1024**3, 2),
            "usage_percent": memory.percent,
            "status": get_status(memory.percent, 75, 90)
        },
        "disk": {
            "total_gb": round(disk.total / 1024**3, 2),
            "used_gb": round(disk.used / 1024**3, 2),
            "usage_percent": disk.percent,
            "status": get_status(disk.percent, 80, 90)
        }
    }

    return result


if __name__ == "__main__":
    data = check_system_metrics()
    print(json.dumps(data, indent=2, ensure_ascii=False))
