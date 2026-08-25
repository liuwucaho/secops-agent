import json
import socket


def check_port(host: str, port: int, timeout: int = 2):
    result = {
        "host": host,
        "port": port,
        "status": "closed"
    }

    try:
        with socket.create_connection((host, port), timeout=timeout):
            result["status"] = "open"

    except socket.timeout:
        result["status"] = "timeout"

    except ConnectionRefusedError:
        result["status"] = "closed"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


if __name__ == "__main__":
    data = check_port("127.0.0.1", 80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
