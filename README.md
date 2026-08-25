# SecOps Agent

一个面向 Linux / Web 服务场景的智能巡检与故障分析 Agent。

## 项目目标

传统巡检通常按照固定脚本执行，而实际故障排查路径并不固定。

本项目通过大模型 + Tool Calling 的方式，让 Agent 根据用户描述的问题，自主选择合适的诊断工具，获取真实系统数据，并根据检查结果继续决定下一步排查动作。

核心原则：

- Python Tool 负责获取真实、确定性的数据
- AI 负责理解问题、选择工具和总结分析
- 数据不足时不进行无依据推断
- 高风险操作默认禁止自动执行
- 工具权限遵循最小权限原则

## 当前功能

- CPU / 内存 / 磁盘巡检
- TCP 端口连通性检查
- Linux 端口监听检查
- systemd 服务状态检查
- HTTP / HTTPS 访问检查
- Nginx 错误日志分析
- Nginx 配置与监听端口检查
- DeepSeek Tool Calling
- 多步骤自动故障排查

## 示例

用户输入：

```text
http://127.0.0.1:8081 访问不了，帮我排查一下原因。
```

Agent 会根据情况自主调用：

```text
check_listener
    ↓
check_http
    ↓
check_service
    ↓
check_nginx_config
    ↓
生成故障结论
```

## 安全设计

当前 Demo 对工具能力进行了限制：

- 网络检查默认只允许 localhost
- 不允许 Agent 自动执行删除文件、重启服务、修改配置等高风险操作
- API Key 通过环境变量保存，不写入代码
- Tool 执行层会校验工具名称及参数

## 项目结构

```text
secops-agent/
├── app/
│   ├── agent.py
│   ├── ai_analyzer.py
│   ├── health_check.py
│   └── tools/
│       ├── system_metrics.py
│       ├── port_check.py
│       ├── listener_check.py
│       ├── service_check.py
│       ├── http_check.py
│       ├── log_analyzer.py
│       └── nginx_config_check.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 安装

创建 Python 虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

复制环境变量示例文件：

```bash
cp .env.example .env
```

然后编辑 `.env`：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## 运行

启动智能巡检 Agent：

```bash
python app/agent.py
```

示例：

```text
你：http://127.0.0.1:8081 访问不了，帮我排查一下原因。
```

Agent 会根据当前问题自主选择诊断工具，并根据每一步工具返回的数据继续决定是否需要进一步排查。

## 设计思路

整体流程：

```text
用户自然语言问题
        ↓
   DeepSeek LLM
        ↓
判断需要调用的 Tool
        ↓
Python Tool 获取真实数据
        ↓
结构化 JSON 返回给模型
        ↓
模型根据新证据继续判断
        ↓
证据充分后停止调用
        ↓
输出故障分析和处理建议
```

本项目并不是让大模型直接执行 Linux 命令，而是通过预定义 Tool 控制其能力范围。

模型负责：

- 理解用户意图
- 决定排障路径
- 选择工具
- 分析工具返回结果
- 生成最终报告

Python 程序负责：

- 实际获取系统数据
- 参数校验
- 权限控制
- 工具白名单
- 风险边界控制
