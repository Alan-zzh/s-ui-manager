# CAKE队列启用增强 Spec

## Why

VPS上CAKE队列未启用（降级为FQ），原因是多数VPS使用精简内核，`sch_cake`模块未安装。当前代码只尝试`modprobe sch_cake`，未主动安装缺失的内核模块包。此外，降级时只设置sysctl参数，未通过`tc qdisc replace`实际应用到网卡接口，导致降级也不生效。

## What Changes

* `setup_cake_qdisc()`增加主动安装`linux-modules-extra-$(uname -r)`步骤，获取CAKE内核模块

* 安装模块包后重试`modprobe sch_cake`

* CAKE不可用时，通过`tc qdisc replace`实际应用`fq_pie`到网卡（而非仅设置sysctl）

* 降级时创建`fq-pie-qdisc@{网卡名}` systemd服务确保持久化

* `verify_installation`和`print_summary`增加降级原因提示（内核模块缺失 vs 应用失败）

* `cmd_optimize`子命令同步更新显示信息

## Impact

* Affected code: `install.sh` 中的 `setup_cake_qdisc()`、`set_default_qdisc_fq_pie()`、`verify_installation()`、`print_summary()`、`cmd_optimize()`

* Affected docs: `project_snapshot.md`、`AI_DEBUG_HISTORY.md`、`TECHNICAL_DOC.md`

## ADDED Requirements

### Requirement: CAKE内核模块主动安装

系统在检测到CAKE不可用时，SHALL尝试安装`linux-modules-extra-$(uname -r)`包，安装后重试加载`sch_cake`模块。

#### Scenario: VPS精简内核缺少CAKE模块

* **WHEN** `modprobe sch_cake`失败且`tc qdisc add ... cake`也失败

* **THEN** 自动执行 `apt-get install -y linux-modules-extra-$(uname -r)`，安装后重试`modprobe sch_cake`

* **AND** 如果安装后CAKE可用，继续正常CAKE流程

* **AND** 如果安装后仍不可用，降级到FQ-PIE

### Requirement: FQ-PIE降级实际应用到网卡

当CAKE不可用时，系统SHALL通过`tc qdisc replace dev $MAIN_IF root fq_pie`将FQ-PIE实际应用到主网卡接口，而非仅设置sysctl参数。

#### Scenario: CAKE不可用降级FQ-PIE

* **WHEN** CAKE内核模块不可用或tc qdisc应用失败

* **THEN** 执行 `tc qdisc replace dev $MAIN_IF root fq_pie` 实际应用FQ-PIE到网卡

* **AND** 设置 `default_qdisc=fq_pie` 到sysctl.conf

* **AND** 创建 `fq-pie-qdisc@${MAIN_IF}.service` systemd服务确保持久化

* **AND** 日志输出降级原因（内核模块缺失 or tc应用失败）

### Requirement: 降级原因精确诊断

`verify_installation`和`print_summary` SHALL区分CAKE未启用的具体原因，给出可操作建议。

#### Scenario: CAKE模块缺失

* **WHEN** `tc qdisc show`不包含cake且`modprobe sch_cake`失败

* **THEN** 显示"CAKE队列: 未启用（内核缺少sch\_cake模块，已降级FQ-PIE）"

#### Scenario: CAKE应用失败

* **WHEN** `tc qdisc show`不包含cake但`modprobe sch_cake`成功

* **THEN** 显示"CAKE队列: 未启用（tc qdisc应用失败，已降级FQ-PIE）"

#### Scenario: FQ-PIE降级已生效

* **WHEN** `tc qdisc show`包含fq\_pie

* **THEN** 显示"CAKE队列: 降级为FQ-PIE（内核不支持CAKE，FQ-PIE仍可与BBR配合）"

## MODIFIED Requirements

### Requirement: setup\_cake\_qdisc函数

原函数在CAKE不可用时仅设置sysctl参数返回，现需：

1. 先尝试安装`linux-modules-extra`包获取CAKE模块
2. 降级时通过`tc qdisc replace`实际应用FQ-PIE到网卡
3. 降级时创建systemd持久化服务
4. 记录降级原因供诊断显示

