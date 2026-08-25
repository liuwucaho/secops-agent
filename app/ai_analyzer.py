import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from health_check import run_health_check


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def analyze_health():
    health_data = run_health_check()

    prompt = f"""
你是一名专业的 Linux 和网络安全技术支持工程师。

下面是一台服务器的真实巡检数据：

{json.dumps(health_data, ensure_ascii=False, indent=2)}

请根据这些数据生成一份简洁的巡检分析报告。

要求：
1. 只能依据提供的数据判断，不允许编造。
2. 先给出整体健康状态。
3. 分析 CPU、内存、磁盘、Nginx 服务、80/443端口和Nginx日志。
4. 如果存在异常，说明可能原因和下一步排查建议。
5. 如果没有异常，也要明确说明当前没有发现明显风险。
6. 使用中文输出。
7. 不允许根据现有数据做超出证据范围的推断。
   例如127.0.0.1端口open，只能说明本机端口可访问，
   不能推断公网访问一定正常。
8. 如果现有数据不足以判断某个问题，要明确写“当前数据不足以判断”，
   并说明还需要采集什么信息。
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    report = analyze_health()
    print(report)
