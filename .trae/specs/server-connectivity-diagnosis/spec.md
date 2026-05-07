# 服务器连接故障全面诊断与修复 Spec

## Why
服务器出现"各种软件打不开、时不时掉线突然连不上"的症状，但本地ping正常。说明网络层(ICMP)可达，但应用层(代理协议/订阅服务)存在问题。需要全面诊断服务状态、配置一致性、证书、CDN、防火墙等，并修复所有发现的隐患。

## What Changes
- 新增 `scripts/diagnose.sh` 服务器端一键诊断脚本（SSH到服务器执行）
- 修复代码中已发现的隐患：
  - config.py CDN_PREFERRED_IPS 包含应被过滤的 104.x.x.x 段（违反 Bug #29 规则）
  - cert_manager.py restart_singbox() 缺少 singbox-cdn 重启（违反 Bug #15 规则）
  - health_check.sh 缺少 UDP 端口检查（HY2 使用 UDP）
  - cdn_monitor.py init_db() 数据库连接未在 finally 中关闭（违反规则14）
  - subscription_service.py 客户端配置缺少 geoip-cn rule_set 定义（route.rules 引用了但 rule_set 未定义）

## Impact
- Affected specs: CDN优选IP策略、服务重启覆盖、健康检查、数据库连接安全、客户端配置完整性
- Affected code: config.py, cert_manager.py, health_check.sh, cdn_monitor.py, subscription_service.py

## ADDED Requirements

### Requirement: 服务器一键诊断脚本
系统 SHALL 提供 diagnose.sh 诊断脚本，覆盖所有可能导致"连不上/掉线"的检查项

#### Scenario: 执行诊断
- **WHEN** 用户在服务器上运行 `bash scripts/diagnose.sh`
- **THEN** 脚本自动检查以下所有项目并输出详细报告：
  1. 三个 systemd 服务运行状态（singbox/singbox-sub/singbox-cdn）
  2. 所有端口监听状态（TCP: 443/8443/2053/2083/2087, UDP: 443）
  3. SSL 证书有效期和文件完整性
  4. iptables 端口跳跃规则是否完整（21000-21200 → 443, UDP+TCP）
  5. 防火墙默认策略（应为 ACCEPT）
  6. CDN 优选IP数据库当前值和更新时间
  7. singbox config.json 语法校验
  8. .env 关键变量完整性（非空检查）
  9. 磁盘空间和内存使用
  10. 最近1小时 singbox 日志中的 ERROR/FATAL
  11. DNS 解析测试（8.8.8.8 和 223.5.5.5）
  12. crontab 定时任务是否完整
  13. BBR/FQ/CAKE qdisc 状态
  14. 从外部测试订阅接口可达性

### Requirement: CDN本地IP池清理
config.py 的 CDN_PREFERRED_IPS SHALL 不包含 104.x.x.x 段IP，与 Bug #29 规则保持一致

#### Scenario: 本地池IP段校验
- **WHEN** 检查 CDN_PREFERRED_IPS 列表
- **THEN** 不应包含 104.16.x.x / 104.17.x.x / 104.18-21.x.x 段的IP（这些段对中国延迟130ms+）

### Requirement: 证书续签后重启覆盖所有服务
cert_manager.py 的 restart_singbox() SHALL 重启 singbox + singbox-sub + singbox-cdn 三个服务

#### Scenario: 证书续签后重启
- **WHEN** cert_manager.py 执行证书续签并调用 restart_singbox()
- **THEN** 必须重启 singbox、singbox-sub、singbox-cdn 三个服务（Bug #15 教训）

### Requirement: 健康检查覆盖UDP端口
health_check.sh SHALL 同时检查 TCP 和 UDP 端口监听状态

#### Scenario: HY2 UDP端口检查
- **WHEN** health_check.sh 检查端口
- **THEN** 除了检查 TCP 443/8443/2053/2083/2087 外，还需检查 UDP 443（HY2/QUIC协议）

### Requirement: 数据库连接安全关闭
cdn_monitor.py 的 init_db() SHALL 在 finally 块中关闭数据库连接

#### Scenario: 数据库异常时连接释放
- **WHEN** init_db() 执行过程中发生异常
- **THEN** 数据库连接必须在 finally 中关闭，防止连接泄漏（规则14）

### Requirement: 客户端配置 rule_set 完整性
subscription_service.py 生成的客户端配置 SHALL 在 route.rule_set 中定义所有 route.rules 引用的 rule_set

#### Scenario: geoip-cn rule_set 定义
- **WHEN** route.rules 中引用了 `geoip-cn` rule_set
- **THEN** route.rule_set 数组中必须包含 geoip-cn 的定义（type=remote, format=binary, url指向SagerNet/sing-geoip）

## MODIFIED Requirements

### Requirement: CDN优选IP本地池（修复104段混入）
CDN_PREFERRED_IPS 列表移除 104.16.123.96、104.16.124.96、104.17.136.90 三个高延迟IP，替换为 162.159/172.64 段实测低延迟IP

### Requirement: 健康检查端口覆盖（增加UDP）
check_ports() 函数增加 UDP 443 端口检查，确保 HY2/QUIC 协议正常监听

### Requirement: 证书续签服务重启（增加singbox-cdn）
restart_singbox() 增加 `systemctl restart singbox-cdn`，与 Bug #15 修复保持一致

## REMOVED Requirements

### Requirement: 无
无需移除任何现有功能
