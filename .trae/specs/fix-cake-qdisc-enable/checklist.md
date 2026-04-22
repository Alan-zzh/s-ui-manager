* [x] CAKE内核模块安装逻辑：`modprobe sch_cake`失败时自动安装`linux-modules-extra-$(uname -r)`并重试

* [x] FQ-PIE降级实际应用：`tc qdisc replace dev $MAIN_IF root fq_pie`执行成功

* [x] FQ-PIE持久化：`fq-pie-qdisc@${MAIN_IF}.service` systemd服务创建并启用

* [x] CAKE不可用时所有降级分支都调用`setup_fq_pie_qdisc()`（而非仅设置sysctl）

* [x] verify\_installation区分3种状态：CAKE已启用 / FQ-PIE降级已生效 / 未优化

* [x] print\_summary显示实际qdisc状态和降级原因

* [x] cmd\_optimize输出显示实际qdisc状态

* [x] project\_snapshot.md版本号更新

* [x] AI\_DEBUG\_HISTORY.md记录Bug原因和修复

* [x] TECHNICAL\_DOC.md更新CAKE降级方案说明
