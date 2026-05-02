---
name: ingest
description: 将 raw/ 目录原始资料编译到 wiki/（sources/entities/concepts），完成后归档到 raw/09-archived/。支持 `/ingest`（扫描所有未归档文件）或 `/ingest <path>`（处理指定文件）。触发词：摄取/导入/收入资料、把论文 PDF 放入 raw/02-papers/ 生成 Obsidian 知识网络。禁止读取 raw/09-archived/。
user-invocable: true
---

# ingest 技能

## 目录约定

`raw/` 是收件箱，`wiki/` 是编译输出层。

| 目录 | 用途 |
|---|---|
| `raw/01-articles/` | 网页剪藏 Markdown |
| `raw/02-papers/` | 论文 PDF |
| `raw/09-archived/` | 已处理归档（**禁止读取**） |
| `wiki/sources/` | 资料摘要 |
| `wiki/entities/` | 实体（人物/公司/工具/方法） |
| `wiki/concepts/` | 概念（框架/方法论/理论） |

## 触发条件

- `/ingest`：扫描 `raw/` 所有非 `09-archived/` 子目录
- `/ingest <path>`：仅处理指定文件
- 用户说“摄入/导入/收入这篇文章/论文”

---

## 工作流

### 步骤 0：路径解析

```bash
python ".agents/scripts/router.py" ingest
```

读取 JSON 获取 `workspace_root`、`wiki_dir`、`raw_dir`、`index_path`、`log_path`。

**短规则**：

> 若 `router.py` 返回 `missing_paths`，停止 ingest，先向用户报告缺失路径，不继续读源文件。

### 步骤 1：判定类型 + 读取

| 输入类型 | 模式 | 读取策略 | 失败处理 |
|---|---|---|---|
| `raw/02-papers/*.pdf` | 论文模式 | **先调用 `paper_deep_read.py` 生成证据层**；普通英文论文默认规则直出，中文论文或复杂候选默认走 agent 两阶段，再补摘要 / entity / concept / index / log | 深读脚本失败时保留 source 骨架并标注 `需要人工补读`，**不归档** |
| `raw/01-articles/*.md` | 通用模式 | 全文读取 | 正常继续 |
| 其他可读文本资料 | 通用模式 | 全文读取 | 正常继续 |

#### 论文模式默认子流程（强制）

当输入是 `raw/02-papers/*.pdf` 时，`ingest` 不再自己从零做图示/公式工作，而是把这部分交给 `paper-deep-reading` 的本地执行器。

默认分流规则：

- **规则直出模式**：英文论文、caption 规整、候选价值判断明显时，直接运行：

```bash
python ".agents/scripts/paper_deep_read.py" "<pdf路径>" \
  --progress \
  --preview-timeout 10
```

- **agent 两阶段模式**：当满足以下任一条件时，`ingest` 应默认切到两阶段，而不是继续单阶段直出：
  - 论文正文主要是中文，或 caption 高频出现 `图1/图 1/表1/表 1`
  - 候选虽然召回到了，但你判断“规则排序无法稳定代表论文价值”
  - 版面复杂（双栏密集、图表靠得很近、同页多张子图/多张表）
  - 后续明确要做 `/query-with-code`，且图表选择质量会直接影响代码对照

第一阶段先运行：

```bash
python ".agents/scripts/paper_deep_read.py" "<pdf路径>" \
  --selection-mode agent \
  --progress \
  --preview-timeout 10
```

性能保护规则：候选池阶段必须带 `--progress`，避免长时间无输出；默认带 `--preview-timeout 10`，避免单个候选预览长时间占满单核 CPU。只有在用户明确要求“先快看 / 粗筛 / 机器卡顿”时，才追加 `--max-candidates N`；默认不要加候选上限，以免漏掉后文关键实验表。

读取其输出中的：

- `candidate_pool`
- `recommended_slots`
- `selection_deficit`
- `skipped_candidates`

然后由 agent 选择最终要保留的 slot，再运行第二阶段：

```bash
python ".agents/scripts/paper_deep_read.py" "<pdf路径>" --selection-mode agent \
  --progress \
  --preview-timeout 10 \
  --selected-slot figure-01 \
  --selected-slot table-01
```

`ingest` 在论文模式下的职责是：

1. 调用 `paper_deep_read.py` 生成证据层（`assets/papers/{slug}/`、`source` 骨架、文本缓存）；若走 agent 两阶段，则先拿候选池再回填 `selected-slot`
2. 在已有骨架上补：核心摘要、实体、概念、知识链接
3. 更新 `wiki/index.md`、`wiki/log.md`
4. 确认成功后再归档到 `raw/09-archived/`

