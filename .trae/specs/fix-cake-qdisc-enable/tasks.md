# Tasks

- [x] Task 1: 增强 setup_cake_qdisc() — 主动安装CAKE内核模块
  - [x] SubTask 1.1: 在CAKE_SUPPORTED=false分支前，增加安装`linux-modules-extra-$(uname -r)`的逻辑
  - [x] SubTask 1.2: 安装后重试`modprobe sch_cake`，成功则设置CAKE_SUPPORTED=true
  - [x] SubTask 1.3: 记录降级原因变量（CAKE_FAIL_REASON）供后续诊断使用

- [x] Task 2: 增强降级逻辑 — FQ-PIE实际应用到网卡
  - [x] SubTask 2.1: 新增`setup_fq_pie_qdisc()`函数，通过`tc qdisc replace dev $MAIN_IF root fq_pie`实际应用
  - [x] SubTask 2.2: 创建`fq-pie-qdisc@${MAIN_IF}.service` systemd持久化服务
  - [x] SubTask 2.3: 在CAKE不可用的所有分支调用`setup_fq_pie_qdisc()`替代仅设置sysctl

- [x] Task 3: 更新 verify_installation() — 精确诊断CAKE状态
  - [x] SubTask 3.1: 区分"fq_pie已应用"和"完全未优化"两种降级状态
  - [x] SubTask 3.2: CAKE未启用时显示降级原因（模块缺失 vs 应用失败）

- [x] Task 4: 更新 print_summary() — 同步CAKE状态显示
  - [x] SubTask 4.1: 增加fq_pie已应用的显示分支
  - [x] SubTask 4.2: CAKE未启用时显示降级原因

- [x] Task 5: 更新 cmd_optimize() — 同步优化命令输出
  - [x] SubTask 5.1: 优化完成后显示实际qdisc状态（cake/fq_pie/其他）

- [x] Task 6: 同步更新文档
  - [x] SubTask 6.1: project_snapshot.md 版本号+1，记录CAKE增强
  - [x] SubTask 6.2: AI_DEBUG_HISTORY.md 记录Bug和修复
  - [x] SubTask 6.3: TECHNICAL_DOC.md 更新CAKE降级方案说明

# Task Dependencies
- [Task 2] depends on [Task 1] (需要先确定CAKE是否可用，再决定降级方案)
- [Task 3] depends on [Task 2] (需要新的降级逻辑才能正确诊断)
- [Task 4] depends on [Task 2] (同上)
- [Task 5] depends on [Task 2] (同上)
- [Task 6] depends on [Task 1-5] (所有代码改完再更新文档)
