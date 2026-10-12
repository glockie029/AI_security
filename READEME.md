# AI_security

一个用于学习大模型应用安全的 Python 实验项目，主要探索 API 调用、工具调用、提示注入和执行层安全控制。

## 项目结构

```text
AI_security/
├── llm_lic.py             # 命令行入口与模型调用
├── tools.py               # 模拟漏洞数据及工具函数
├── requirements.txt       # Python 依赖
├── mode/
│   └── evaluator.py       # 安全评估
└── test/
    └── test_evaluator.py  # 安全评估测试
```

## 安装配置

建议使用 Python 3.12：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

配置环境变量，也可使用本地 `.env` 文件：

```dotenv
DEEPSEEK_API_KEY=你的密钥
base_url=https://api.deepseek.com
MODEL=deepseek-flash
```

请勿将密钥或包含密钥的 `.env` 文件提交到仓库。

## 使用方法

单次提问：

```bash
python llm_lic.py ask "什么是提示注入？"
```

启动多轮对话：

```bash
python llm_lic.py chat
```

对话中可输入：

```text
请查询 CVE-2021-44228 的漏洞严重程度。
```

输入 `exit` 或 `quit` 退出。

运行安全评估测试：

```bash
python -m test.test_evaluator
```

## TODO

- [x] 接入大模型 API，支持单次提问。
- [x] 实现命令行对话与漏洞查询工具调用。
- [x] 实现基础安全评估和三个测试场景。
- [x] 验证 DeepSeek 接口与漏洞查询流程。
- [ ] 将被污染的工具返回结果接入提示注入实验。
- [ ] 对比正常与恶意工具结果对模型行为的影响。
- [ ] 完善多轮对话历史与多个工具调用处理。
- [ ] 增加工具参数校验和执行权限控制。
- [ ] 补充异常处理与对话流程测试。
- [ ] 保存实验记录，包括模型行为、拦截结果和实际影响。

> 项目用于学习实验，漏洞数据和状态更新均为本地模拟。
