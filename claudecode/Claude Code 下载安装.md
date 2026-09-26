# Claude Code 下载安装 

## 前提条件

- LiteLLM proxy 地址：`https://your-litellm.example.com`（替换为你自己的 LiteLLM 地址）
- API Key：`sk-xxxxxxx`
- macOS/Linux/Windows 均支持

## 1. 下载安装 Claude Code

### Windows 安装

#### 方法一：原生安装（推荐）

**建议**：先安装 Git for Windows（包含 Git Bash，Claude Code 的 Bash 工具会用到；未安装时会退回使用 PowerShell）

1. 安装 Git（如果没有），始终使用最新版本：
   - 下载：https://git-scm.com/downloads/win
   - 或使用 winget：
   ```powershell
   winget install --id Git.Git -e
   ```

2. 安装 Claude Code（PowerShell）：
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```

   或使用 CMD：
   ```cmd
   curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
   ```

3. 添加到 PATH（如果提示未在 PATH 中）：
   ```powershell
   $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
   [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;$env:USERPROFILE\.local\bin", "User")
   ```
   然后重启终端。

#### 方法二：WinGet

```powershell
winget install Anthropic.ClaudeCode
```

#### 方法三：npm 安装（旧方式，可选）

仅在无法使用原生安装时使用，需要 Node.js 22+：
```powershell
npm install -g @anthropic-ai/claude-code
```

### macOS/Linux 安装

#### 方法一：原生安装（推荐）

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

#### 方法二：Homebrew（macOS）

```bash
brew install --cask claude-code
```

#### 方法三：npm 安装（旧方式，可选）

仅在无法使用原生安装时使用，需要 Node.js 22+：

```bash
npm install -g @anthropic-ai/claude-code
```

### 验证安装

```bash
claude --version   # 输出版本号即安装成功
claude doctor      # 可选：检查安装和配置
```


## 2. 配置 API 环境变量

### 临时配置（当前终端会话）

**Linux/macOS**：
```bash
export ANTHROPIC_BASE_URL="https://your-litellm.example.com"
export ANTHROPIC_AUTH_TOKEN="sk-xxxxx"
```

**Windows PowerShell**：
```powershell
$env:ANTHROPIC_BASE_URL = "https://your-litellm.example.com"
$env:ANTHROPIC_AUTH_TOKEN = "sk-xxxxx"
```

### 永久配置（推荐）

**Linux/macOS** 写入当前 shell 的配置文件（zsh 用 `~/.zshrc`，bash 用 `~/.bashrc`，下面会自动判断）：

```bash
case "$SHELL" in
  */zsh) RC=~/.zshrc ;;
  *)     RC=~/.bashrc ;;
esac
echo 'export ANTHROPIC_BASE_URL="https://your-litellm.example.com"' >> "$RC"
echo 'export ANTHROPIC_AUTH_TOKEN="sk-xxxxxxx"' >> "$RC"
source "$RC"
```

**Windows** 设置系统环境变量：

```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://your-litellm.example.com", "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", "sk-xxxxxxxx", "User")
```



## 3. 启动并验证

### 启动 Claude Code

模型名必须是 LiteLLM 里配置、且你的 key 有权限访问的名字。二选一：

- 每次用 `--model` 指定；或
- 按第 4 节设置默认模型环境变量，之后直接运行 `claude` 即可。

如果两者都没设置，Claude Code 会使用内置的默认模型名，LiteLLM 里没有这个名字时会返回 `401 key_model_access_denied`。

```bash
# 使用 Opus 模型
claude --model claude-opus-5-5

# 使用 Sonnet 模型
claude --model claude-sonnet-5
```

常用模型名（以你的 LiteLLM 配置为准）：
- `claude-opus-5-5`
- `claude-sonnet-5`
- `claude-haiku-4-5`

### 验证 LiteLLM 连接

`/model` 只切换/显示模型，**不会**测试连接。用一次非交互请求来验证：

```bash
claude -p "hi"
```

**成功标志**：返回模型的回复。在会话中也可以用 `/status` 查看当前模型和 API 地址。

### 切换模型

在 Claude Code 会话中：
```
/model claude-opus-5-5
/model claude-sonnet-5
```

## 4. 高级配置（可选）

### 设置默认模型

设置后不必每次加 `--model`（模型名必须在 LiteLLM 中存在）：

```bash
# Linux/macOS
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-5-5"
export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-sonnet-5"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="claude-haiku-4-5"   # 后台小任务使用
```

```powershell
# Windows PowerShell
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "claude-opus-5-5"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = "claude-sonnet-5"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = "claude-haiku-4-5"
```


## 5. 故障排查

| 问题 | 解决方法 |
| :-- | :-- |
| `claude: command not found` | 检查 PATH 是否包含安装目录，Windows 默认在 `%USERPROFILE%\.local\bin` |
| Windows 提示需要 Git Bash | 安装 Git for Windows：https://git-scm.com/downloads/win |
| `claude -p "hi"` 无响应或报错 | 检查 LiteLLM 是否运行：`curl https://your-litellm.example.com/health` |
| `401 key_model_access_denied` | 用 `--model` 或第 4 节的默认模型变量指定 key 有权限的模型名（如 `claude-opus-5-5` / `claude-sonnet-5`） |
| VS Code 终端无效 | 重启 VS Code 或检查 `settings.json` 语法 |
| 环境变量不生效 | Windows 需重启终端，或使用 `$env:Path` 刷新 |



