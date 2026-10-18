import subprocess

# 模拟模型返回的服务名，不调用真实模型。
model_service = "api; echo INJECTED"

options = {
    "capture_output": True,
    "text": True,
    "timeout": 3,
    "check": True,
}

# 对照一：模型输出进入 Shell 命令字符串。
unsafe = subprocess.run(
    f"/bin/echo {model_service}",
    shell=True,
    **options,
)

# 对照二：固定程序，模型输出只占一个参数位置。
argv = subprocess.run(
    ["/bin/echo", model_service],
    shell=False,
    **options,
)

print("unsafe:", repr(unsafe.stdout))
print("argv:", repr(argv.stdout))