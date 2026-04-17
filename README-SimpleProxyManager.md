# SimpleProxyManager - 简单代理管理器

**简单、稳定、无面板的代理解决方案**

---

## 📋 项目简介

SimpleProxyManager 是一个轻量级的代理管理方案，借鉴了 Hiddify 的设计理念，但更简单、更稳定。

### 核心特点

- ✅ **无 Web 面板** - 避免了面板带来的不稳定和安全问题
- ✅ **一键部署** - 一条命令安装 sing-box 核心
- ✅ **本地规则管理** - 电脑上有傻瓜式 Web 界面管理规则
- ✅ **订阅生成** - 自动生成兼容各种客户端的订阅

---

## 📁 项目结构

```
SimpleProxyManager/
├── server/              # 服务端（部署到 VPS）
│   ├── install.sh       # 一键安装脚本
│   └── config.json      # sing-box 配置
├── client/              # 本地（你电脑上）
│   ├── app.py          # 规则管理 Web 界面
│   ├── templates/       # Web 模板
│   └── start.bat       # Windows 启动
├── shared/              # 共享脚本
│   └── subscription_generator.py
└── README.md            # 说明文档
```

---

## 🚀 快速开始

### 1. 服务端部署（VPS）

在你的 VPS 上执行：

```bash
# 一键安装
bash <(curl -Ls https://你的域名/install.sh)
```

### 2. 本地规则管理（你电脑上）

```bash
# Windows
双击 client/start.bat

# 浏览器打开
http://127.0.0.1:5000
```

---

## 📄 许可证

MIT License