也就是说：

- `ingest` = 总流程 / 编排层
- `paper-deep-reading` = 论文证据层 / 子流程
- 若切到 agent 两阶段，`ingest` 负责在第一阶段读取候选池、做 slot 决策，再调用第二阶段落盘

### 步骤 2：提炼核心

从源文件提取并翻译为中文：

- **通用**：核心动机、创新点、实体名词、概念名词
- **论文模式追加**：
  - **先复用 `paper_deep_read.py` 已生成的 source 骨架，不重复从零搭结构**
  - 研究问题
  - 核心方法
  - 证据与评估（数据集、指标、2-3 条关键结果）
  - 局限与适用边界
  - 可复现线索（代码/数据/权重链接）
  - Metadata：作者、年份、期刊/会议、DOI / arXiv
  - 关键图示（如模型结构图、流程图、关键结果表）
  - 关键公式（优先 loss、异常分数、核心模块公式，转写为 LaTeX）→ 详见下方 **公式转写** 子节
  - 代码对照线索（公式/图示最可能映射到代码仓的哪些模块）

#### Metadata 固定规则

- 能确认 → 写具体值
- 不能确认 → 写 `未在正文中找到`
- 不允许：
  - 估计年份
  - 猜会议名 / 期刊名
  - 用文件名硬推导正式发表 venue

#### 抗幻觉证据链规则

`ingest` 的输出必须把模型判断降级为可回查的知识编译结果。写入前先按断言强度分级：

| 断言类型 | 示例 | 写入要求 |
|---|---|---|
| 事实型断言 | 作者、年份、venue、数据集、指标、结果数值、公式名称、方法组件 | 必须能在原文或 `paper_deep_read.py` 证据层中定位；找不到就写 `未在正文中找到` 或不写 |
| 关键解释型断言 | 方法解决的问题、核心机制、实验结论、局限 | 必须附原文页码、图表 caption、段落线索或 source 骨架中的证据线索 |
| 推断型断言 | 可能对应哪个代码模块、可归入哪个概念网络 | 必须使用 `可能` / `待核验` 表述，并说明依据；禁止写成确定事实 |

短规则：没有证据锚点的高价值断言不要写成确定语气。宁可保留 `待核验`，不要补一个看似完整但无法回查的结论。

证据锚点推荐格式：

```markdown
- **关键结论**: 本文使用双向记忆自编码器建模视频片段差异。
  - 证据：第 3 页 Fig. 1 caption；第 4 页方法段落。
```

对论文 source 页，至少这些内容必须带证据锚点或明确写 `未在正文中找到`：

- Metadata 中的作者、年份、期刊/会议、DOI / arXiv
- 数据集、指标、关键结果数值
- 关键图示 / 关键公式的作用说明
- 代码对照线索中的 `loss`、`score`、`module` 映射判断

#### 公式转写（论文模式默认执行）

`paper_deep_read.py` 生成的 source 骨架里，公式区域是占位符（`% 在这里补充...`），附带了原文定位线索（页码 + Fig/Table 引用）。ingest 阶段必须把这个占位符**升级为真实 LaTeX**。

**工作流：**

1. 读取 `paper_deep_read.py` 已生成的文本缓存：`.cache/agents/papers/{slug}/source_text.txt`
2. 对每个公式槽位，根据其 `原文定位` 线索（如"第 4 页 3.1 节公式 (1)~(4)"）在缓存文本中定位公式附近的自然语言描述
3. 从自然语言描述转写为 LaTeX：
   - 损失函数 / 目标函数 → `\mathcal{L}`、`\mathbb{E}`、`\|\cdot\|^2`
   - 异常分数 → `S(I_t)`、`\text{PSNR}`、归一化公式
   - 注意力模块 / 约束项 → `\text{softmax}`、`\otimes`、矩阵运算
4. 补全 `原文描述` 行（摘一句原文中紧邻公式的自然语言，方便回查）
5. 补全 `解释` 行（一句话说明该公式的语义作用）
6. 转写完成后，`原文定位` / `原文描述` / `解释` / `证据` 四行保留，作为抗幻觉锚点

**转写质量规则：**

