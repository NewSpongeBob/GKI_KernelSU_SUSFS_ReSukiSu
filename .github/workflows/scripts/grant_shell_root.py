#!/usr/bin/env python3
"""
修改 init.c：
将 allow_shell 的默认值从 false 改为 true（移除 CONFIG_KSU_DEBUG 条件），
使 shell (UID 2000) 在非 DEBUG 模式下也默认获得 root 权限。

ReSukiSU 新版本中 allow_shell 变量控制 shell root 授权，
定义在 kernel/core/init.c，原始代码：
    #ifdef CONFIG_KSU_DEBUG
    bool allow_shell = true;
    #else
    bool allow_shell = false;
    #endif
"""

import sys

def patch_init(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    old_code = (
        '#ifdef CONFIG_KSU_DEBUG\n'
        'bool allow_shell = true;\n'
        '#else\n'
        'bool allow_shell = false;\n'
        '#endif'
    )

    new_code = 'bool allow_shell = true;'

    if old_code not in content:
        print("ERROR: Could not find allow_shell definition in init.c!")
        print("Expected pattern:")
        print(old_code)
        sys.exit(1)

    content = content.replace(old_code, new_code, 1)

    with open(filepath, 'w') as f:
        f.write(content)

    print("✓ Patch applied successfully!")
    print("Shell (UID 2000) will have root access by default (allow_shell = true)")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <init.c-path>")
        sys.exit(1)

    patch_init(sys.argv[1])
