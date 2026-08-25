import json
import subprocess


def check_nginx_config(port: int):
    result = {
        "port": port,
        "syntax_valid": False,
        "test_completed": False,
        "port_found": False,
        "matches": []
    }

    try:
        # 先检查 Nginx 配置语法
        test = subprocess.run(
            ["nginx", "-t"],
            capture_output=True,
            text=True,
            timeout=5
        )

        test_output = test.stderr.strip() or test.stdout.strip()

        result["syntax_valid"] = "syntax is ok" in test_output.lower()
        result["test_completed"] = test.returncode == 0
        result["config_test"] = test_output

        result["config_test"] = (
            test.stderr.strip() or test.stdout.strip()
        )

        # 只读搜索配置中是否存在对应 listen 端口
        grep = subprocess.run(
            [
                "grep",
                "-R",
                "-n",
                f"listen {port}",
                "/etc/nginx"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        if grep.stdout.strip():
            result["port_found"] = True
            result["matches"] = grep.stdout.strip().splitlines()[:10]

    except Exception as e:
        result["error"] = str(e)

    return result


if __name__ == "__main__":
    data = check_nginx_config(80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
