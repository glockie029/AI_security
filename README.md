# AI Security｜AI 应用安全学习实验室

用于学习 LLM 调用、工具调用、RAG、Agent/MCP 和执行层安全边界的 Python 实验项目。
当前目标是形成可阅读、可测试、可继续扩展的项目基础，而非宣称已具备生产级防护能力。

## 1. 范围与安全边界

- 漏洞数据、状态更新函数均为本地模拟；没有连接实际工单系统。
- 提示注入样本是实验内容，保留于模拟工具数据中，不是应执行的指令。
- 模型提出工具调用、工具实际执行、业务产生副作用，属于三个不同的结果层级。
- 本轮只整理结构、命名、导入副作用及测试；权限策略和原评估判据保持不变。
- 本次代码整理不更新课程或 Notion 的学习验收状态。

## 2. 项目结构

```text
AI_Security/
├── ai_security/
│   ├── cli.py                  # ask/chat 命令
│   ├── config.py               # 配置与按需创建客户端
│   ├── agent.py                # 本地及 MCP Agent 循环
│   ├── tools/
│   │   ├── definitions.py      # 唯一工具定义
│   │   ├── validation.py       # 原 CVE 参数校验
│   │   └── vulnerabilities.py  # 模拟数据与注入样本
│   ├── rag/
│   │   ├── chunking.py         # 纯文档切分函数
│   │   └── retrieval.py        # 向量检索与最小问答
│   ├── mcp/
│   │   ├── client.py           # MCP 手动联调客户端
│   │   └── server.py           # 最小教学服务
│   └── evaluation/
│       ├── evaluator.py       # 场景攻击判据
│       └── citations.py       # 引用编号检查
├── examples/                  # 手动运行的课程演示
├── tests/                     # 离线自动化测试
├── llm_lic.py                 # 原 CLI 命令兼容入口
├── .env.example               # 无真实密钥的配置示例
├── requirements.txt           # 核心直接依赖与 MCP 声明
├── requirements-rag.txt       # 可选 RAG/Attention 依赖
└── README.md
```

```text
CLI / 示例 → 配置与客户端 → 模型
                      ↓ 工具调用请求
               Agent 执行白名单
                      ↓
               本地工具 / MCP 工具
                      ↓
               场景评估与引用编号检查
```

CLI 的原教学流程与 Agent 循环是两个入口，不应将 CLI 的模拟拦截描述为完整的 Agent IAM 实现。
导入核心模块不创建模型客户端、不加载 Embedding 权重、不启动 MCP 服务，也不运行教学演示。

## 3. 环境与依赖

本地执行统一使用以下解释器，本次整理未安装、升级或降级任何依赖：

```text
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python
```

| 范围 | 依赖 | 使用时机 |
|---|---|---|
| 纯函数与本地 Agent 模拟测试 | Python 标准库 | 不需要模型 API 或可选 SDK |
| CLI 离线用例 | 复用 CLI 核心依赖 | 模型响应由测试替身提供，不访问 API |
| CLI 与真实模型调用 | OpenAI SDK、Typer、Prompt Toolkit、python-dotenv | 真实运行 ask/chat 或模型 Agent |
| RAG / Attention | NumPy、Sentence Transformers | 运行相应示例 |
| MCP | MCP SDK | 手动启动 MCP 集成 |

**依赖声明不是已验证的锁文件：**
- 核心依赖保留原清单中的直接依赖版本，不从共享虚拟环境重新冻结全量依赖。
- 新补的 RAG/MCP 依赖尚未锁定；MCP 的 SDK 接口与版本兼容性待单独验证。
- 指定解释器的实际安装版本与原依赖声明存在差异，尚未进行全新环境安装验证。

以下仅记录安装方式；本轮没有执行，实际安装前需单独确认版本与环境变更范围。

```bash
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -m pip install -r /Users/mac/Documents/GitHub/AI_Security/requirements.txt
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -m pip install -r /Users/mac/Documents/GitHub/AI_Security/requirements-rag.txt
```

## 4. 配置

参考项目根目录的 `.env.example`，经确认后自行配置根目录 `.env`。
配置沿用现有变量名，尤其保留小写的 `base_url`；已有进程环境变量优先于文件中的值。

```dotenv
DEEPSEEK_API_KEY=TOKEN
base_url=https://api.deepseek.com
MODEL=deepseek-flash
```

- 不将真实密钥写入代码、测试、示例或提交到 Git。
- 离线测试与查看帮助不需要 API 密钥；当前环境的帮助显示另有依赖兼容问题，见待修项。
- 首次真实运行 RAG 时可能下载 Embedding 模型并占用磁盘；问答会调用模型 API。
- 原 RAG 使用 `deepseek-chat`，CLI/Agent 使用 `MODEL`；本轮不改变这一模型选择差异。

## 5. 离线验证

以下命令不访问模型 API，不下载模型权重，不启动 MCP，不创建 Python 字节码缓存：

```bash
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m unittest discover -s /Users/mac/Documents/GitHub/AI_Security/tests -t /Users/mac/Documents/GitHub/AI_Security -v
```

