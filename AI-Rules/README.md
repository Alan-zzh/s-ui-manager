# AI-Rules 个人全局规则包

**版本**: v1.0  
**作者**: Alan  
**创建日期**: 2024-04-23

---

## 📦 这是什么？

这是一套**跨AI、跨项目、跨系统**的个人AI助手规则包。

**核心功能：**
- Git一键推送（不问、不解释、自动执行）
- 行动优先（做完再汇报）
- 简洁报告（不说废话）

**适用所有AI：**
- Trae AI
- Claude / Claude Code
- Cursor
- GitHub Copilot
- WorkBuddy
- 其他任何AI助手

---

## 🚀 如何使用？

### 场景1：换系统/换电脑
1. 备份整个 `AI-Rules` 文件夹
2. 新系统恢复后，按下方"部署到各AI"说明使用

### 场景2：新项目
1. 复制对应规则文件到新项目
2. AI自动读取并遵守

### 场景3：新AI工具
1. 把 `CLAUDE.md` 或 `.cursorrules` 丢给它
2. 它自然就懂了

---

## 📁 文件说明

| 文件 | 用途 | 部署位置 |
|------|------|----------|
| `personal.md` | Trae AI主规则 | `~/.trae/rules/` 或项目 `.trae/rules/` |
| `CLAUDE.md` | Claude/WorkBuddy通用规则 | 项目根目录 |
| `.cursorrules` | Cursor规则 | 项目根目录 |
| `git-push-rules.md` | Git推送专用规则 | 项目 `.trae/rules/` |
| `.ai-rules.md` | 精简版规则 | 项目根目录 |

---

## ⚡ 一键自动化脚本

| 脚本 | 功能 |
|------|------|
| `一键推送Git.bat` | 双击自动git add+commit+push |
| `同步AI规则.bat` | 自动把规则同步到所有Git项目 |

---

## 🎯 核心规则（Git推送）

**用户说"推送Git"时，AI必须：**

```bash
git add -A
git commit -m "自动更新"
git push
```

**禁止：**
- ❌ 调用MCP GitHub API
- ❌ 询问提交内容
- ❌ 分步确认
- ❌ 解释原理

---

## 📞 维护

规则需要更新时，修改本文件夹内文件，然后执行 `同步AI规则.bat` 同步到各项目。
