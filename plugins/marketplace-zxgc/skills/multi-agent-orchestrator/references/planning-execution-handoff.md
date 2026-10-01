# 规划生产、执行消费：多智能体交接

由requirement-to-plan与code-exec共同按需读取。执行入口仅保留code-exec。适用于已决定采用多智能体的Codex工作流；主代理负责语义映射、权限判断和状态写入，本说明不提供后台调度或自然语言自动转换器。

## 三种真源的边界

- 同名plan当前active_module_key：需求意图、方案、Todo与验收的唯一规划真源。
- workflow JSON：从当前模块生成的执行表示；字段遵循相邻workflow-contract.md，不自行增加schema字段。发生冲突先回到plan判定，不让JSON成为另一份需求。
- 同名task与执行状态：已发生的派工、attempts、失败、验收及产物事实，不能随计划再生成而清零。

模型与重试/上下文上限继续来自code-exec既有机器策略。类型和难度路由由orchestrate.py负责，任何入口都不维护另一套模型表。

## 规划生产者：requirement-to-plan

1. 先判断收益：仅有一个紧耦合修改、小型查询或共享文件无法拆分时选择single_agent，记录理由；不要为了展示团队而硬拆五类agent。可以独立产生可验收产物且上下文边界清楚时选择multi_agent。
2. 有授权的独立证据采集可以并行；主代理保留需求歧义、风险、架构取舍及最终计划。每个取证包只给问题、必要引用和输出约定。先复用当前证据，过期或缺口才重查，不重新扫描全部技能。
3. 在当前plan模块内为Todo给出稳定id、kind、difficulty、risk、dependencies、allowed_files、evidence_refs、acceptance和constraints。模型理由写能力档位及原因，不写硬编码模型名；字段名与相邻合同一致。主代理负责难度/风险判断，不接受待执行任务自行声明低风险作为授权。
4. 读写次序必须表达：修改前分析是writer依赖reader，修改后评测是reader依赖writer。目标不明确、同文件不能拆清或需要多个任务共享可变结构时先串行/主代理裁决。
5. 在模块内给出handoff摘要：plan绝对路径、active_module_key、独立product_context路径、workflow/state所在文件、稳定Todo到task id对应关系、受影响文件、授权来源和恢复边界。计划证据足以支撑难度/类型才输出执行表示。
6. workflow中的available_models和capacity在执行前按当前工具核验；规划时若未知应在plan记录unknown，暂不生成可调度JSON，不编造一个模型清单通过校验。
7. 已生成的未来写入workflow若未授权保持confirmed=false。规划阶段只读侦察若有单独明确授权，可使用独立read-only合同，不能把侦察的confirmed=true复制到未来写入任务。

### 可审阅的交接样例

| Todo/task id | 类型与难度 | 依赖 | 允许范围 | 验收 |
|---|---|---|---|---|
| inspect | query / low | 无 | 只读当前模块源文件 | 定位问题并附引用 |
| fix | implementation / medium | inspect | 计划列明的具体文件 | 目标行为与回归证据 |
| verify | evaluation / high | fix | 主代理质量判断 | 需求符合且无未关闭关键缺陷 |

这里的inspect完成不等于通过；只有主代理accepted才允许fix。verify不因fix自述“通过”而省略。执行表示仍按既有schema生成，不把此Markdown表当可调用参数。

## 执行消费者：code-exec

1. 从当前router取得独立product_context与模块身份；用既有product_scope恢复核验。读取当前plan模块与task状态，主代理逐项核对Todo/task映射、文件范围、依赖、验收和授权，再消费workflow，不重新从零拆解。
2. 在任务证据目录记录handoff事实：plan/workflow的SHA256、授权消息摘要及稳定映射。哈希是变化检测线索，不是权限来源；这是一项主代理检查，现有脚本没有自动检测plan漂移。
3. 发现哈希变化时先判断归属：同文件其他模块变化不重置本模块；当前模块目标/文件/依赖/验收变化时，更新对应执行表示，保留已有attempts和产物历史。仅对受影响节点及其下游重新判断验收有效性；不能以旧accepted放行不再匹配的产物，也不能清零失败次数。新增范围或高风险边界按用户授权规则处理。
4. running任务先恢复真实agent状态，无法确认时等待或交主代理诊断，不重新spawn。failed任务先检查失败原因；可重试时保留attempts，现有compiler决定是否超限。结构错误或不确定风险不能通过改低difficulty、删依赖、扩大allowed_files来放行。
5. 调用现有orchestrate.py生成当前wave。ready才允许派工；waiting是等待运行/验收，blocked需要明确原因；complete要求全部passed且accepted。主代理更新状态前保留快照，保证一份workflow只有一个写入负责人。
6. 派工前登记running和真实尝试次数，传最小必要上下文与fork_turns=none。按当前工具能力使用编译器参数；模型/角色不支持时返回主代理，不隐式另开CLI或API。子代理不得自行递归分派。
7. 回收固定摘要summary/artifacts/tests/risks/escalation_reason；先核对需求与文件范围，再做质量判断，主代理才可accepted。输入引用不是权限沙箱；必要时核对实际变更，不能只听子代理自述。
8. 已确认范围内继续验证、修复和下一波，不在每个Todo重复询问。无工具支持或不值得并行时由主代理继续同一Todo，task记录实际执行方式，不能谎称模型降档成功。

## 上下文与成本约束

复用plan的证据摘要和精确引用；仅为发生变化的部分重新取证。子代理不读整个会话、全部plan或全部同伴输出。消息超过既有字符上限时由主代理重新提炼，不静默删除约束；字符上限不等同token预算。

统计口径必须包括主代理规划/整合、所有子调用和失败重试。现有usage仅为上报任务小计，完整成本与节省没有配对证据时仍unknown。共享交接可以减少重复步骤，不能仅凭少写文档或少用agent就宣称总token降低。

## 验证与可执行边界

编排器确定性测试覆盖DAG、未确认/未验收、冲突和重试保护；规划与执行的指针和本说明用文档差异检查。语义拆解、计划漂移归因、授权与主代理质量裁决属于工作流职责，本轮没有新增强制执行器。验证报告必须分别写清脚本已强制的约束和仅靠主代理遵循的约定。

本说明不修改AGENTS、默认模型、权限、router算法或外部runtime；只补规划与执行的共同交接。既有主需求与历史执行证据保留，增量融合回同一个active_module_key。
