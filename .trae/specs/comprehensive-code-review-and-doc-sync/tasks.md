# 全面代码审查与文档同步任务清单

- [x] 任务1: 完善AI_DEBUG_HISTORY.md文档
  - [x] 1.1 新增Bug #23 DNS代理查询导致延迟飙升
  - [x] 1.2 新增Bug #24 CDN优选IP不自动更新
  - [x] 1.3 新增Bug #25 SOCKS5路由规则顺序错误导致X/推特走错
  - [x] 1.4 新增Bug #26 SOCKS5缺少故障转移机制
  - [x] 1.5 新增预防规则：路由规则顺序和DNS配置规范

- [x] 任务2: 代码注释补充
  - [x] 2.1 subscription_service.py 路由规则添加详细注释
  - [x] 2.2 subscription_service.py DNS配置添加详细注释
  - [x] 2.3 config_generator.py 路由规则添加详细注释
  - [x] 2.4 cdn_monitor.py IP获取策略添加详细注释
  - [x] 2.5 所有关键配置点添加"为什么这样做"的说明

- [x] 任务3: 全方位代码逻辑审查
  - [x] 3.1 路由规则顺序审查（确保匹配优先级正确）
  - [x] 3.2 DNS配置审查（确保detour都是direct）
  - [x] 3.3 CDN优选IP更新机制审查（外部API优先）
  - [x] 3.4 SOCKS5故障转移审查（selector包含direct）
  - [x] 3.5 X/推特/groK排除规则审查（位置在AI规则之前）
  - [x] 3.6 国内直连规则审查（geosite-cn/geoip-cn）
  - [x] 3.7 最终路由final规则审查（ePS-Auto）
  - [x] 3.8 跨文件一致性审查（subscription_service.py vs config_generator.py）

- [x] 任务4: 面板功能验证
  - [x] 4.1 验证路由规则生成的JSON配置格式正确
  - [x] 4.2 验证所有outbounds定义完整
  - [x] 4.3 验证route.rules顺序正确
  - [x] 4.4 验证DNS配置正确
  - [x] 4.5 验证CDN IP分配逻辑正确
  - [x] 4.6 验证订阅链接生成正确
  - [x] 4.7 验证sing-box JSON配置完整性

- [x] 任务5: 更新版本号
  - [x] 5.1 config.py 版本号更新 (v1.0.79)
  - [x] 5.2 subscription_service.py 版本号更新
  - [x] 5.3 cdn_monitor.py 版本号更新

# 任务依赖
- 任务1 和 任务2 可并行
- 任务3 依赖 任务2（注释完善后更容易审查）
- 任务4 依赖 任务3（审查完成后再验证）
- 任务5 最后执行
