import json
import os

from tools.nginx_config_check import check_nginx_config

from tools.listener_check import check_listener

from dotenv import load_dotenv
from openai import OpenAI

from tools.system_metrics import check_system_metrics
from tools.port_check import check_port
from tools.service_check import check_service
from tools.log_analyzer import analyze_nginx_log
from tools.http_check import check_http


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_system_metrics",
            "description": "检查当前Linux服务器的CPU、内存和磁盘使用情况",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_port",
            "description": "检查指定主机的TCP端口是否可以连接",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "需要检查的主机地址"
                    },
                    "port": {
                        "type": "integer",
                        "description": "需要检查的TCP端口"
                    }
                },
                "required": ["host", "port"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_service",
            "description": "检查Linux systemd服务当前是否正在运行",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "需要检查的服务名称，例如nginx"
                    }
                },
                "required": ["service_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_nginx_log",
            "description": "读取并分析Nginx错误日志，检查error、warning和critical异常",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_http",
            "description": "检查指定HTTP或HTTPS URL是否可以正常访问，并返回状态码和响应时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "需要检查的完整URL"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "check_listener",
        "description": "检查Linux服务器指定TCP端口是否正在监听，并返回监听信息",
        "parameters": {
            "type": "object",
            "properties": {
                "port": {
                    "type": "integer",
                    "description": "需要检查的TCP端口"
                }
            },
            "required": ["port"]
        }
    }
},

         {
    "type": "function",
    "function": {
        "name": "check_nginx_config",
        "description": "检查Nginx配置语法，并确认配置中是否存在指定监听端口",
        "parameters": {
            "type": "object",
            "properties": {
                "port": {
                    "type": "integer",
                    "description": "需要检查的Nginx监听端口"
                }
            },
            "required": ["port"]
        }
    }
},

]

TOOL_ALIASES = {
    "check_nginx_log": "analyze_nginx_log"
}

def execute_tool(tool_name, arguments):
    tool_name = TOOL_ALIASES.get(tool_name, tool_name)
    """
    真正执行模型选择的工具。
    当前 Demo 只允许检查本机，避免 Agent 被用于扫描任意外部地址。
    """
    
    if tool_name == "check_listener":
        port = arguments.get("port")
        return check_listener(port) 

    elif tool_name == "check_system_metrics":
        return check_system_metrics()


    elif tool_name == "check_port":
        host = arguments.get("host", "127.0.0.1")
        port = arguments.get("port")


        # 安全边界：只允许检查本机
        if host not in ["127.0.0.1", "localhost"]:
            return {
                "status": "denied",
                "message": "当前Agent只允许检查本机端口"
            }

        return check_port(host, port)

    elif tool_name == "check_nginx_config":
        port = arguments.get("port")
        return check_nginx_config(port)

    elif tool_name == "check_service":
        service_name = arguments.get("service_name")
        return check_service(service_name)

    elif tool_name == "analyze_nginx_log":
        return analyze_nginx_log()

    elif tool_name == "check_http":
        url = arguments.get("url", "")

        # 安全边界：当前只检查本机Web服务
        allowed_prefixes = [
            "http://127.0.0.1",
            "https://127.0.0.1",
            "http://localhost",
            "https://localhost"
        ]

        if not any(url.startswith(prefix) for prefix in allowed_prefixes):
            return {
                "status": "denied",
                "message": "当前Agent只允许检查本机HTTP/HTTPS服务"
            }

        return check_http(url)

    return {
        "status": "error",
        "message": f"未知工具: {tool_name}"
    }

def run_agent(user_question):
    messages = [
        {
            "role": "system",
            "content": """
你是一名Linux和网络安全技术支持工程师。

你的任务是根据用户描述的问题，选择合适的工具进行故障排查。

规则：
1. 能通过工具获得的数据必须调用工具，不能猜测。
2. 不要为了展示能力而调用所有工具，只调用当前排障需要的工具。
3. 根据上一步检查结果决定下一步是否需要继续调用工具。
4. 如果证据不足，要明确说明无法判断，并指出还需要什么数据。
5. 不允许执行重启、删除文件、修改配置等高风险操作。
6. 最终使用中文输出。
7. 最终报告必须区分：
   - 已确认事实
   - 可能原因
   - 下一步建议
8. 优先使用最少数量的工具完成问题定位，不要为了完整巡检而调用无关工具。
9. 如果已经获得足够证据支持明确结论，应停止继续调用工具并输出结果。
10. 工具调用应遵循“先直接证据，后辅助证据”的原则。
例如：
- URL访问失败，优先检查目标端口；
- 端口已经明确closed，可以确认当前没有服务监听，不需要再检查CPU和内存；
- 只有服务运行但响应异常时，才进一步检查资源和日志。
11. 不要重复检查与当前故障无直接关系的正常服务，除非需要做对照验证。
12. 只能调用系统提供的工具，工具名称必须与提供的Tool名称完全一致，不允许自行创造工具名称。
"""
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    max_steps = 8

    for step in range(max_steps):

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1
        )

        message = response.choices[0].message

        # 如果模型不再调用工具，说明已经准备给最终答案
        if not message.tool_calls:
            return message.content

        # 将模型这次的工具调用请求加入上下文
        messages.append(
            message.model_dump(exclude_none=True)
        )

        # 可以一次调用一个或多个工具
        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments or "{}"
                )
            except json.JSONDecodeError:
                arguments = {}

            print(f"\n[Agent] 调用工具: {tool_name}")
            print(
                f"[Agent] 参数: "
                f"{json.dumps(arguments, ensure_ascii=False)}"
            )

            result = execute_tool(
                tool_name,
                arguments
            )

            print(
                f"[Tool] 返回: "
                f"{json.dumps(result, ensure_ascii=False)}"
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False
                )
            })

    return "达到最大排查步骤，建议人工进一步分析。"


if __name__ == "__main__":
    print("SecOps Agent 已启动")
    print("输入 exit 退出\n")

    while True:
        question = input("你：").strip()

        if question.lower() in ["exit", "quit"]:
            print("Agent 已退出")
            break

        if not question:
            continue

        try:
            answer = run_agent(question)

            print("\n========== Agent 分析结果 ==========")
            print(answer)
            print("====================================\n")

        except Exception as e:
            print(f"\nAgent运行异常: {e}\n")




