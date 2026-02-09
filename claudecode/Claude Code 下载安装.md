# Claude Code 下载安装 

## 前提条件

- LiteLLM proxy 地址：`https://litellm.xcaoliu.com`
- API Key：`sk-xxxxxxx`
- macOS/Linux/Windows 均支持

## 1. 下载安装 Claude Code

### Windows 安装

#### 方法一：原生安装（推荐）

**前提**：需要先安装 Git（包含 Git Bash）

1. 安装 Git（如果没有）：
   - 下载：https://git-scm.com/downloads/win
   - 或使用 PowerShell 静默安装：
   ```powershell
   Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.2/Git-2.47.1.2-64-bit.exe" -OutFile "$env:TEMP\GitInstaller.exe"
   Start-Process -FilePath "$env:TEMP\GitInstaller.exe" -ArgumentList "/VERYSILENT /NORESTART" -Wait
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

#### 方法二：npm 安装

需要先安装 Node.js 18+：
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

#### 方法三：npm 安装

```bash
npm install -g @anthropic-ai/claude-code
```

### 验证安装

```bash
claude --version
# 输出类似：2.1.37 (Claude Code)
```


## 2. 配置 API 环境变量

### 临时配置（当前终端会话）

**Linux/macOS**：
```bash
export ANTHROPIC_BASE_URL="https://litellm.xcaoliu.com"
export ANTHROPIC_AUTH_TOKEN="sk-xxxxx"
```

**Windows PowerShell**：
```powershell
$env:ANTHROPIC_BASE_URL = "https://litellm.xcaoliu.com"
$env:ANTHROPIC_AUTH_TOKEN = "sk-xxxxx"
```

### 永久配置（推荐）

**Linux/macOS** 编辑 `~/.zshrc` 或 `~/.bashrc`：

```bash
echo 'export ANTHROPIC_BASE_URL="https://litellm.xcaoliu.com"' >> ~/.zshrc
echo 'export ANTHROPIC_AUTH_TOKEN="sk-xxxxxxx"' >> ~/.zshrc
source ~/.zshrc
```

**Windows** 设置系统环境变量：

```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://litellm.xcaoliu.com", "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", "sk-xxxxxxxx", "User")
```



## 3. 启动并验证

### 启动 Claude Code

**重要**：必须使用 `--model` 指定模型，否则会报 401 错误。

```bash
# 使用 Opus 模型
claude --model claude-opus-4.5

# 使用 Sonnet 模型
claude --model claude-sonnet-4.5
```

可用模型：
- `claude-opus-4.5`
- `claude-sonnet-4.5`

### 验证 LiteLLM 连接

在 Claude Code 中运行：

```
/model
```

**成功标志**：显示当前使用的模型名称。

### 切换模型

在 Claude Code 会话中：
```
/model claude-opus-4.5
/model claude-sonnet-4.5
```

## 4. 高级配置（可选）

### 设置默认模型

```bash
# Linux/macOS
export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-sonnet-4.5"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-4.5"
```

```powershell
# Windows PowerShell
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = "claude-sonnet-4.5"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "claude-opus-4.5"
```


## 5. 故障排查

| 问题 | 解决方法 |
| :-- | :-- |
| `claude: command not found` | 检查 PATH 是否包含安装目录，Windows 默认在 `%USERPROFILE%\.local\bin` |
| Windows 提示需要 Git Bash | 安装 Git for Windows：https://git-scm.com/downloads/win |
| `/model` 无响应 | 检查 LiteLLM 是否运行：`curl https://litellm.xcaoliu.com/health` |
| `401 key_model_access_denied` | 必须用 `--model` 指定允许的模型（claude-opus-4.5 或 claude-sonnet-4.5） |
| VS Code 终端无效 | 重启 VS Code 或检查 `settings.json` 语法 |
| 环境变量不生效 | Windows 需重启终端，或使用 `$env:Path` 刷新 |



