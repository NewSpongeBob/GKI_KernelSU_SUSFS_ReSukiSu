#!/usr/bin/env python3
"""
修改 allowlist.c，移除 ksu_grant_root_to_shell 函数的 CONFIG_KSU_DEBUG 宏限制
使 shell (UID 2000) 默认获得 root 权限
"""

import sys
import re

def patch_allowlist(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # 找到需要删除的行号
    lines_to_remove = set()
    
    # 第一处：函数定义处的 #ifdef CONFIG_KSU_DEBUG (在 static void ksu_grant_root_to_shell 之前)
    for i, line in enumerate(lines):
        if '#ifdef CONFIG_KSU_DEBUG' in line and i + 1 < len(lines):
            if 'static void ksu_grant_root_to_shell' in lines[i + 1]:
                lines_to_remove.add(i)
                print(f"Found function #ifdef at line {i+1}")
                # 找到对应的 #endif (在函数结束后的第一个 #endif)
                brace_count = 0
                found_func = False
                for j in range(i+1, len(lines)):
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                        if found_func and brace_count == 0:
                            if '#endif' in lines[j+1] if j+1 < len(lines) else False:
                                lines_to_remove.add(j+1)
                                print(f"Found function #endif at line {j+2}")
                            break
                    if 'static void ksu_grant_root_to_shell' in lines[j]:
                        found_func = True
                break
    
    # 第二处：调用处的 #ifdef CONFIG_KSU_DEBUG (包含 always allow adb shell 注释)
    for i, line in enumerate(lines):
        if '#ifdef CONFIG_KSU_DEBUG' in line and i + 2 < len(lines):
            if 'always allow adb shell' in lines[i+1] or 'ksu_grant_root_to_shell()' in lines[i+2]:
                lines_to_remove.add(i)
                print(f"Found call #ifdef at line {i+1}")
                # 找到对应的 #endif (在 ksu_grant_root_to_shell(); 之后)
                for j in range(i+1, min(i+5, len(lines))):
                    if 'ksu_grant_root_to_shell()' in lines[j] and j+1 < len(lines):
                        if '#endif' in lines[j+1]:
                            lines_to_remove.add(j+1)
                            print(f"Found call #endif at line {j+2}")
                        break
                break
    
    print(f"\nRemoving lines: {sorted([x+1 for x in lines_to_remove])}")
    
    # 创建新内容
    new_lines = []
    for i, line in enumerate(lines):
        if i not in lines_to_remove:
            new_lines.append(line)
        else:
            print(f"Removed line {i+1}: {line.strip()[:50]}...")
    
    with open(filepath, 'w') as f:
        f.writelines(new_lines)
    
    print("\n✓ Patch applied successfully!")
    print("Shell (UID 2000) will have root access by default")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <allowlist.c-path>")
        sys.exit(1)
    
    patch_allowlist(sys.argv[1])
