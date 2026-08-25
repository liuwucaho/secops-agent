import json
import subprocess


def check_listener(port: int):
    result = {
        "port": port,
        "listening": False,
        "details": []
    }

    try:
        process = subprocess.run(
            ["ss", "-lntp"],
            capture_output=True,
            text=True,
            timeout=5
        )

        lines = process.stdout.splitlines()

        for line in lines:
            if f":{port} " in line or line.rstrip().endswith(f":{port}"):
                result["listening"] = True
                result["details"].append(line.strip())

        if process.returncode != 0:
            result["error"] = process.stderr.strip()

    except Exception as e:
        result["error"] = str(e)

    return result


if __name__ == "__main__":
    data = check_listener(80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