覆盖范围：
- 保留原三项攻击判定场景：无恶意调用、执行层阻断、模拟状态改变。
- 验证文档切分、引用编号、CVE 参数及唯一工具定义。
- 验证按需读取配置，以及导入时不加载可选 SDK 或运行示例。
- 用模拟模型响应验证本地 Agent 的只读白名单、非法参数拒绝和轮数限制。
- CLI、RAG 和 MCP 路径测试使用替身；不把这些用例描述为真实 SDK/服务联调。

这些测试不代表真实模型的注入防御率、真实 MCP 兼容性或端到端业务权限已通过验证。

**本轮离线结果（2026-10-15）：** 38 项测试通过，36 个 Python 文件语法检查通过；
Attention、切分、Agent 状态三个教学演示与整理前输出一致。真实模型和 MCP 集成未重新联调。

## 6. 运行入口

原 CLI 入口保留：

```bash
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B /Users/mac/Documents/GitHub/AI_Security/llm_lic.py --help
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B /Users/mac/Documents/GitHub/AI_Security/llm_lic.py ask "什么是提示注入？"
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B /Users/mac/Documents/GitHub/AI_Security/llm_lic.py chat
```

模块与示例命令先切换至项目根目录：

```bash
cd /Users/mac/Documents/GitHub/AI_Security
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m ai_security.cli --help
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m examples.chunking_demo
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m examples.agent_state_demo
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m examples.attention_demo
```

以下入口涉及外部依赖、模型 API 或 MCP，环境兼容性需单独验收：

```bash
cd /Users/mac/Documents/GitHub/AI_Security
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m examples.agent_demo
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m examples.rag_demo
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m ai_security.mcp.client
/Users/mac/Documents/GitHub/ChatApp/venv/bin/python -B -m examples.agent_mcp_demo
```

## 7. 旧代码迁移映射

| 原位置 | 新位置 |
|---|---|
| `llm_lic.py` 中的 CLI | `ai_security/cli.py`，根入口保留兼容壳 |
| `llm_lic.py` 中的配置和 CVE 校验 | `ai_security/config.py`、`ai_security/tools/validation.py` |
| `agent_loop.py` | `ai_security/agent.py`，手动入口移至 `examples/` |
| `tools/toolsCalls.py` 与 CLI 中重复定义 | `ai_security/tools/definitions.py` |
| `tools/tools.py` | `ai_security/tools/vulnerabilities.py` |
| `chunking.py` | `ai_security/rag/chunking.py`、`examples/chunking_demo.py` |
| `vector_search.py` | `ai_security/rag/retrieval.py`、`examples/rag_demo.py` |
| `mcp_cs/` | `ai_security/mcp/` |
| `mode/` | `ai_security/evaluation/` |
| `test/` | `tests/` |
| `attention_demo.py`、`agent/one_agent_loop.py` | `examples/attention_demo.py`、`examples/agent_state_demo.py` |

除根 CLI 外，旧模块路径不再维护重复实现；历史笔记中的其他命令需要按本表迁移。
IDE 配置、实际 `.env`、既有缓存和 Git 索引未作清理或改动。

## 8. 已知限制与待修项

以下仅登记，不在本轮结构整理中改变：

| 项目 | 当前限制 |
|---|---|
| CLI 多工具回填 | 原流程仅回填最后一个 `tool_call_id` 的结果；多工具协议配对待修 |
| CLI 对话历史 | 工具轮仍可能额外追加空的 Assistant 内容；异常回滚也尚未完善 |
| 模拟数据状态 | `get_vulnerability()` 仍会修改返回的共享字典，测试间状态隔离待补 |
| 基线与注入样本 | 默认 Log4Shell 资料已含注入文本，不应当作干净基线统计 ASR |
| 评估判据 | 仅识别特定工具名与 `resolved` 状态；不覆盖所有危险调用 |
| 引用检查 | 只核对 DOC 编号，不检查引用内容是否支持回答 |
| MCP | 指定环境未安装 SDK；沿用原接口，尚未完成版本兼容与联调验证 |
| MCP 参数校验 | Server 保留原 `findall` 行为，完整匹配与类型校验待单独处理 |
| 模型协议 | ask 沿用 Responses，chat/RAG 沿用 Chat Completions，服务端兼容性待联调 |
| 代理环境 | 原客户端初始化提示缺少 SOCKS 传输依赖；未改代理，也未安装该依赖 |
| CLI 帮助 | 指定环境的 Typer 0.9.4 / Click 8.5.0 存在帮助渲染兼容问题；未改共享环境或加入兼容补丁 |

## 9. 作品交付状态

- [x] 复用代码、教学示例和离线测试分离。
- [x] 工具定义单一来源，配置和客户端按需初始化。
- [x] 保留原实验样本、执行策略与评估含义。
- [x] 提供迁移映射、实际入口和已知限制。
- [ ] 核验依赖锁定与全新环境复现。
- [ ] 修复已登记的 CLI 协议问题并补专项回归。
- [ ] 完成真实模型、Embedding、MCP 的集成验收。
- [ ] 保存攻击/正常样本、运行参数、加固前后报告及失败分析。

本目录是学习实验与作品基础，个人实验结果不作为生产部署或整体安全保证。
