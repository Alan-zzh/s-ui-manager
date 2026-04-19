# S-UI 全自动配置项目

## 项目概述
这是一个用于全自动配置 S-UI 面板 v1.4.1 的项目，支持多种协议配置和CDN优选IP。

## 功能特性
- ✅ 全自动配置 S-UI 面板
- ✅ 支持 VLESS Reality、VLESS WS、Trojan WS、Hysteria2 协议
- ✅ 自动生成 TLS 证书
- ✅ 支持 Hysteria2 端口跳跃
- ✅ 支持 CDN 优选 IP
- ✅ 一键恢复脚本

## 技术参数
- **S-UI 版本**：v1.4.1
- **Sing-Box 版本**：v1.13.4
- **数据库**：SQLite
- **面板端口**：2095
- **订阅端口**：2096

## 快速开始

### 1. 安装 S-UI
```bash
# 一键安装 S-UI
bash <(curl -Ls https://raw.githubusercontent.com/gulucat/s-ui/master/install.sh)
```

### 2. 配置服务
运行配置脚本：
```bash
python SUI全自动配置_正确版.py
```

### 3. 配置 Hysteria2 端口跳跃
```bash
python 配置Hysteria2端口跳跃.py
```

### 4. 访问面板
- **面板地址**：http://IP:2095/app/
- **登录凭据**：admin / admin
- **订阅地址**：http://IP:2096/sub/

## 入站配置

| 协议 | 端口 | 路径 | 状态 |
|------|------|------|------|
| VLESS Reality | 443 | - | 需配置 |
| VLESS WS | 8080 | /vless | ✅ 运行中 |
| Trojan WS | 8081 | /trojan | ✅ 运行中 |
| Hysteria2 | 4433 | - | ✅ 运行中 |

## 客户端配置
- **名称**：JP（或其他地区代码）
- **描述**：puzan
- **支持协议**：VLESS Reality、VLESS WS、Trojan WS、Hysteria2

## 问题排查

### 常见错误
1. **数据库 BLOB 字段错误**：运行 `修复TLS配置6.py`
2. **订阅链接 404**：检查 settings 表配置
3. **TLS 证书问题**：确保证书路径正确
4. **Hysteria2 启动失败**：检查 TLS 配置

### 日志查看
```bash
# 查看 S-UI 日志
journalctl -u s-ui -f

# 查看端口监听
ss -tlnp | grep sui
```

## 项目文件
- `SUI全自动配置_正确版.py`：完整配置脚本
- `修复TLS配置6.py`：修复 TLS 配置
- `配置Hysteria2端口跳跃.py`：配置端口跳跃
- `检查S-UI配置结构.py`：检查服务状态
- `S-UI_Bug文档.txt`：Bug 修复记录
- `技术文档.md`：技术说明文档
- `project_snapshot.md`：项目状态快照

## 注意事项
1. 请确保服务器防火墙已开放所需端口
2. 配置 CDN 时需在 Cloudflare 中设置优选 IP
3. 定期备份数据库文件
4. 保持 S-UI 版本更新

## 许可证
MIT License
