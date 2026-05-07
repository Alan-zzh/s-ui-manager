# 全量代码审计与自动修复任务清单

- [x] 任务1: 创建基础设施文件
  - [x] 1.1 创建 `ssh_utils.py` 公共模块（SSH连接上下文管理器、命令执行封装、统一异常处理）
  - [x] 1.2 扩展 `audit_config.py`（新增 `get_server(name)` 函数，支持按名称获取单台服务器配置）
  - [x] 1.3 创建 `requirements.txt`（声明 paramiko 等依赖）
  - [x] 1.4 创建 `.env.example`（列出所有必需环境变量及示例值）

- [x] 任务2: 重构 check_*.py 系列脚本（消除硬编码，使用 ssh_utils + audit_config）
  - [x] 2.1 重构 check_cdn.py
  - [x] 2.2 重构 check_config_valid.py
  - [x] 2.3 重构 check_direct_config.py
  - [x] 2.4 重构 check_env.py
  - [x] 2.5 重构 check_file.py
  - [x] 2.6 重构 check_hysteria.py
  - [x] 2.7 重构 check_jp.py
  - [x] 2.8 重构 check_jp_cdn.py
  - [x] 2.9 重构 check_logs.py
  - [x] 2.10 重构 check_mtu.py
  - [x] 2.11 重构 check_network_tuning.py
  - [x] 2.12 重构 check_protocols.py
  - [x] 2.13 重构 check_reality.py
  - [x] 2.14 重构 check_reality_config.py
  - [x] 2.15 重构 check_reality_connections.py
  - [x] 2.16 重构 check_server_status.py
  - [x] 2.17 重构 check_sg_cdn.py
  - [x] 2.18 重构 check_sub.py

- [x] 任务3: 重构 fix_*.py 系列脚本
  - [x] 3.1 重构 fix_all_env.py
  - [x] 3.2 重构 fix_and_check.py
  - [x] 3.3 重构 fix_dns_config.py
  - [x] 3.4 重构 fix_issues.py
  - [x] 3.5 重构 fix_mtu.py
  - [x] 3.6 重构 fix_sg_domain.py
  - [x] 3.7 重构 fix_sg_reality.py
  - [x] 3.8 重构 fix_subscription_cache.py

- [x] 任务4: 重构 deploy_*.py 系列脚本
  - [x] 4.1 重构 deploy_and_restart.py
  - [x] 4.2 重构 deploy_cdn_update.py
  - [x] 4.3 重构 deploy_config.py

- [x] 任务5: 重构其余脚本
  - [x] 5.1 重构 deep_diagnose.py
  - [x] 5.2 重构 deep_diagnose2.py
  - [x] 5.3 重构 deep_diagnose3.py
  - [x] 5.4 重构 final_check.py
  - [x] 5.5 重构 final_test.py
  - [x] 5.6 重构 force_refresh_cdn.py
  - [x] 5.7 重构 full_server_check.py
  - [x] 5.8 重构 get_config.py
  - [x] 5.9 重构 make_mtu_permanent.py
  - [x] 5.10 重构 regenerate_reality.py
  - [x] 5.11 重构 run_cdn.py
  - [x] 5.12 重构 sync_server_ports.py
  - [x] 5.13 重构 test_local_latency.py（无需修改，纯本地测试不含凭据）
  - [x] 5.14 重构 test_sub.py
  - [x] 5.15 重构 update_reality_final.py
  - [x] 5.16 重构 wait_cdn.py

- [x] 任务6: 重构 server_audit*.py 系列（统一使用 ssh_utils）
  - [x] 6.1 重构 server_audit.py（改用 ssh_utils 上下文管理器）
  - [x] 6.2 重构 server_audit2.py
  - [x] 6.3 重构 server_audit3.py
  - [x] 6.4 重构 server_audit4.py
  - [x] 6.5 重构 server_audit5.py

- [x] 任务7: 验证与确认
  - [x] 7.1 对所有修改过的文件进行语法检查（python -m py_compile）— 环境无Python，通过代码审查验证
  - [x] 7.2 确认无硬编码凭据残留（grep 扫描）— 已确认0处残留
  - [x] 7.3 确认所有 SSH 连接使用 try/finally 或上下文管理器 — 已确认
  - [x] 7.4 确认无裸 except 残留 — 已确认0处残留
  - [x] 7.5 生成最终审计报告

# 任务依赖
- 任务1 必须最先完成（所有后续任务依赖 ssh_utils.py 和 audit_config.py）
- 任务2~6 可并行执行（各自独立重构不同脚本）
- 任务7 依赖任务2~6 全部完成
