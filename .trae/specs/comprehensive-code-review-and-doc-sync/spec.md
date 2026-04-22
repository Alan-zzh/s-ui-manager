# 全面代码审查与文档同步 Spec

## Why
最近两次修复暴露出多处隐藏Bug：DNS代理查询走错、CDN优选IP不自动更新、SOCKS5路由规则顺序错误、X/推特/groK排除规则位置错误、故障转移机制缺失。这些问题说明代码注释不足、文档不完整、缺乏系统性审查。需要全面记录所有踩坑经验、补充代码注释、全方位验证系统逻辑。

## What Changes
- AI_DEBUG_HISTORY.md：新增Bug #23~#26及预防规则
- 代码注释补充：所有关键配置点添加"为什么这样做"的详细说明
- 全面审查：路由规则逻辑、DNS配置、CDN更新机制、SOCKS5故障转移、排除规则
- 面板功能验证：确认每个模块正常工作

## Impact
- Affected specs: 路由规则、DNS配置、CDN监控、SOCKS5故障转移
- Affected code: subscription_service.py, config_generator.py, cdn_monitor.py, config.py, AI_DEBUG_HISTORY.md

## ADDED Requirements

### Requirement: Bug经验文档化
系统 SHALL 将所有历史Bug经验记录到 AI_DEBUG_HISTORY.md，防止重复踩坑

#### Scenario: 每次修复Bug后
- **WHEN** 修复一个Bug
- **THEN** 必须在 AI_DEBUG_HISTORY.md 中记录：现象、根因、修复方案、预防措施

### Requirement: 关键代码注释
所有关键配置和路由规则 SHALL 包含详细中文注释，说明设计意图和原理

#### Scenario: 路由规则注释
- **WHEN** 编写路由规则
- **THEN** 必须注释：规则作用、匹配顺序、故障转移机制

### Requirement: 全面代码审查
系统 SHALL 进行全方位审查，覆盖所有模块和逻辑

#### Scenario: 审查完成
- **WHEN** 执行全面审查
- **THEN** 必须验证：路由逻辑正确、DNS配置正确、CDN自动更新、故障转移生效、排除规则生效

## MODIFIED Requirements

### Requirement: SOCKS5路由规则（已修复）
X/推特/groK 排除规则必须放在 AI 规则之前，outbound 设为 ePS-Auto（客户端）或 direct（服务端）

### Requirement: DNS代理配置（已修复）
dns_proxy 的 detour 必须为 direct，不能走 ePS-Auto

### Requirement: CDN优选IP更新（已修复）
WeTest.vip 外部API必须优先于本地池，确保每小时获取最新最快IP

### Requirement: SOCKS5故障转移（已修复）
ai-residential selector 必须包含 direct 作为fallback

## REMOVED Requirements

### Requirement: 旧版本地池优先策略
**Reason**: 本地池永远优先导致外部API永不触发，IP不更新
**Migration**: 改为外部API优先+本地池兜底
