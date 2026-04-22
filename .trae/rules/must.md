# Singbox EPS Node 项目铁律

## 业务红线
改代码不能破坏现有功能；改代码必须同步更新文档

## 动手前
1. 先读 project_snapshot.md 和 AI_DEBUG_HISTORY.md，不读就改=重复犯错
2. 全局搜索影响范围，改A文件忘B文件=隐藏Bug

## 硬规矩
3. 禁止硬编码：IP/域名/端口/密码/凭据从.env读，路径从config.py拼
4. 唯一真相源：配置值只在config.py定义，其他文件必须import，禁止各自独立定义
5. 幕后路由出站（如AI-SOCKS5）不暴露给用户：禁止加入订阅链接/selector/首页节点列表
6. HTTPS订阅必须用域名+CDN端口(443/2053/2083/2087/2096/8443)，IP访问证书不匹配
7. HY2端口跳跃必须UDP+TCP双规则，目标端口与listen_port一致
8. CDN优选IP优先用WeTest.vip电信优选DNS(ct.cloudflare.182682.xyz)获取，每15分钟更新
9. SOCKS5 AI路由规则写死，X/推特/groK排除，禁止随意改
10. SSL证书路径自动检测：优先fullchain.pem，降级cert.pem
11. 服务重启覆盖所有相关服务：singbox + singbox-sub + singbox-cdn
12. 安装脚本执行顺序：端口跳跃→防火墙→服务启动（防火墙重置会清空iptables规则）
13. 订阅链接不加token认证，保持原有规则直接访问
14. 数据库连接必须在finally中关闭，禁止泄漏
15. 异常信息禁止返回给用户：写日志，返回通用错误
16. ImportError降级必须定义所有必需变量，否则NameError导致服务无法启动
17. 禁止裸except:必须指定Exception，否则会吞掉KeyboardInterrupt/SystemExit

## 改完后
18. 同步更新文档：project_snapshot.md版本号+1，AI_DEBUG_HISTORY.md记Bug，TECHNICAL_DOC.md记架构变更
19. 测试模拟真实客户端，不用-k/--insecure
20. grep验证跨文件一致性

## 技术要求
中文注释，报错写logs/不打印给用户