| 情况 | 动作 |
|---|---|
| 文本缓存中能找到明确的公式描述 | 转写为 LaTeX，附页码锚点 |
| 文本缓存中描述模糊或截断（pdftotext 的 artifacts） | 保留占位符 `%`，但在 `原文描述` 中注明"缓存文本截断，需对照原文 PDF 补写" |
| 缓存中完全找不到对应公式 | 保留占位符，注明"未在文本缓存中找到，需人工回查 PDF" |
| 公式涉及复杂多行对齐（如消融表的约束项） | 优先保留核心项，多行对齐标注 `待补完整形式` |

**禁止：**
- 禁止从 PDF metadata 或文件名推测公式
- 禁止将无原文依据的推断公式写成确定事实
- 禁止删除 `paper_deep_read.py` 生成的 `原文定位` / `原文描述` 行（即使公式已补全）

### 步骤 3：创建 source 页

#### 通用模板（`wiki/sources/摘要-{slug}.md`）

```markdown
---
title: "摘要-{slug}"
type: source
tags: [来源]
sources: ["raw/09-archived/{文件名}"]
last_updated: YYYY-MM-DD
---

## 核心摘要
[3-5 句：问题→方法→证据→局限；关键事实需能回查原文]

## 关联连接
- [[EntityName]] — 关联实体
- [[ConceptName]] — 关联概念
```

#### 论文专属追加块

```markdown
## Metadata
- **作者**: 作者1, 作者2, ...
- **年份**: YYYY / 未在正文中找到
- **期刊/会议**: 期刊或会议名 / 未在正文中找到
- **DOI / arXiv**: 有则写，无则写"未在正文中找到"
```

如论文包含对后续 `/query-with-code` 有高价值的图或公式，优先再追加：

```markdown
## 关键图示
- ![[papers/{slug}/figure-01.png]]
- 图 1：一句话说明图中模块与数据流。

## 关键公式
### 公式 1：总训练目标
- 原文定位：优先回到对应页码附近的 `loss / objective / equation` 段落。
- 原文描述：摘一条原文里紧邻该公式的自然语言描述，方便读者反查。
$$
...
$$
- 解释：该式负责什么，最可能对应哪个代码层模块。
- 证据：第 N 页公式附近段落 / Fig. X caption。

## 代码对照线索
- `loss`：可能对照训练脚本中的总损失聚合处。状态：待核验；依据：第 N 页训练目标公式。
- `score`：可能对照推理阶段的异常分数函数。状态：待核验；依据：第 N 页异常分数描述。

## 表格速览
### Table N — 表格标题（第 N 页）     ← 必须包含 Table 编号、英文原标题、页码

| 列1 | 列2 | ... |          ← 标准 Markdown 表格，从 pdf 原文手动转录
|-----|-----|-----|
| 行1 | ... | ... |
| 行2 | ... | ... |
| **本文方法** | **最优值** | ... |   ← 加粗突出本文方法所在行和最优值

> 表格注释 / 脚注说明。                   ← 引用块解释表格中的特殊标注

- 关键发现：从表格中提炼 1-2 条核心结论。   ← 必填
- **来源**: 第 N 页 Table N。                 ← 必填，证据锚点
```

**表格速览格式规则：**

| 规则 | 要求 |
|---|---|
| 标题行 | `### Table N — 英文标题（第N页）`，N 为论文中的实际表格编号 |
| 表格体 | 从 PDF 原文手动转录为 Markdown 表格（`| col | col |`），列名使用英文原词，数据行中的本文方法用 `**粗体**` 标注 |
| 引用块 | 用 `>` 标注表格脚注、特殊符号说明（如 `a 表示含姿态数据`）、数据来源限定 |
| 关键发现 | 用 `-` 列表提炼 1-2 条从该表得出的核心结论，避免翻译表格内容本身，而是解释"这个表说明了什么" |
| 来源 | `- **来源**: 第N页 Table N`，末尾必须有页码锚点 |
| 数量 | 每篇论文 1-2 张最重要的表（对比表优先、消融表次之），不要机械全量列出 |
| 转录失败 | snippet 截断严重无法还原表格结构时，用 `> [!warning] pdftotext 未能拆分为列，保留原文块待人工整理。` 回退 |

**禁止：**
- 禁止将表格截图嵌入（`![[...]]`）放在 `## 表格速览` 区块
- 禁止猜测数值 — 表格中的数字必须来自 PDF 原文
- 禁止用中文重命名列名（保留原文的 Method、AUC、FPS 等）
- 禁止空表格或只写"待补"（至少转录一条 snippet 中的关键行）

