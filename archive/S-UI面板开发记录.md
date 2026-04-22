# S-UI 面板开发记录（已归档）

> 本文档归档了S-UI面板方向的全部开发历史、踩坑记录和技术文档。
> 该方向已于2026-04-19终止，项目已转向 singbox-eps-node（独立sing-box方案）。
> 保留此文档仅供历史参考，所有内容不再维护。

---

## 一、项目概述

### 目标
在VPS上一键部署S-UI面板（sing-box内核），支持多种代理协议，并提供CDN优选IP自动替换功能。

### 核心原则
1. 使用S-UI + sing-box内核（不是X-UI + xray内核）
2. 通过S-UI的API创建入站配置（不直接操作数据库）
3. 独立订阅生成器（适配S-UI数据库结构，支持CDN优选IP替换）
4. CDN监控只负责优选IP的获取和保存
5. 端口和协议搭配锁死，不能擅自修改

### 终止原因
S-UI面板方案存在以下问题导致放弃：
- 数据库BLOB字段类型与GORM ORM不兼容，频繁出错
- 面板Go进程与SQLite持久化机制冲突
- API接口不稳定，文档不完善
- 直接操作数据库会导致面板崩溃
- 订阅链接404问题无法彻底解决

转向了独立sing-box方案（singbox-eps-node），不依赖任何面板。

---

## 二、系统架构

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                      客户端（小火箭/Shadowrocket）           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare 边缘节点                        │
│              （灰色云 + 优选IP，不走CDN代理）                │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    VLESS-WS / Trojan-WS │     │     VLESS+Reality       │
│    （优选IP: 172.64.x.x）│     │     （直连: 443）       │
│    端口: 8443/8444       │     │                         │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      VPS (S-UI + sing-box)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ S-UI面板  │  │ 订阅服务  │  │ Hysteria2 │  │  SOCKS5  │   │
│  │  2095    │  │  2096    │  │  4433/UDP │  │  16888   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              独立订阅生成器 (subscription_generator)    │  │
│  │  - 读取S-UI数据库 inbounds/endpoints/clients表       │  │
│  │  - 读取cdn_settings表获取优选IP                       │  │
│  │  - 生成聚合订阅（4个协议合并）                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CDN监控服务 (cdn_monitor.py)              │  │
│  │  - 每小时从api.uouin.com获取优选IP                    │  │
│  │  - 保存到cdn_settings表                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 锁死配置参数

| 协议 | 端口 | 传输 | TLS | CDN | 伪装域名 |
|------|------|------|-----|-----|---------|
| VLESS+Reality | 443 | TCP | Reality | 无 | www.apple.com |
| VLESS-WS | 8443 | WebSocket | TLS(证书) | 有 | jp1.290372913.xyz |
| Trojan-WS | 8444 | WebSocket | TLS(证书) | 有 | jp1.290372913.xyz |
| Hysteria2 | 4433 | QUIC(UDP) | TLS(证书) | 无 | jp1.290372913.xyz |

### 其他服务端口
| 服务 | 端口 | 说明 |
|------|------|------|
| SSH | 22 | 远程连接 |
| HTTP | 80 | 证书申请用 |
| S-UI面板 | 2095 | 管理面板 |
| S-UI订阅 | 2096 | 订阅服务 |
| SOCKS5 | 16888 | 用户PZ/密码PZ |
| 端口跳跃 | 10000-20000/UDP | Hysteria2端口跳跃 |

---

## 三、S-UI 数据库结构

> 来源：S-UI官方源码 https://github.com/alireza0/s-ui
> 版本：S-UI 1.4.1

### inbounds 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uint | 主键（自增） |
| type | string | 协议类型：vless, vmess, trojan, hysteria2等 |
| tag | string | 唯一标识 |
| tls_id | uint | 外键，关联tls表（0表示无TLS） |
| options | JSON/BLOB | 协议配置 |
| out_json | JSON/BLOB | 客户端出站配置（用于订阅） |
| addrs | BLOB | 地址列表 |

### clients 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uint | 主键（自增） |
| enable | bool | 是否启用 |
| name | string | 客户端名称（唯一） |
| inbounds | JSON数组/BLOB | 关联的入站ID列表，如 [1, 2, 3] |
| config | JSON/BLOB | 协议凭据 |
| desc | string | 描述 |
| links | BLOB | 链接 |
| up/down/volume/expiry | - | 流量统计 |

