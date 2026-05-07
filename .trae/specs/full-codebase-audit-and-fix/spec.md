# 全量代码审计与自动修复 Spec

## Why
项目根目录下 45+ 个 Python 运维脚本普遍存在硬编码密码/IP、SSH连接资源泄漏、缺少异常处理、大量重复代码等严重问题。需要系统性审查并自动修复，使代码符合项目铁律（must.md）中"禁止硬编码""唯一真相源""禁止裸except"等规则。

## What Changes
- 新增 `ssh_utils.py` 公共模块：封装 SSH 连接/执行/关闭逻辑，统一资源管理和异常处理
- 扩展 `audit_config.py`：覆盖所有服务器配置（JP/JP_OLD/SG），提供统一的配置获取接口
- 重构所有 `check_*.py`、`fix_*.py`、`deploy_*.py`、`deep_diagnose*.py`、`final_*.py`、`full_*.py`、`get_config.py`、`make_mtu_permanent.py`、`regenerate_reality.py`、`run_cdn.py`、`sync_server_ports.py`、`test_*.py`、`update_reality_final.py`、`wait_cdn.py` 等脚本，消除硬编码凭据，改用 audit_config + ssh_utils
- 新增 `requirements.txt`：声明 paramiko 等依赖
- 新增 `.env.example`：记录所有必需环境变量
- 修复所有裸 except、资源泄漏、缺少错误处理的问题

## Impact
- Affected specs: 服务器连接配置、SSH操作模式
- Affected code: 所有根目录下的 Python 脚本（约 45 个文件）

## ADDED Requirements

### Requirement: 公共SSH工具模块
系统 SHALL 提供 `ssh_utils.py` 模块，封装 SSH 连接创建、命令执行、连接关闭的标准流程

#### Scenario: 脚本需要SSH连接服务器
- **WHEN** 任何脚本需要通过SSH连接远程服务器
- **THEN** 必须通过 `ssh_utils.py` 提供的上下文管理器或函数获取连接，确保连接在 finally 中关闭

### Requirement: 统一配置管理
所有脚本 SHALL 从 `audit_config.py` 获取服务器连接信息，禁止在脚本中硬编码IP/密码/端口

#### Scenario: 脚本需要服务器配置
- **WHEN** 脚本需要连接某台服务器
- **THEN** 必须调用 `audit_config.py` 提供的函数获取 host/port/username/password，不得硬编码

### Requirement: 异常处理规范
所有脚本 SHALL 对 SSH 操作和远程命令执行进行异常捕获，禁止裸 except，禁止吞没异常

#### Scenario: SSH操作失败
- **WHEN** SSH连接或命令执行失败
- **THEN** 必须捕获具体异常（如 paramiko.SSHException、socket.error），记录错误日志并优雅退出

### Requirement: 依赖声明
项目 SHALL 包含 `requirements.txt` 文件，声明所有 Python 依赖

#### Scenario: 新环境部署
- **WHEN** 在新环境中部署项目
- **THEN** 执行 `pip install -r requirements.txt` 即可安装所有依赖

### Requirement: 环境变量示例
项目 SHALL 包含 `.env.example` 文件，列出所有必需的环境变量及示例值

#### Scenario: 新用户配置环境
- **WHEN** 新用户需要配置运行环境
- **THEN** 复制 `.env.example` 为 `.env` 并填入实际值即可

## MODIFIED Requirements

### Requirement: audit_config.py 服务器配置（扩展）
`audit_config.py` SHALL 支持按名称获取单台服务器配置，提供 `get_server(name)` 函数，支持 'jp'、'jp_old'、'sg' 等名称

## REMOVED Requirements

### Requirement: 各脚本独立硬编码服务器信息
**Reason**: 违反项目铁律"禁止硬编码"和"唯一真相源"规则，且维护困难
**Migration**: 统一迁移到 audit_config.py + .env 文件