短规则：如果 `paper_deep_read.py` 已经生成 `## 关键图示 / 关键公式 / 代码对照线索`，`ingest` 只补充和修正，不重排、不覆盖用户已填写公式；补公式时保留“原文定位 / 原文描述”两行，方便读者定位原文公式。

#### source 强制规则

- `sources` 必为数组
- 归档后路径必须指向 `raw/09-archived/`
- frontmatter 保持极简（仅 5 字段）
- metadata 只放正文 `## Metadata`，不放 frontmatter

### 步骤 4：知识网络化（entity / concept）

#### Concept 复用优先原则

`ingest` 的目标不是为每篇资料制造新概念页，而是把新资料编译进已有知识网络。创建新 `concept` 是最后手段。

在新建任何 `concept` 前，必须先执行以下检查：

1. 先检索 `wiki/concepts/`、`wiki/index.md` 完整注册表，以及当前 source 可能关联的已有页面。
2. 优先寻找语义等价、上下位关系或可合并的既有 `concept`：
   - 同义词 / 翻译不同：复用已有 `concept`，并在页面中补充别名。
   - 新资料只是已有概念的一个案例：不要新建 `concept`，增量写入已有 `concept`。
   - 新资料是已有概念的子机制：优先写入已有 `concept` 的“子机制 / 相关方法”段落；只有该子机制会被多篇资料复用时才新建独立 `concept`。
3. 只有同时满足以下条件，才允许新建 `concept`：
   - 现有 `concept` 无法准确容纳该概念；
   - 该概念具有跨资料复用价值；
   - 它不是单篇 source 的一次性术语；
   - 已在 `## 关联连接` 中连接至少一个已有 `concept` 或 `entity`，避免孤岛页面。
4. 如果不确定是否该新建，默认不要新建；先把内容合并进最接近的已有 `concept`，并用一句话标注来源限定。

| 条件 | 动作 |
|---|---|
| 提取到明确命名的方法 / 系统 | 建 `entity` |
| 论文是 survey / tutorial | 通常不建 `entity` |
| 已有 `concept` 可容纳新知识 | 优先增量合并，不新建 |
| 只是已有 `concept` 的案例 / 变体 / 子机制 | 合并进已有 `concept` |
| 概念可跨多篇资料复用，且现有 `concept` 无法容纳 | 才新建 `concept` |
| 只是一次性短语 | 不建 `concept` |
| 页面不存在 | 先确认无法复用后再创建 |
| 页面已存在 | 增量合并 |
| 发现知识冲突 | 立即暂停并报告 |

#### 页面模板

```markdown
---
title: "页面名称"
type: entity | concept
tags: [标签]
sources: ["raw/09-archived/{文件名}"]
last_updated: YYYY-MM-DD
---

## 定义
[核心定义；若来自单篇 source，保留证据或来源限定]

## 关键信息
[提取的详细信息；事实型断言需能回查 source]

## 关联连接
- [[摘要-{slug}]] — 来源
- [[RelatedName]] — 相关实体/概念
```

#### 网络化规则

- `entity -> wiki/entities/`
- `concept -> wiki/concepts/`
- source 至少链接 `entity + concept`
- entity / concept 必须回链 source
- 如果 source 中加入关键图示或公式，entity / concept 只同步保留**高复用**部分，不要机械复制全部细节

### 论文深读联动（论文模式下默认执行）

当输入是论文 PDF 时，默认先跑 `paper_deep_read.py`。以下情况属于**必须**走该子流程，而不是“可选增强”：

- 存在关键结构图，后续需要在 Obsidian 中反复引用
- 存在明确训练目标 / 异常分数 / 检索公式，后续需要与代码对照
- 用户明确说“后面还要和代码仓做对照分析”

对于普通论文，即使没有明显图/公式需求，也建议先复用该子流程，因为它会统一生成：

- `assets/papers/{slug}/`
- `wiki/sources/摘要-{slug}.md` 骨架
- `## 关键图示`
- `## 关键公式`
- `## 代码对照线索`

#### 何时必须升级为 agent 两阶段 deep read

命中以下任一条件时，`ingest` 不应停留在规则直出模式，而应自动升级：

- 中文论文或中英混排论文，且关键 caption 以 `图/表` 为主
- `paper_deep_read.py --selection-mode agent` 返回的 `candidate_pool` 明显比规则模式更丰富
- `selection_deficit` 显示规则模式在高价值表格上存在明显缺额，而该论文又依赖表格证据支撑结论
- `skipped_candidates` 显示大量候选在某些 query 变体上失败，需要 agent 根据上下文做更稳的保留决策

