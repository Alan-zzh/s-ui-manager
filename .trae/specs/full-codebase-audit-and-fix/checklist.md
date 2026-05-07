## 基础设施检查
- [x] ssh_utils.py 存在且提供 SSH 连接上下文管理器
- [x] ssh_utils.py 的 `exec_command` 封装包含超时和异常处理
- [x] ssh_utils.py 的连接在 finally 中确保关闭
- [x] audit_config.py 提供 `get_server(name)` 函数
- [x] audit_config.py 支持 'jp'、'jp_old'、'sg'、'other' 名称查询
- [x] requirements.txt 存在且包含 paramiko 依赖
- [x] .env.example 存在且列出所有必需环境变量

## 硬编码消除检查
- [x] 所有 .py 文件中无硬编码的 IP 地址
- [x] 所有 .py 文件中无硬编码的密码
- [x] 所有 .py 文件中无硬编码的用户名
- [x] 所有 .py 文件中无硬编码的端口号
- [x] 所有服务器连接信息均从 audit_config.py 获取

## 异常处理检查
- [x] 无裸 except 语句（必须指定 Exception 或更具体的异常类型）
- [x] 所有 SSH 连接操作有 try/except 包裹
- [x] 所有 exec_command 调用有异常处理
- [x] 异常信息写入 stderr 而非暴露给用户

## 资源管理检查
- [x] 所有 SSH 连接使用 try/finally 或上下文管理器确保关闭
- [x] 所有数据库连接在 finally 中关闭
- [x] 无文件句柄泄漏

## 代码规范检查
- [x] 所有修改过的文件通过代码审查验证语法正确
- [x] 无重复的 SSH 连接代码（统一使用 ssh_utils）
- [x] 无重复的服务器配置代码（统一使用 audit_config）

## 文档检查
- [x] .env.example 与 audit_config.py 中引用的环境变量一致
- [x] requirements.txt 与实际 import 依赖一致
