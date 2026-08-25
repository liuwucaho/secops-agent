import json
import requests


def check_http(url: str, timeout: int = 5):
    result = {
        "url": url,
        "status": "unknown"
    }

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True
        )

        result["status_code"] = response.status_code
        result["response_time_ms"] = round(
            response.elapsed.total_seconds() * 1000,
            2
        )

        if 200 <= response.status_code < 400:
            result["status"] = "healthy"
        elif 400 <= response.status_code < 500:
            result["status"] = "client_error"
        else:
            result["status"] = "server_error"

    except requests.exceptions.Timeout:
        result["status"] = "timeout"

    except requests.exceptions.ConnectionError:
        result["status"] = "connection_error"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


if __name__ == "__main__":
    data = check_http("http://127.0.0.1")
    print(json.dumps(data, indent=2, ensure_ascii=False))
