# 全局决策工作台模板

这是一个供多个工作流复用的离线决策后台模板。它不是营销页，也不是普通 KPI 大屏，而是把结论、证据、风险、选项、行动、场景模拟和来源审计组织成可复核的判断链。

当前模板采用单文件多视图架构。用户看到的是带固定侧边栏和独立路由的后台管理界面，实际交付仍然是一个可离线打开的 HTML 文件。

## 核心文件

- `report-template.html`：主模板，包含样式、页面结构、示例数据、量化计算和交互逻辑。
- `DESIGN.md`：当前仓库的 UI、数据可视化与交互约束。
- `workflow-template-sync.json`：八工作流激活与同步校验配置。
- `scripts/verify_workflow_template_sync.py`：只读同步校验脚本。

## 使用方式

1. 复制 `report-template.html`，或由工作流生成新的报告 HTML。
2. 替换 `<script type="application/json" id="report-data">` 中的结构化数据。
3. 用浏览器打开报告文件。
4. 使用侧边栏进入决策、证据、风险、执行、模拟和审计页面。
5. 点击顶部“当前主题”，在报告内部选择主题模板，主题会立即作用于全部视图。
6. 点击“导出 PDF”，选择导出当前页面或完整报告。

PDF 导出使用浏览器原生渲染。系统对话框打开后选择“另存为 PDF”。模板不引入外部 PDF 库。

## 路由

- `#/overview`：决策概览
- `#/decision`：决策分析
- `#/evidence`：证据中心
- `#/risk`：风险中心
- `#/execution`：执行中心
- `#/scenario`：场景模拟
- `#/audit`：来源与审计

Hash 路由支持浏览器前进、后退和页面深链接，不使用服务器路由。

## 数据边界

- 模板只读取自身内嵌 JSON。
- 不读取本地来源文件。
- 不发起网络请求。
- 不使用 `localStorage`、`sessionStorage` 或 IndexedDB。
- 不写回任何来源工作流。
- 场景模拟只在页面内存中计算，不保存结果。
- 主题选择只记录在当前报告地址的 hash 中，不改写内嵌报告数据。
- 数据中不得包含密钥、访问令牌、密码或私有凭证。

文件必须保存为 UTF-8。生成 JSON 时，应把用户输入中的 `<` 转义为 `\u003c`，避免意外关闭内嵌脚本节点。

## 数据结构

当前结构版本为 `3.0`，主要字段如下：

```json
{
  "schemaVersion": "3.0",
  "brand": "全局决策系统",
  "subtitle": "多视图决策工作台",
  "title": "工作流决策报告",
  "generatedAt": "2026-07-05T14:30:00+08:00",
  "timezone": "北京时间",
  "dataMode": "真实数据或示例数据",
  "quantitative": {},
  "executive": {},
  "keySignals": [],
  "decisionOptions": [],
  "simulator": {},
  "criteria": [],
  "evidence": [],
  "risks": [],
  "actions": [],
  "assumptions": [],
  "openQuestions": [],
  "sourceIntegrity": []
}
```

## 量化计算

模板只使用预定义、可复核的计算，不执行数据提供者传入的任意公式。

- 方案领先分差：第一名得分减去第二名得分。
- 证据覆盖率：已覆盖证据数除以预期证据数。
- 决策稳定率：对每个默认权重施加 `-10`、`0`、`+10` 点扰动，检查 81 个标准化组合中推荐方案保持第一名的比例。
- 风险暴露值：严重度分值乘以概率分值，其中高为 3、中为 2、低为 1。
- 总风险暴露率：实际风险暴露总值除以当前风险数量对应的最大暴露值。
- 残余风险暴露率：执行缓解动作后的残余暴露总值除以最大暴露值。
- 缓释降幅：原始暴露减去残余暴露，再除以原始暴露。
- 行动可执行率：同时具备行动、负责人、截止时间和成功标准的行动比例。
- 校验通过率：`checkStatus` 为 `passed` 的来源比例。

数字必须有分母、单位、来源或计算口径。没有数据时显示“未提供”，禁止补造趋势、百分比或综合指数。

`quantitative` 用于承载无法从基础条目可靠推导、但上游已经明确提供的量化事实。当前支持：

- `previousConfidence`：上一期置信度，用于计算净变化。
- `decisionRange`：推荐得分或判断区间，使用两元素数字数组。
- `evidenceFreshnessDays`：证据中位新鲜度天数。
- `expectedImpactPercentile`：预期影响所处分位。
- `conflictingEvidence`：存在冲突的证据数量。
- `expiredEvidence`：已过期证据数量。
- `signalWindowHours`：获得下一可观察信号的时间窗口。
- `confidenceTrend`：真实历史置信度序列。只有数据提供者明确给出时才渲染。

这些字段全部可选。模板不会根据视觉需要自动补造历史值。

## 最低接入标准

一个工作流至少应输出：

- `executive`
- `decisionOptions`
- `simulator`
- `evidence`
- `risks`
- `actions`
- `sourceIntegrity`

`decisionOptions[].scores` 应包含与 `simulator.weights[].key` 对应的评分字段，否则场景模拟会以 0 分处理缺失维度。

`actions[].state` 建议使用稳定机器值，例如 `pending`、`planned`、`review`、`blocked`、`completed`。用户可见状态继续放在 `status`。

行动建议同时提供 `nextSignal` 和 `rollbackTrigger`，分别说明下一可观察结果和停止或回滚的触发条件。

风险建议提供 `residualExposure`，范围为 `0-9`。如果任一风险缺失该字段，模板显示“未提供”，并停止计算残余暴露率和缓释降幅。

顶部命令搜索支持点击搜索框或按 `Ctrl K` / `Cmd K` 打开，可检索页面、证据、风险、动作和开放问题。搜索只处理当前 HTML 中的内嵌数据。

`sourceIntegrity[].checkStatus` 建议使用 `passed`、`warning` 或 `failed`。

## 同步边界

主文件是 `report-template.html`。八个工作流通过 `$visual-report-template` 使用它；全局离线备用模板已在用户确认后同步，并与主文件保持一致。

多视图量化模板已于 2026-07-19 在用户确认后同步到全局离线备用模板。八个工作流继续通过 `$visual-report-template` 激活，不在各工作流业务目录复制模板，也不写入任何工作流数据。

只读校验命令：

```powershell
py scripts\verify_workflow_template_sync.py
```

同步完成后，主模板与备用模板必须保持相同 SHA-256；八个工作流的激活标记也必须全部通过校验。
