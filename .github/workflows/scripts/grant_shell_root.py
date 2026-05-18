#!/usr/bin/env python3
"""
修改 allowlist.c：
1. 在 ksu_grant_root_to_shell() 中设置 use_default = true
2. 移除调用处的 #ifdef CONFIG_KSU_DEBUG，使函数实际被调用
使 shell (UID 2000) 默认获得 root 权限，且在 Manager 中显示为"默认"
"""

import sys

def patch_allowlist(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 修改1：在 profile 定义中添加 use_default = true
    old_code1 = '''#ifdef CONFIG_KSU_DEBUG
static void ksu_grant_root_to_shell(void)
{
    struct app_profile profile = {
        .version = KSU_APP_PROFILE_VER,
        .allow_su = true,
        .current_uid = 2000,
    };
    strcpy(profile.key, "com.android.shell");
    strcpy(profile.rp_config.profile.selinux_domain,
           KSU_DEFAULT_SELINUX_DOMAIN);
    ksu_set_app_profile(&profile);
}
#endif'''
    
    new_code1 = '''static void ksu_grant_root_to_shell(void)
{
    struct app_profile profile = {
        .version = KSU_APP_PROFILE_VER,
        .allow_su = true,
        .current_uid = 2000,
        .rp_config.use_default = true,
    };
    strcpy(profile.key, "com.android.shell");
    strcpy(profile.rp_config.profile.selinux_domain,
           KSU_DEFAULT_SELINUX_DOMAIN);
    ksu_set_app_profile(&profile);
}'''
    
    if old_code1 not in content:
        print("ERROR: Could not find the profile definition!")
        sys.exit(1)
    
    content = content.replace(old_code1, new_code1, 1)
    
    # 修改2：移除调用处的 #ifdef CONFIG_KSU_DEBUG 和 #endif
    old_code2 = '''#ifdef CONFIG_KSU_DEBUG
    // always allow adb shell by default
    ksu_grant_root_to_shell();
#endif'''
    
    new_code2 = '''// always allow adb shell by default
    ksu_grant_root_to_shell();'''
    
    if old_code2 not in content:
        print("ERROR: Could not find the function call!")
        sys.exit(1)
    
    content = content.replace(old_code2, new_code2, 1)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("✓ Patch applied successfully!")
    print("Shell (UID 2000) will have root access with default profile")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <allowlist.c-path>")
        sys.exit(1)
    
    patch_allowlist(sys.argv[1])
