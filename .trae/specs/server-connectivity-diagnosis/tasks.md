# Tasks

- [x] Task 1: 创建服务器诊断脚本 diagnose.sh
  - [x] SubTask 1.1: 编写服务状态检查（singbox/singbox-sub/singbox-cdn systemd状态）
  - [x] SubTask 1.2: 编写端口监听检查（TCP: 443/8443/2053/2083/2087 + UDP: 443）
  - [x] SubTask 1.3: 编写SSL证书检查（有效期+文件完整性）
  - [x] SubTask 1.4: 编写iptables端口跳跃规则检查（21000-21200→443, UDP+TCP双协议）
  - [x] SubTask 1.5: 编写防火墙策略检查（INPUT默认ACCEPT）
  - [x] SubTask 1.6: 编写CDN优选IP数据库检查（当前值+更新时间）
  - [x] SubTask 1.7: 编写singbox config.json语法校验
  - [x] SubTask 1.8: 编写.env关键变量非空检查
  - [x] SubTask 1.9: 编写系统资源检查（磁盘+内存）
  - [x] SubTask 1.10: 编写singbox日志ERROR/FATAL扫描（最近1小时）
  - [x] SubTask 1.11: 编写DNS解析测试（8.8.8.8 + 223.5.5.5）
  - [x] SubTask 1.12: 编写crontab定时任务完整性检查
  - [x] SubTask 1.13: 编写BBR/FQ/CAKE qdisc状态检查
  - [x] SubTask 1.14: 编写订阅接口外部可达性测试
  - [x] SubTask 1.15: 汇总诊断报告，标记问题项和修复建议

- [x] Task 2: 修复 config.py CDN_PREFERRED_IPS 包含 104.x.x.x 高延迟IP
  - [x] SubTask 2.1: 移除 104.16.123.96、104.16.124.96、104.17.136.90
  - [x] SubTask 2.2: 替换为 162.159/172.64 段实测低延迟IP
  - [x] SubTask 2.3: 同步更新 cdn_monitor.py ImportError 降级中的 CDN_PREFERRED_IPS

- [x] Task 3: 修复 cert_manager.py restart_singbox() 缺少 singbox-cdn 重启
  - [x] SubTask 3.1: 在 restart_singbox() 中添加 `systemctl restart singbox-cdn`

- [x] Task 4: 修复 health_check.sh 缺少 UDP 端口检查
  - [x] SubTask 4.1: 在 check_ports() 中增加 UDP 443 检查（ss -ulnp）

- [x] Task 5: 修复 cdn_monitor.py init_db() 数据库连接泄漏
  - [x] SubTask 5.1: 将 conn.close() 移入 finally 块

- [x] Task 6: 修复 subscription_service.py 客户端配置缺少 geoip-cn rule_set 定义
  - [x] SubTask 6.1: 经验证 route.rule_set 中已包含 geoip-cn 定义，无需修改

- [x] Task 7: 更新项目文档
  - [x] SubTask 7.1: 更新 project_snapshot.md 版本号和修复记录
  - [x] SubTask 7.2: 更新 AI_DEBUG_HISTORY.md 记录新发现的Bug

# Task Dependencies
- [Task 2] 独立，可并行
- [Task 3] 独立，可并行
- [Task 4] 独立，可并行
- [Task 5] 独立，可并行
- [Task 6] 独立，可并行
- [Task 1] 独立，可并行
- [Task 7] 依赖 Task 2-6 全部完成