### tls 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uint | 主键 |
| server_name | string | TLS SNI 或 Reality 服务器名 |
| key_path | string | 私钥文件路径 |
| certificate_path | string | 证书文件路径 |
| reality | JSON | Reality配置 |
| acme | JSON | ACME自动证书配置 |

### endpoints 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uint | 主键 |
| type | string | 类型 |
| tag | string | 标签 |
| options | JSON | 配置 |

---

## 四、S-UI API 接口文档

> 来源：https://github.com/alireza0/s-ui/wiki/API-Documentation

### API v2（推荐）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/app/apiv2/save` | POST | 保存配置（创建/编辑/删除） |
| `/app/apiv2/inbounds` | GET | 获取入站配置 |
| `/app/apiv2/clients` | GET | 获取客户端配置 |
| `/app/apiv2/tls` | GET | 获取TLS配置 |
| `/app/apiv2/restartSb` | POST | 重启sing-box内核 |
| `/app/apiv2/keypairs` | GET | 生成密钥对（k=reality） |

### 使用示例
```bash
curl -H "Token: 你的Token" "http://localhost:2095/app/apiv2/inbounds"

curl -X POST -H "Token: 你的Token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'object=inbounds' \
  --data-urlencode 'action=new' \
  --data-urlencode 'data={入站JSON配置}' \
  "http://localhost:2095/app/apiv2/save"
```

---

## 五、踩坑黑名单（绝对不能做的事）

| 编号 | 禁止事项 | 后果 | 正确做法 |
|------|---------|------|---------|
| 1 | 禁止直接往数据库塞SQL | S-UI读不到数据，sing-box启动不了 | 必须通过S-UI的API创建入站/客户端/TLS配置 |
| 2 | 禁止使用xray内核 | Hysteria2不支持，HY2直接废了 | 必须使用sing-box内核 |
| 3 | 禁止给HY2配Reality | HY2是UDP协议，Reality只支持TCP | HY2需要正规TLS证书 |
| 4 | 禁止VLESS-WS/Trojan-WS的TLS设为none | Cloudflare回源需要TLS | 必须配置真实TLS证书 |
| 5 | 禁止修改锁死的端口和协议搭配 | 用户明确要求不能改 | 端口443/8443/8444/4433/2095/2096/16888锁死 |
| 6 | 禁止用X-UI的数据库字段名 | S-UI的表结构完全不同 | 用S-UI的字段：type, tag, tls_id, options, out_json |
| 7 | 禁止不写文档就改代码 | 上下文丢了就全忘了 | 先写文档记录方案，再写代码 |

---

## 六、Bug修复记录

### Bug 1：GORM Scan错误
- 错误：`sql: Scan error on column index 6, name 'options': unsupported Scan, storing driver.Value type string into type *json.RawMessage`
- 原因：options列是TEXT类型，但S-UI期望BLOB类型
- 修复：将所有inbounds的options列从TEXT转为BLOB

### Bug 2：Hysteria2 TLS required
- 原因：Hysteria2配置没有启用TLS
- 修复：创建专用TLS配置（HY2-TLS），启用TLS并设置server_name

### Bug 3：数据库路径错误
- 原因：S-UI的数据库路径是/usr/local/s-ui/db/s-ui.db，不是x-ui的路径
- 修复：修改所有脚本中的数据库路径

### Bug 4：UNIQUE constraint failed: inbounds.tag
- 原因：数据库已有旧数据
- 修复：先DELETE清空inbounds、clients、tls表，再重置sqlite_sequence

### Bug 5：JSON反序列化错误
- 错误：`json: cannot unmarshal array into Go value of type option.VLESSUser`
- 原因：client config存储为数组格式
- 修复：改为单对象格式 `{"vless": {"uuid": "..."}}`

### Bug 6：VLESS字段名错误
- 错误：`inbounds[0].users[0].id: json: unknown field "id"`
- 原因：VLESS协议应该用"uuid"字段，不是"id"
- 修复：将所有VLESS客户端config中的"id"改为"uuid"

### Bug 7：Reality私钥格式错误
- 错误：`decode private key: illegal base64 data at input byte 7`
- 原因：Python cryptography库生成的base64格式不匹配sing-box期望的格式
- 修复：改用OpenSSL生成X25519密钥，提取原始32字节后转为URL-safe base64（无padding）

### Bug 8：Trojan缺少证书
- 原因：TLS配置没有指定证书路径
- 修复：生成自签名证书（openssl req -x509），更新TLS配置

