"""Stop running instances of the racn MCP server (any OS).

Matches processes by the server's entry point name, so it won't touch
unrelated processes that happen to use this repo's virtualenv (e.g. an
editor's language server).
"""

from __future__ import annotations

import os
import platform
import signal
import subprocess

PATTERN = "risk-aware-commit-notation-mcp"


def find_pids() -> list[int]:
    if platform.system() == "Windows":
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process "
                f"| Where-Object {{ $_.CommandLine -match '{PATTERN}' }} "
                "| Select-Object -ExpandProperty ProcessId",
            ],
            capture_output=True,
            text=True,
        )
    else:
        result = subprocess.run(
            ["pgrep", "-f", PATTERN],
            capture_output=True,
            text=True,
        )
    return [int(pid) for pid in result.stdout.split()]


def main() -> None:
    for pid in find_pids():
        if pid == os.getpid():
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Stopped racn MCP server process {pid}")
        except (ProcessLookupError, PermissionError, OSError):
            pass


if __name__ == "__main__":
    main()
