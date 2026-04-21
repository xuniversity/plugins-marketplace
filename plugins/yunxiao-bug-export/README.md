# yunxiao-bug-export

独立技能插件，包含 `yunxiao-bug-export` 单个 skill。

## Skill path

- `skills/yunxiao-bug-export/SKILL.md`

## Dependency requirements

安装 skill 本身可以走 marketplace 一键安装，但运行时仍依赖本机环境：

1. 安装官方 Yunxiao MCP 服务：

```bash
npm install -g alibabacloud-devops-mcp-server
```

2. 在 Codex 配置中声明 `yunxiao` MCP，并提供访问凭证：

```toml
[mcp_servers.yunxiao]
command = "alibabacloud-devops-mcp-server"

[mcp_servers.yunxiao.env]
YUNXIAO_ACCESS_TOKEN = "pt-..."
YUNXIAO_API_BASE_URL = "https://your-org.devops.aliyuncs.com"
```

3. 重启 Codex，让 MCP 和新安装的插件一起生效。

## Notes

- skill 脚本会优先读取当前 shell 的 `YUNXIAO_ACCESS_TOKEN` / `YUNXIAO_API_BASE_URL`
- 如果 shell 里没有，会自动回退到 `~/.codex/config.toml` 的 `[mcp_servers.yunxiao.env]`
- 如果缺少 `alibabacloud-devops-mcp-server`，skill 无法通过官方 MCP 路径导出缺陷
