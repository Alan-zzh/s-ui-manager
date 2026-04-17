# S-UI 一键安装系统

> S-UI 服务器管理面板自动化配置工具

## 版本信息

- **当前版本**: v2.2.0
- **最后更新**: 2026-04-18
- **作者**: Alan

## 快速开始

### 一键安装

```bash
bash <(curl -sL https://raw.githubusercontent.com/Alan-zzh/s-ui-manager/master/install.sh)
```

### 功能特性

- ✅ 自动切换root权限
- ✅ 系统源更新 + 系统包更新
- ✅ BBR + FQ + CAKE三合一网络加速
- ✅ TCP参数优化
- ✅ 系统限制优化
- ✅ 防火墙自动配置
- ✅ S-UI面板自动安装
- ✅ SSL证书自动申请（Cloudflare API）
- ✅ CDN监控自动配置（每小时自动更新优选IP）
- ✅ systemd服务自动创建
- ✅ 定时任务自动创建

## 更新日志

### v2.2.0 (2026-04-18)

**架构调整**
- 确认使用独立订阅服务方案（方案B）
- S-UI面板负责节点管理，独立订阅服务负责优选IP替换
- 两者互不干扰，面板永不故障

**配置优化**
- CDN监控间隔调整为1小时（3600秒）
- 优选IP自动保存到数据库cdn_settings表
- 订阅生成器读取优选IP生成最终订阅

### v2.1.0 (2026-04-18)

**新增**
- 订阅链接支持域名/IP自动切换
- 支持HTTP/HTTPS协议订阅
- Windows环境编码兼容性修复

**修复**
- 修复订阅链接只能使用域名的问题
- 修复Windows系统下Emoji字符显示异常

### v2.0.0 (2026-04-18)

**新增**
- 合并系统优化和面板安装为单一脚本
- 自动切换root权限功能
- BBR + FQ + CAKE三合一网络加速
- TCP参数优化（高延迟环境适配）
- 系统限制优化（文件描述符、进程数）
- 防火墙自动配置
- SSL证书自动申请（Cloudflare API集成）
- CDN监控服务自动部署
- systemd服务自动创建
- 定时任务自动创建

**修复**
- 修复敏感信息泄露问题（API密钥写死在脚本中）
- 修复GitHub仓库历史记录包含敏感信息
- 修复CDN监控模块依赖问题

**优化**
- 优化脚本执行顺序（系统优化 → 面板安装 → 证书配置 → 监控部署）
- 优化错误提示信息
- 优化日志输出格式

### v1.0.0 (2026-04-17)

**初始版本**
- 基础S-UI面板安装
- CDN监控模块
- 订阅生成功能

## 技术架构

### 完整工作流程

```
第一步：安装S-UI面板
  └── 配置节点（VLESS-Reality、VLESS-WS、Trojan-WS、Hysteria2）
  └── 配置TLS/Reality证书
  └── 创建用户

第二步：CDN监控自动运行（后台）
  └── 每小时从网站获取优选IP
  └── 保存到数据库（cdn_settings表）
  └── 每天自动更新

第三步：订阅生成（独立服务）
  └── 读取S-UI面板的节点配置
  └── 读取CDN监控的优选IP
  └── 生成订阅链接（用优选IP替换原地址）
```

### 网络加速方案

| 组件 | 作用 | 配置 |
|------|------|------|
| **BBR** | 智能调节发送速率 | `net.ipv4.tcp_congestion_control=bbr` |
| **FQ** | 公平分配带宽 | `net.core.default_qdisc=fq` |
| **CAKE** | 主动队列管理，集成FQ+PIE | `tc qdisc replace dev eth0 root cake` |

### 系统优化

- TCP缓冲区优化（应对高延迟）
- 文件描述符限制优化（65535）
- 进程数限制优化（65535）
- 防火墙端口开放（22, 80, 443, 6868）

## 开发历史

### 调试记录

1. **CDN监控模块开发**
   - 从网站获取优选IP排名
   - 自动分配不同IP给VLESS-WS和Trojan-WS
   - 保存到数据库供订阅生成使用

2. **订阅生成器开发**
   - 读取S-UI数据库节点配置
   - 读取CDN监控优选IP
   - 生成Base64/JSON订阅链接
   - 支持域名/IP自动切换

3. **系统优化集成**
   - BBR + FQ + CAKE三合一加速
   - TCP参数优化
   - 系统限制优化
   - 防火墙自动配置

4. **SSL证书自动申请**
   - 使用Cloudflare API
   - acme.sh自动申请
   - 证书自动续期

### 常见问题修复

- 修复Reality协议解析错误
- 修复Hysteria2 JSON解析错误
- 修复Windows GBK编码问题
- 修复数据库字段不匹配问题

## 常见问题

### 1. 脚本运行失败？

确保使用root用户运行，或脚本会自动切换权限。

### 2. SSL证书申请失败？

检查Cloudflare API配置是否正确。

### 3. CDN监控服务未启动？

```bash
systemctl status s-ui-cdn-monitor
journalctl -u s-ui-cdn-monitor -f
```

### 4. 优选IP未更新？

```bash
# 查看CDN监控日志
cat /var/log/cdn-monitor.log

# 手动运行一次
cd /opt/s-ui-manager && python3 cdn_monitor.py
```

## 开发者

- **作者**: Alan
- **项目开始**: 2026-04-15
- **最后维护**: 2026-04-18

## 节点配置说明

> 所有节点端口均从S-UI数据库自动读取，无需手动配置

| 协议 | 连接方式 | CDN | 端口 |
|------|---------|-----|------|
| **VLESS+Reality** | 直连 | 无 | 自动读取 |
| **VLESS-WS** | CDN | 优选IP | 443 |
| **Trojan-WS** | CDN | 优选IP | 443 |
| **Hysteria2** | 直连 | 无 | 自动读取 |

## 订阅功能

### 订阅链接格式

- **Base64订阅**: `https://你的域名/sub/编码字符串`
- **JSON订阅**: `https://你的域名/sub-json/编码字符串`
- **IP订阅**: `https://服务器IP/sub/编码字符串`

### 配置项

在 `.env` 文件中配置：

```bash
USE_HTTPS=true          # 是否使用HTTPS（默认true）
SUB_DOMAIN=你的域名     # 订阅使用的域名（留空则使用服务器IP）
```

### 智能切换逻辑

- 配置了域名 → 使用域名
- 没配置域名 → 使用服务器IP
- HTTP/HTTPS 都支持