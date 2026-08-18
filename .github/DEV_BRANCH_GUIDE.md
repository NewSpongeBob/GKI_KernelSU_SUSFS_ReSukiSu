# Dev 分支维护指南

## 分支结构

```
origin/main  ← 上游原作者 (ReSukiSU-GKI) 的代码，只读，不做任何修改
dev          ← 原作者代码 + 我们的自定义功能，线性叠加在最上面
```

## 核心原则

**dev = origin/main + 自定义提交（rebase 在最上面）**

不要用 merge，永远用 rebase/cherry-pick，保持自定义提交干净地叠在原作者代码之上。

## 自定义功能清单（4 个提交）

从下到上的顺序：

1. **feat: 默认给 shell (UID 2000) 授予 root 权限**
   - 新增 `.github/workflows/scripts/grant_shell_root.py`
   - `build.yml` 中添加调用步骤（在 KernelSU 添加之后、SUSFS 补丁之前）
   - 使 shell 用户在非 DEBUG 模式下也默认获得 root 权限

2. **fix: 适配 ReSukiSU 新版 allow_shell 机制**
   - 更新 `grant_shell_root.py`，适配 `allow_shell` 变量（替代旧的 `#ifdef CONFIG_KSU_DEBUG`）

3. **fix: 获取管理器时过滤 main 分支，避免拉取 PR debug 构建**
   - 修改 `.github/workflows/get-manager.yml`，API 请求中加 `branch=main` 过滤

4. **feat: 加回 KPM (Kernel Patch Module) 功能支持**
   - `build.yml` 中添加 `use_kpm` 输入参数（boolean, 默认 true）
   - 添加 KPM 配置写入（`CONFIG_KPM=y`），含 Kconfig 存在性检查
   - 添加编译后 KPM 二进制补丁步骤（`应用 KPM 补丁`）
   - 所有 caller workflow（main.yml, kernel-*.yml, kernel-custom.yml）都传递 `use_kpm` 参数

## 同步上游的操作步骤

```bash
# 1. 拉取上游最新
git fetch origin

# 2. 更新本地 main
git checkout main
git reset --hard origin/main

# 3. 将 dev 的自定义提交 rebase 到最新 main 上
git checkout dev
git rebase main

# 4. 如有冲突，解决后 git rebase --continue
#    冲突通常出现在 build.yml，注意保留自定义功能的同时采用上游新逻辑

# 5. 推送
git push origin main --force-with-lease
git push origin dev --force-with-lease
```

## 冲突解决原则

- **上游改了基础逻辑**（如 SUSFS 修复方式、构建流程）→ 采用上游的新方式
- **我们的自定义功能**（KPM、Shell Root、Manager 过滤）→ 保留，适配上游新代码
- **数据文件**（data/*.json）→ 采用上游的版本数据

## 验证清单

同步完成后确认以下功能存在：

```bash
# Shell Root 脚本存在
test -f .github/workflows/scripts/grant_shell_root.py

# build.yml 中有 Shell Root 调用
grep "grant_shell_root" .github/workflows/build.yml

# build.yml 中有 KPM 输入定义和补丁步骤
grep "use_kpm" .github/workflows/build.yml
grep "应用 KPM 补丁" .github/workflows/build.yml

# Manager 过滤生效
grep "branch=main" .github/workflows/get-manager.yml

# caller workflows 传递 use_kpm
grep "use_kpm" .github/workflows/main.yml

# YAML 语法正确
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/build.yml')); print('OK')"
```
