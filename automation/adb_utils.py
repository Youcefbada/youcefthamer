#!/usr/bin/env python3
"""
================================================================================
  Shared ADB Utilities for Toki Enterprise Automation Suite (adb_utils.py)
  Centralizes ADB path discovery, command execution, and shell escaping
  to eliminate duplication across all automation modules.
================================================================================
"""

import subprocess
import os

ADB_CANDIDATES = [
    r"C:\Users\Youcef\AppData\Local\Android\Sdk\platform-tools\adb.exe",
    r"C:\Users\Youcef\Desktop\platform-tools\adb.exe",
    "adb"
]


def find_adb() -> str:
    """Discovers the ADB binary path from known candidate locations."""
    for c in ADB_CANDIDATES:
        if os.path.exists(c):
            return c
    return "adb"


ADB_PATH = find_adb()


def run_adb(cmd: str, is_su: bool = False, timeout: int = 12) -> str:
    """
    Executes an ADB shell command with proper escaping.

    Args:
        cmd: The shell command to execute on the device.
        is_su: If True, wraps the command in `su -c '...'` for root access.
        timeout: Command timeout in seconds.

    Returns:
        Stripped stdout output, or an error string prefixed with "ERROR:".
    """
    if is_su:
        escaped = cmd.replace("'", "'\\''")
        full_cmd = [ADB_PATH, "shell", f"su -c '{escaped}'"]
    else:
        full_cmd = [ADB_PATH, "shell"] + cmd.split()
    try:
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
        if res.returncode != 0 and res.stderr.strip():
            # Log stderr for debugging but don't fail
            import sys
            print(f"[ADB WARN] {res.stderr.strip()[:200]}", file=sys.stderr)
        return res.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"ERROR: Command timed out after {timeout}s"
    except Exception as e:
        return f"ERROR: {e}"