短规则：agent 两阶段 deep read 默认使用 `--progress --preview-timeout 10`；仅在粗筛或机器负载敏感时加 `--max-candidates N`。

升级后的收口规则：

1. 先拿 `candidate_pool`
2. 基于 `recommended_slots` 做初判，但不要盲从
3. 如需保守，优先保留“方法总览图 + 关键结果表 + 一张补充图”
4. 第二阶段回填 `--selected-slot ...` 后，再继续 ingest 的摘要 / entity / concept / index / log / 归档流程

此时补充要求：

- 图片写入 `assets/papers/{slug}/`
- wiki 页面中用 `![[papers/{slug}/figure-01.png]]` 引用
- 公式优先保存为 LaTeX，而不是只保留截图

#### ingest 与 paper-deep-reading 的边界

- `paper-deep-reading` 负责：PDF 文本抽取、锚点检索、图示裁图、source 骨架与公式空位
- `ingest` 负责：知识提炼、entity/concept 建立、索引更新、日志更新、归档，以及在需要时 orchestrate agent 两阶段 slot 选择
- 禁止两边都重复生成同一批图示或重复初始化同一个 source 页结构

### 步骤 5：更新索引与日志

1. **完整注册表（必须）**：统一通过 `write_index.py` 更新 `wiki/index.md` 的 `## 完整注册表`
2. **导航层（按需）**：只补入口价值高的页面；拿不准只更注册表。需要补入口时也通过 `write_index.py --nav-section ...` 完成
3. **日志**：必须通过统一脚本 append-only 写入 `wiki/log.md`

完整注册表示例：

```bash
python ".agents/scripts/write_index.py" \
  --index-path "<index_path>" \
  --section "Sources" \
  --page "摘要-foo" \
  --description "该资料的核心主旨摘要。"
```

导航层示例（仅对高入口价值页面使用）：

```bash
python ".agents/scripts/write_index.py" \
  --index-path "<index_path>" \
  --section "Concepts" \
  --page "ConceptName" \
  --description "该概念的核心定义。" \
  --nav-section "快速入口"
```

```bash
python ".agents/scripts/write_log.py" \
  --log-path "<log_path>" \
  --action ingest \
  --summary "<操作简述>" \
  --detail "变更=新增 [[PageName]]；更新 [[index.md]]" \
  --detail "冲突=无"
```

写入效果示例：

```markdown
## [YYYY-MM-DD] ingest | 操作简述
- **变更**: 新增 [[PageName]]；更新 [[index.md]]
- **冲突**: 无 (或: 冲突 [[Page]]，已暂停)
```

### 步骤 6：归档 + 路径一致性

确认 `source / entity / concept / index / log` 全部就绪后，移动源文件到 `raw/09-archived/`。

#### 归档规则

- 禁止修改源文件正文
- PDF 提取失败 → 不归档
- 归档后 `wiki/` 中不得再出现 `raw/02-papers/` 的 `sources:` 引用

---

## 冲突处理

发现新旧知识冲突时：

1. 暂停
2. 报告冲突内容
3. 让用户选择：
   - 保留两者并标注
   - 新覆盖旧
   - 放弃本次
4. 再继续

---

## 强制约束

- 禁止读取 `raw/09-archived/` 下任何文件
- 禁止归档 PDF 提取失败的源文件
- 禁止修改源文件内部文字
- 禁止将论文 metadata 塞入 frontmatter
- 禁止把无证据的模型推断写成确定事实
- 事实型断言找不到证据时必须写 `未在正文中找到`、`待核验`，或不写
- 所有 wiki 页面必有 `## 关联连接`
- 简体中文输出，entity 用 TitleCase，source/concept/synthesis 用 kebab-case

---

## 快速自检

- [ ] source 页符合模板（frontmatter + 二级标题）
- [ ] entity/concept 有 `定义 / 关键信息 / 关联连接`
- [ ] 高价值事实型断言均有证据锚点，或已标注 `未在正文中找到` / `待核验`
- [ ] 推断型内容没有写成确定事实，且说明了依据
- [ ] `index.md` 完整注册表已登记，导航层已判断是否补录
- [ ] `log.md` 已 append
- [ ] `wiki/` 中无 `raw/02-papers/` 的 `sources:` 引用
- [ ] 公式占位符已根据文本缓存转写为 LaTeX，无法转写的已标注原因
- [ ] PDF 提取失败已标注且未归档
