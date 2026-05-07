# Singbox EPS Node 项目铁律

**版本**: v2.0  
**更新日期**: 2026-04-25

## 🔴 编码前强制检查 (新增)
每次写代码前必须先读取:
1. `project_snapshot.md` - 查看项目快照和避坑记录
2. `AI_DEBUG_HISTORY.md` - 查看历史 Bug 修复方案
3. 本文件所有规则 - 不得跳过任何一条

## 业务红线
改代码不能破坏现有功能；改代码必须同步更新文档

## 动手前
1. 先读 project_snapshot.md 和 AI_DEBUG_HISTORY.md，不读就改=重复犯错
2. 全局搜索影响范围，改 A 文件忘 B 文件=隐藏 Bug

## 硬规矩
3. 禁止硬编码：IP/域名/端口/密码/凭据从.env 读，路径从 config.py 拼
4. 唯一真相源：配置值只在 config.py 定义，其他文件必须 import，禁止各自独立定义
5. 幕后路由出站（如 AI-SOCKS5）不暴露给用户：禁止加入订阅链接/selector/首页节点列表
6. HTTPS 订阅必须用域名+CDN 端口(443/2053/2083/2087/2096/8443)，IP 访问证书不匹配
7. HY2 端口跳跃必须 UDP+TCP 双规则，目标端口与 listen_port 一致
8. CDN 优选 IP 获取：多源聚合+综合评分排序（v2.0.0），不再按 IP 段前缀硬过滤；数据源：vvhan(30 分)→090227(25 分)→001315(15 分)→WeTest(10 分)→IPDB(5 分)→本地池(0 分)；评分=数据源分+排名分+交叉验证分+IP 段参考分；104 段降权(-10)但不丢弃；境外服务器用 DoH(dns.alidns.com)解析
9. SOCKS5 AI 路由规则写死，X/推特/groK 排除，禁止随意改
10. SSL 证书路径自动检测：优先 fullchain.pem，降级 cert.pem
11. 服务重启覆盖所有相关服务：singbox + singbox-sub + singbox-cdn
12. 安装脚本执行顺序：端口跳跃→防火墙→服务启动（防火墙重置会清空 iptables 规则）
13. 订阅链接不加 token 认证，保持原有规则直接访问
14. 数据库连接必须在 finally 中关闭，禁止泄漏
15. 异常信息禁止返回给用户：写日志，返回通用错误
16. ImportError 降级必须定义所有必需变量，否则 NameError 导致服务无法启动
17. 禁止裸 except:必须指定 Exception，否则会吞掉 KeyboardInterrupt/SystemExit

## 改完后
18. 同步更新文档：project_snapshot.md 版本号+1，AI_DEBUG_HISTORY.md 记 Bug，TECHNICAL_DOC.md 记架构变更
19. 测试模拟真实客户端，不用-k/--insecure
20. grep 验证跨文件一致性

## 技术要求
中文注释，报错写 logs/不打印给用户
