#!/usr/bin/env python3
"""argcheck - Validate CLI arguments and environment variables.

Single-file, zero-dependency CLI.
"""

import sys
import argparse
import os
import re


def cmd_env(args):
    """Check required environment variables."""
    missing = []
    found = []
    for var in args.vars:
        val = os.environ.get(var)
        if val:
            masked = val[:3] + "***" if len(val) > 6 and args.mask else val
            found.append((var, masked))
        else:
            missing.append(var)
    for var, val in found:
        print(f"  ✅ {var}={val}")
    for var in missing:
        print(f"  ❌ {var} — not set")
    if missing:
        return 1


def cmd_port(args):
    """Check if port is valid and available."""
    import socket
    for port in args.ports:
        if not (1 <= port <= 65535):
            print(f"  ❌ {port} — invalid (must be 1-65535)")
            continue
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            s.close()
            if result == 0:
                print(f"  🔴 {port} — in use")
            else:
                print(f"  🟢 {port} — available")
        except Exception as e:
            print(f"  ⚠️  {port} — {e}")


def cmd_file(args):
    """Check file existence and permissions."""
    for path in args.paths:
        if not os.path.exists(path):
            print(f"  ❌ {path} — not found")
            continue
        stat = os.stat(path)
        perms = []
        if os.access(path, os.R_OK): perms.append("r")
        if os.access(path, os.W_OK): perms.append("w")
        if os.access(path, os.X_OK): perms.append("x")
        kind = "dir" if os.path.isdir(path) else "file"
        size = stat.st_size
        print(f"  ✅ {path} ({kind}, {''.join(perms)}, {size} bytes)")


def cmd_url(args):
    """Validate URL format."""
    for url in args.urls:
        m = re.match(r'^https?://[^\s/$.?#].[^\s]*$', url)
        if m:
            print(f"  ✅ {url}")
        else:
            print(f"  ❌ {url} — invalid URL format")


def main():
    p = argparse.ArgumentParser(prog="argcheck", description="Validate arguments and environment")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("env", help="Check env vars"); s.add_argument("vars", nargs="+"); s.add_argument("-m", "--mask", action="store_true")
    s = sub.add_parser("port", help="Check ports"); s.add_argument("ports", type=int, nargs="+")
    s = sub.add_parser("file", help="Check files"); s.add_argument("paths", nargs="+")
    s = sub.add_parser("url", help="Validate URLs"); s.add_argument("urls", nargs="+")
    args = p.parse_args()
    if not args.cmd: p.print_help(); return 1
    cmds = {"env": cmd_env, "port": cmd_port, "file": cmd_file, "url": cmd_url}
    return cmds[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
