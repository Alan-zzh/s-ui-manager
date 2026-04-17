# S-UI 自动化配置系统

> S-UI 1.3.6 服务器管理面板自动化配置工具

## 版本信息

- **当前版本**: v1.1.0
- **最后更新**: 2026-04-17
- **S-UI版本**: 1.3.6
- **VPS地址**: 43.159.168.175

## 快速开始

### 1. 配置VPS

SSH登录VPS后，执行以下脚本：

```bash
ssh root@43.159.168.175
# 复制 scripts/setup/setup_vps_final.sh 的内容粘贴执行
```

### 2. 验证配置

```bash
# 检查服务状态
systemctl is-active s-ui

# 检查端口监听
ss -tlnp | grep -E '4431|4432|10001|10002'

# 测试订阅
curl -sk 'https://127.0.0.1:4432/sub/default?format=json'
```

### 3. 访问面板

- **面板地址**: https://43.159.168.175:4431
- **订阅地址**: https://43.159.168.175:4432/sub/default

## 项目结构

```
S-ui/
├── config/                  # 配置文件
│   ├── settings.json       # 主配置
│   ├── config.env          # 环境变量
│   └── solutions.json      # 解决方案索引（重要！）
├── scripts/                 # 可执行脚本
│   ├── setup/              # 安装配置（5个）
│   ├── check/              # 检查诊断（5个）
│   ├── fix/                # 修复脚本（5个）
│   └── test/               # 测试脚本（3个）
├── modules/                 # 功能模块（12个）
├── results/                 # 运行结果
│   └── outputs/            # 输出文件
├── certs/                   # SSL证书
├── database/                # SQLite数据库
├── docs/                    # 文档
│   ├── README.md           # 项目说明
│   ├── CHANGELOG.md        # 更新日志
│   ├── BUGS.md             # BUG记录
│   ├── SOLUTIONS.md        # 解决方案
│   ├── NAMING_CONVENTIONS.md # 命名规则
│   └── VERSION_PROTOCOL.md # 版本协议
└── organize.ps1             # 整理脚本
```

## 配置参数

### 协议配置

| 协议 | 端口 | 密码/UUID | 特性 |
|------|------|-----------|------|
| VLESS | 10001 | a1b2c3d4-e5f6-7890-abcd-ef1234567890 | TLS |
| Trojan | 10002 | TrojanP@ss2024 | TLS |
| Hysteria2 | 10003 | Hy2P@ss2024 | 混淆+端口跳跃 |

### 用户信息

- **用户名**: puzan
- **描述**: 美国线路
- **流量限制**: 无
- **过期时间**: 永久

## 文档导航

| 文档 | 说明 |
|------|------|
| [CHANGELOG.md](docs/CHANGELOG.md) | 版本更新历史 |
| [BUGS.md](docs/BUGS.md) | BUG记录与修复 |
| [SOLUTIONS.md](docs/SOLUTIONS.md) | 解决方案详情 |
| [NAMING_CONVENTIONS.md](docs/NAMING_CONVENTIONS.md) | 命名规则 |
| [VERSION_PROTOCOL.md](docs/VERSION_PROTOCOL.md) | 版本更新协议 |
| [ORGANIZATION_REPORT.md](docs/ORGANIZATION_REPORT.md) | 目录整理报告 |

## 已知问题

- ⚠️ Raw格式订阅返回0字节（JSON/Clash正常）
- ℹ️ IDE报Git分支错误（可忽略，不影响运行）

## 维护说明

### 添加新脚本

1. 按功能分类放入 `scripts/` 子目录
2. 遵循命名规范（见 NAMING_CONVENTIONS.md）
3. 添加文件头部注释

### 更新文档

1. 修复BUG → 更新 BUGS.md
2. 新增方案 → 更新 SOLUTIONS.md
3. 任何变更 → 更新 CHANGELOG.md
4. 状态变更 → 更新 solutions.json

### 清理规则

- 新脚本验证成功后，删除旧版本
- 结果文件定期清理或归档
- 保持scripts目录精简

## 开发者

- **作者**: Alan
- **项目开始**: 2026-04-15
- **最后维护**: 2026-04-17
