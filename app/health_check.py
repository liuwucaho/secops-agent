import json

from tools.system_metrics import check_system_metrics
from tools.port_check import check_port
from tools.service_check import check_service
from tools.log_analyzer import analyze_nginx_log


def run_health_check():
    result = {
        "system_metrics": check_system_metrics(),
        "nginx_service": check_service("nginx"),
        "http_port": check_port("127.0.0.1", 80),
        "https_port": check_port("127.0.0.1", 443),
        "nginx_log": analyze_nginx_log()
    }

    return result


if __name__ == "__main__":
    data = run_health_check()
    print(json.dumps(data, indent=2, ensure_ascii=False))
