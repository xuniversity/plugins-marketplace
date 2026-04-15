# Kepler Plugins Marketplace

这是团队内部的插件市场仓库，用于分发可在 **Claude Code** 和 **Codex** 中安装的插件。

## 仓库说明

本仓库采用“通用规范 + 工作流打包”的形式：

- `kepler-rules`：独立的项目编码规范插件
- `riper-workflow`：整套 RIPER 工作流插件（包含 5 个 skills）

当前插件：

- `kepler-rules`
- `riper-workflow`

关键目录结构：

```text
.
├── .claude-plugin/marketplace.json          # Claude Code 市场清单
├── .agents/plugins/marketplace.json         # Codex 市场清单
└── plugins/
    ├── kepler-rules/
    └── riper-workflow/
```

`riper-workflow` 内包含以下 skills：

- `riper-research`
- `riper-plan`
- `riper-execute`
- `riper-review`
- `riper-innovate`

---

## 在 Claude Code 中安装

Claude Code 支持直接从 GitHub 仓库添加 marketplace。

### 方式一：直接使用 GitHub 仓库（推荐）

```bash
claude plugin marketplace add <owner>/<repo>
```

示例：

```bash
claude plugin marketplace add xuniversity/skills-markerplace
```

### 方式二：使用本地路径

```bash
claude plugin marketplace add /绝对路径/skills-markerplace
```

添加成功后，在 Claude Code 插件界面中找到本市场并安装：

- 需要 Kepler 编码规范时：`kepler-rules`
- 需要完整 RIPER 工作流时：`riper-workflow`（一次安装含 5 个 skills）

---

## 在 Codex 中安装

Codex 目前采用仓库内本地市场文件模式（`$REPO_ROOT/.agents/plugins/marketplace.json`）。

### 安装步骤

1. 克隆仓库到本地：

```bash
git clone https://github.com/xuniversity/skills-markerplace.git
```

2. 在 Codex 中打开该仓库目录（作为当前工作目录）。
3. 确保存在市场文件：`.agents/plugins/marketplace.json`。
4. 重启 Codex（修改 marketplace 或 plugin 后也建议重启）。
5. 在 Codex 中打开 `/plugins`，选择 `Kepler Skills Marketplace`，安装所需插件。
6. 推荐安装 `riper-workflow` 以获得完整 RIPER 工作流能力。

---

## 更新与维护

- 拉取最新插件与市场配置：

```bash
git pull
```

- 新增或调整 skill 时，请同时更新对应插件目录和两份 marketplace：
  - `.claude-plugin/marketplace.json`
  - `.agents/plugins/marketplace.json`