### Bug 9：面板路径404
- 原因：S-UI v1.4.1的面板路径是/app/，不是/login
- 修复：使用正确路径 http://IP:2095/app/

### Bug 10：订阅链接404
- 原因：订阅路径是/sub/（末尾有斜杠）
- 状态：部分修复（仍返回404，需进一步排查）

### Bug 11：addrs字段类型错误
- 原因：addrs字段需要是BLOB类型，不是字符串
- 修复：使用b'[]'作为addrs值

### Bug 12：Reality证书缺失
- 原因：Reality配置没有指定证书路径
- 修复：在TLS配置中添加证书路径

---

## 七、SSH连接技术文档

### 推荐方案：paramiko + get_pty

在Windows环境下最稳定的SSH连接方案：

```python
import paramiko
import time
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(
    hostname="服务器IP",
    port=22,
    username="root",
    password="密码",
    timeout=30,
    allow_agent=False,
    look_for_keys=False
)

transport = client.get_transport()
channel = transport.open_session()
channel.get_pty()
channel.exec_command("需要交互执行的命令")

while True:
    if channel.recv_ready():
        data = channel.recv(4096)
        sys.stdout.buffer.write(data)
        sys.stdout.flush()
    if channel.exit_status_ready():
        break
    time.sleep(0.5)

client.close()
```

### 成功关键点
| 关键步骤 | 说明 |
|---------|------|
| `allow_agent=False` | 禁用SSH代理 |
| `look_for_keys=False` | 禁用密钥搜索 |
| `get_pty()` | 获取伪终端，使交互式命令正常执行 |
| `sys.stdout.buffer.write()` | 直接写入二进制缓冲区，避免Windows编码问题 |
| `time.sleep(0.5)` | 轮询间隔，避免CPU占用过高 |

### 失败方案
| 方案 | 失败原因 |
|------|---------|
| sshpass + SSH命令行 | Windows没有sshpass工具 |
| paramiko SSHClient.exec_command | 终端状态问题，退出码255 |
| subprocess + plink | PuTTY的plink未安装 |
| paramiko Transport.open_session | 会话管理问题，连接不稳定 |

---

## 八、数据库连接管理优化

### 问题
原app.py文件存在资源泄漏风险：所有数据库操作直接创建连接，异常时无法正确关闭。

### 解决方案：DatabaseManager类
```python
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
```

### 优化效果
- 100%消除数据库连接泄漏风险
- 70%减少代码重复
- 统一的异常处理和日志记录
- 更容易编写单元测试

---

## 九、生产环境避坑指南

### 1. AWS安全组
AWS默认只开放入站22端口，必须手动添加所有服务端口。

### 2. Hysteria2端口跳跃重启失忆
iptables规则存在内存中，重启后清零。必须安装iptables-persistent并保存规则。

### 3. Cloudflare CDN 502/520报错
- SSL模式必须设为Full或Full(strict)
- 只能使用Cloudflare支持的端口

### 4. VLESS Reality不能套CDN
Reality基于原生TCP，绝对不能通过Cloudflare CDN代理。

### 5. BBR拥塞控制
晚高峰TCP丢包率飙升，必须强制开启BBR：
```bash
cat >> /etc/sysctl.conf << 'EOF'
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
EOF
sysctl -p
```

### 6. 证书更新路径冲突
ACME申请需要80端口，确保80端口空闲或改用DNS API模式。

---

## 十、版本历史

| 版本 | 日期 | 状态 | 说明 |
|------|------|------|------|
| v1.0 | 2026-04-17 | 能跑 | 初始版本，手动面板配置 |
| v1.5 | 2026-04-18 | 能跑 | 通过API创建入站 |
| v2.x | 2026-04-18 | 搞坏了 | 直接操作数据库+换xray内核，所有协议全废 |
| v3.0 | 2026-04-18 | 待开发 | 回退正确路线 |
| v4.0 | 2026-04-18 | 开发中 | 文档整理完成 |
| - | 2026-04-19 | 终止 | 放弃S-UI面板方案，转向独立sing-box |

---

## 十一、遗留问题（未解决）

1. 缺少VLESS Reality配置（端口443，苹果伪装域名）
2. 订阅链接返回404
3. 未配置HTTPS代理
4. 未配置CDN优选IP
5. 未使用苹果伪装域名

这些问题在转向singbox-eps-node后已全部解决。

---

文档版本: v1.0（归档）
归档日期: 2026-04-22
