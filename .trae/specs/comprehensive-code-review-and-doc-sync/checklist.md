## 文档检查
- [x] AI_DEBUG_HISTORY.md 包含 Bug #23 DNS代理查询导致延迟飙升记录
- [x] AI_DEBUG_HISTORY.md 包含 Bug #24 CDN优选IP不自动更新记录
- [x] AI_DEBUG_HISTORY.md 包含 Bug #25 SOCKS5路由规则顺序错误记录
- [x] AI_DEBUG_HISTORY.md 包含 Bug #26 SOCKS5缺少故障转移机制记录
- [x] AI_DEBUG_HISTORY.md 包含预防规则：路由规则顺序规范
- [x] AI_DEBUG_HISTORY.md 包含预防规则：DNS配置规范

## 代码注释检查
- [x] subscription_service.py 路由规则有详细中文注释（说明匹配顺序、故障转移）
- [x] subscription_service.py DNS配置有详细注释（说明detour为什么是direct）
- [x] config_generator.py 路由规则有详细注释
- [x] cdn_monitor.py IP获取策略有详细注释（说明优先级和自动切换逻辑）
- [x] 所有关键配置点都有"为什么这样做"的说明

## 路由规则逻辑检查
- [x] 路由规则顺序：dns → private → 国内直连 → X/推特排除 → AI网站 → final
- [x] X/推特/groK 排除规则在 AI 规则之前（防止先被AI规则匹配）
- [x] X/推特/groK 客户端配置 outbound 为 ePS-Auto（走正常代理）
- [x] AI 网站 outbound 为 ai-residential（走SOCKS5）
- [x] ai-residential selector 包含 ["AI-SOCKS5", "direct"]（故障转移）
- [x] 国内网站 outbound 为 direct（geosite-cn/geoip-cn）
- [x] final 规则为 ePS-Auto（未匹配流量走正常代理）

## DNS配置检查
- [x] dns_proxy (8.8.8.8) 的 detour 为 direct
- [x] dns_direct (dns.alidns.com) 的 detour 为 direct
- [x] 无 DNS 查询走代理的情况

## CDN优选IP更新检查
- [x] 步骤1 为 WeTest.vip 电信优选DNS（外部API优先）
- [x] 步骤2 为 001315电信API（补充）
- [x] 步骤3 为 IPDB API（补充）
- [x] 步骤4 为本地实测IP池（兜底）
- [x] 外部API不再被本地池阻塞

## 跨文件一致性检查
- [x] subscription_service.py 和 config_generator.py 路由规则逻辑一致
- [x] 两个文件的 AI 规则域名列表一致
- [x] 两个文件的排除规则域名列表一致
- [x] 版本号同步更新（config.py v1.0.79, subscription_service.py v1.0.79, cdn_monitor.py v1.0.79）

## 面板功能验证
- [x] generate_singbox_config() 生成的 JSON 格式正确（22项验证全部通过）
- [x] 所有 outbounds 定义完整（11个outbounds：selector+5协议节点+DNS+direct+block+AI-SOCKS5）
- [x] route.rules 顺序正确（dns→private→cn→x_exclusion→ai，5条规则）
- [x] DNS 配置正确（4个DNS服务器，detour全为direct）
- [x] CDN IP 分配逻辑正确（每个协议独立IP）
- [x] 订阅链接生成正确（5个Base64链接）
- [x] sing-box JSON 配置完整性（包含log/dns/inbounds/outbounds/route/experimental全部字段）
