"""Local Docker sandbox boundary demo; requires Docker Desktop and a pre-pulled image.

Lab type: real container isolation for a harmless fixed test payload, NOT a
production-grade sandbox or a simulation of a malicious agent executing tools.
"""

from __future__ import annotations

import subprocess
import uuid

IMAGE = "python:3.12-alpine"
CHECKS = r'''
import os
import socket
from pathlib import Path

try:
    Path('/root_write_probe.txt').write_text('test')
    print('filesystem_write=ALLOWED')
except OSError:
    print('filesystem_write=BLOCKED')

try:
    with socket.create_connection(('1.1.1.1', 443), timeout=1):
        print('network_egress=ALLOWED')
except OSError:
    print('network_egress=BLOCKED')

print('host_private_path_visible=', Path('/host_private').exists())
print('deepseek_key_in_container=', 'DEEPSEEK_API_KEY' in os.environ)
for name in ('memory.max', 'pids.max', 'cpu.max'):
    path = Path('/sys/fs/cgroup') / name
    if path.is_file():
        print(name + '=', path.read_text().strip())
    else:
        print(name + '=not_exposed')
'''


def isolated_run(program: str, timeout_seconds: int):
    name = 'ai-security-sandbox-' + uuid.uuid4().hex[:12]
    cmd = [
        'docker', 'run', '--rm', '--pull=never', '--name', name,
        '--network=none', '--read-only', '--cap-drop=ALL',
        '--security-opt=no-new-privileges', '--user=65534:65534',
        '--memory=128m', '--memory-swap=128m', '--cpus=0.5',
        '--pids-limit=64', '--tmpfs=/tmp:rw,nosuid,noexec,size=16m',
        IMAGE, 'python', '-B', '-c', program,
    ]
    try:
        return subprocess.run(
            cmd, text=True, capture_output=True, timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        # Stop the container, not merely the waiting docker CLI process.
        subprocess.run(
            ['docker', 'rm', '-f', name], capture_output=True,
            text=True, timeout=10, check=False,
        )
        return None


def main() -> None:
    print('=== filesystem / network / secrets / resource limits ===')
    try:
        result = isolated_run(CHECKS, timeout_seconds=20)
        if result is None:
            print('first_run=HOST_TIMEOUT')
            return
        if result.returncode != 0:
            print('docker_error:', result.stderr.strip())
            print('Hint: docker pull ' + IMAGE)
            return
        print(result.stdout, end='')

        print('=== wall-clock timeout ===')
        timeout_result = isolated_run(
            'import time; time.sleep(30)', timeout_seconds=3,
        )
        print('wall_time_limit=ENFORCED' if timeout_result is None
              else 'wall_time_limit=NOT_OBSERVED')
    except FileNotFoundError:
        print('docker_error: Docker CLI not found; install/start Docker Desktop')
    except subprocess.TimeoutExpired:
        print('docker_error: cleanup timed out; inspect running containers')


if __name__ == '__main__':
    main()