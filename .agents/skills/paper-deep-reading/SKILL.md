---
name: paper-deep-reading
description: 深读 `raw/02-papers/` 中的论文 PDF，抽取关键图片到 `assets/`，在 `wiki/` 中沉淀关键公式空位 / LaTeX 草稿与代码对照线索，并为后续 `/query-with-code` 预埋结构化论文证据。当前默认执行器是本地 `pdf_tool.py + paper_deep_read.py`；需要更强公式/版面抽取时可升级到 MinerU 或 Marker。
user-invocable: true
---

# paper-deep-reading 技能

## 目标

- 深读论文 PDF，而不是只做 3-5 句摘要。
- 把**关键图片**沉淀到 `assets/`，便于 Obsidian 直接嵌入。
- 把**关键公式**优先沉淀为 LaTeX；若当前无法稳定自动识别，至少要在 `wiki/` 中预留公式空位、局部截图或公式草稿，并写出公式参数（如有）、描述及其在对应原文的页码，便于后续 `/query-with-code` 对照 loss、模块和推理公式。
- 给 `wiki/sources/`、`wiki/entities/`、`wiki/concepts/` 提供可检索的结构化论文证据。

---

## 何时触发

- `/paper-deep-reading <pdf路径>`
- 用户要求“深读论文”“把论文图和公式抽出来”“把论文转成便于后续对代码的资料”
- 用户希望为 `/query-with-code` 提前准备论文结构化证据

如果用户只是要普通 ingest，不必单独显式调用本技能；因为在当前仓库里，**论文模式的 `ingest` 已把本技能视为默认子流程**。当用户显式调用本技能时，表示希望先做“论文证据层”，稍后再由 `ingest` 或人工补全知识提炼。

---

## 工作流

### 步骤 0：路径引导

```bash
python ".agents/scripts/router.py" paper-deep-reading "<pdf路径或论文标识>"
```

读取 JSON，获取 `workspace_root`、`wiki_dir`、`raw_dir`、`index_path`、`log_path`。

### 可直接复用的本地脚本

- `python ".agents/scripts/pdf_tool.py" extract-text <pdf>` — 抽全文文本
- `python ".agents/scripts/pdf_tool.py" find <pdf> "Figure 1" --mode auto` — 找锚点页码与矩形（先 PDF 文本，失败再 OCR）
- `python ".agents/scripts/pdf_tool.py" snapshot-query-preview <pdf> "Table II" --preset table --mode auto` — 只返回候选元数据，不落 PNG，适合先看正文候选
- `python ".agents/scripts/pdf_tool.py" render-page <pdf> --page 3 --output /tmp/page-3.png` — 渲染整页
- `python ".agents/scripts/pdf_tool.py" snapshot-query <pdf> "Figure 1" --output "assets/papers/{slug}/figure-01.png" --preset figure --mode auto` — 按 query 裁图
- `python ".agents/scripts/pdf_tool.py" snapshot-rect <pdf> --page 3 --rect x0,y0,x1,y1 --output "assets/papers/{slug}/figure-01.png"` — 按矩形裁图
- `python ".agents/scripts/paper_deep_read.py" <pdf>` — 规则直出模式：生成 `wiki/sources/` 草稿页、文本缓存和 `assets/papers/{slug}/` 图示骨架，并负责正文候选召回、论文价值排序与软配额选择
- `python ".agents/scripts/paper_deep_read.py" <pdf> --selection-mode agent` — 两阶段模式：先输出双语候选池与推荐 slot，不立即落盘图示
- `python ".agents/scripts/paper_deep_read.py" <pdf> --selection-mode agent --selected-slot figure-01 --selected-slot table-01` — agent 选定 slot 后，第二次调用才真正落盘

### 默认自动选择口径

- `pdf_tool.py` 负责找锚点、预览候选、裁图和截图质量评分，`score` 只表示定位/截图质量，不表示论文内容价值。
- `paper_deep_read.py` 负责正文候选召回后的价值判断，会生成独立的 `value_bucket`、`value_score`、`selection_reason`，再决定最终落盘顺序。
- 默认候选范围只看主论文正文，不纳入 `References`、`Appendix`、`Appendices`、`Supplementary`、`Supplemental` 之后的图表。
- 正文 caption 召回支持 `Figure`、`Fig.`、`Table`、`Tab.`、`图`、`表`，同时支持阿拉伯数字和罗马数字。
- 默认排序采用保守版策略，先保留解释方法的图表，再保留证明效果、效率或权衡关系的图表。
- 目标配额是 `2 图 + 1 表`，但这是软配额。缺少高价值表格时允许返回 2 图或更少，并通过 `selection_deficit` 报告缺额，不用低价值表格补 filler。

### 两阶段筛选模式（推荐用于中文文献或复杂版面）

当论文是中文文献、caption 中含 `图1/表1`，或你怀疑规则排序无法稳定反映论文价值时，优先走 agent 两阶段模式：

1. 先运行：

```bash
python ".agents/scripts/paper_deep_read.py" "<pdf>" --selection-mode agent
```

它会返回：

- `candidate_pool`：双语召回后的候选池
- `recommended_slots`：规则系统默认推荐的 slot
- `selection_deficit`：若高价值表格不足，会显式报告缺额

2. 再由 agent 依据 `candidate_pool` 选择真正保留的 slot，然后运行：

```bash
python ".agents/scripts/paper_deep_read.py" "<pdf>" --selection-mode agent \
  --selected-slot figure-01 \
  --selected-slot figure-03 \
  --selected-slot table-02
```

此时脚本才会真正落盘图片、更新 source/index/log。

### Snapshot Playbook（截图策略）

#### Section-2：理论 / 方法核心截图

优先按以下顺序搜索 formal-result anchors：

- `Theorem`
- `Lemma`
- `Proposition`
- `Corollary`
- `Assumption`
- `Property`
- `Remark`

当锚点是正式命题块开头时，优先用：

```bash
python ".agents/scripts/pdf_tool.py" snapshot-query <pdf> "Theorem 1" --output /tmp/theorem-1.png --preset theorem --mode auto
```

目标是：**截 theorem/lemma/assumption/property/remark 主体，不带后续 `Proof`**。

如果论文没有显式 theorem-style 结构，再按以下 technical-core anchors 搜索：

- `Algorithm`
- `Objective`
- `Problem`
- `System Model`
- `Architecture`
- `Framework`
- `Loss`
- `Optimization`

这类块优先用 `generic`；若裁图接近但仍混入太多无关文本，再切到：

```bash
python ".agents/scripts/pdf_tool.py" snapshot-rect <pdf> --page N --rect x0,y0,x1,y1 --output /tmp/core.png --preset exact
```

#### Section-3：图 / 表 / 对比证据截图

优先搜索：

- `Fig.`
- `Figure`
- `Table`
- `Tab.`

推荐至少保留一个小证据集，而不是只抓一张：

- 一个主结果图 / 性能图
- 一个对比 / 消融 / 鲁棒性 / 通信代价图
- 一个补充信息的总结表格

当走当前仓库默认自动流程时，要把上面的经验规则收束成以下约束：

- 先做正文候选召回，不再使用“固定抓 `Figure 1 / Table 1 / Figure 2`”的老口径。
- 候选先按论文价值排序，再按软配额决定是否真正落 PNG。
- 表格只有在属于高价值对比表或性能表等场景时才优先入选。若没有高价值表格，不强补 filler。

使用规则：

- `figure`：caption 在下方时的常规图示截图
- `figure-column`：双栏页面里常规 `figure` 把邻栏卷进来时使用
- `table`：标题在上方、主体在下方的表格
- `exact`：自动裁图接近但仍不干净时，人工精裁

例如：

```bash
python ".agents/scripts/pdf_tool.py" snapshot-query <pdf> "Figure 2" --output /tmp/figure-2.png --preset figure-column --mode auto
python ".agents/scripts/pdf_tool.py" snapshot-query <pdf> "Table II" --output /tmp/table-2.png --preset table --mode auto
```

#### Caption 消歧规则（避免截到正文交叉引用）

论文正文经常先在段落里写 `as shown in Fig. 4`，真正的 `Fig. 4.` caption 可能在后一页。`snapshot-query` 默认会按命中顺序选择候选，因此**不能把第一个命中直接视为真实图注**。

处理规则：

1. 对每个要保留的图，先用 `find` 查看全部命中：

```bash
python ".agents/scripts/pdf_tool.py" find <pdf> "Fig. 4" --mode auto
```

2. 区分两类命中：
   - 正文交叉引用：snippet 像 `shown in Fig. 4`、`as Fig. 5 shows`，通常在正文段落中，不是 caption
   - 真实 caption：snippet 以 `Fig. N.` / `Figure N.` 开头，位置通常紧贴图下方
3. 若同一图号有多个命中，必须优先选择真实 caption 所在页，并在裁图时显式加 `--page N`：

```bash
python ".agents/scripts/pdf_tool.py" snapshot-query <pdf> "Fig. 4" \
  --preset figure \
  --page 13 \
  --output /tmp/figure-4.png
```

4. 临时输出到 `/tmp/opencode/` 后先检查，再覆盖 `assets/` 正式图片。
5. source 页中的证据锚点必须写真实 caption 页码，而不是正文交叉引用页码。

短规则：出现“正文页先提到图号、后一页才出现图”的版面时，一律用 `find → 选 caption 页 → snapshot-query --page N → 验图 → 覆盖资产`，不要依赖默认首个命中。

#### 何时必须重裁（Recropping Rules）

出现以下任一情况，必须重裁：

- theorem / method block 被截掉首行或末行
- theorem 图混进了 `Proof` 或下一个 theorem-like block
- figure / table 混入太多邻近正文或相邻图表
- 图只截到部分子图，或坐标轴 / 图例 / 标题缺失
- 表格少了底线、最后几行、列标题或边界线
- 自动裁图过小，符号 / 轴标签不可读

自动 preset 不够时，优先：

1. `render-page` 渲染整页
2. 观察近似边界
3. 用 `snapshot-rect --preset exact` 精裁

#### 命名建议

- `figure-01.png`
- `table-01.png`
- `theorem-01.png`
- `lemma-01.png`
- `property-01.png`
- `technical-core-01.png`

命名按“角色 + 序号”，不要用时间戳。

### 步骤 1：确认输入与边界

- 输入优先级：
  1. `raw/02-papers/*.pdf`
  2. 用户明确给出的本地 PDF 绝对路径
  3. 已归档论文对应的 `wiki/sources/` 页面（只做补全，不回读 `raw/09-archived/`）
- `raw/` 视为事实层：**禁止修改 PDF 正文**。
- 图片产物写入 `assets/`；知识产物写入 `wiki/`。

### 步骤 2：论文解析后端选择

当前仓库默认执行路径：

1. **本地 `pdf_tool.py + paper_deep_read.py`**：默认主路径。负责抽全文、找锚点、截图、生成 `wiki/sources/` 草稿、缓存文本和代码对照线索。

选择规则：

- 只需截图、锚点搜索、source 草稿、代码对照线索 → 默认走本地 `pdf_tool.py + paper_deep_read.py`。
- 只需补抓某张图、某个定理框、某个表格 → 直接使用 `pdf_tool.py` 的 screenshot workflow。

### 步骤 3：抽取产物

在当前默认执行器里，这一步分成两层职责：

- `pdf_tool.py` 负责把指定 query 或 preview 渲染成稳定截图，保证定位与裁图质量。
- `paper_deep_read.py` 负责从正文候选里挑出“最值得看”的图表，优先方法解释图，再补效果/效率证据。
- 若启用 `--selection-mode agent`，则脚本负责候选召回与定位，agent 负责第二步筛选与优先级判断。

#### 3.1 图片

优先抽：

- 模型结构图
- 总体流程图
- 训练/推理流程图
- 关键实验表格
- 论文中用于解释核心机制的图示

写入路径：

```text
assets/papers/{paper-slug}/figure-01.png
assets/papers/{paper-slug}/figure-02.png
assets/papers/{paper-slug}/table-01.png
assets/papers/{paper-slug}/equation-region-01.png
```

命名规则：

- 用 `paper-slug` 作为一级目录。
- 文件名使用 `figure-01` / `table-01` / `equation-region-01` 这类稳定编号。
- 不要把空格、中文作者名、年份直接塞进图片文件名。

在 wiki 页面中一律使用 Obsidian embed：

```markdown
![[papers/{paper-slug}/figure-01.png]]
```

#### 3.2 公式

优先抽：

- 总体目标函数 / loss
- 关键模块的打分函数
- 训练目标与约束项
- 推理阶段异常分数 / 检索分数 / 融合公式

保存原则：

- 能转写为 LaTeX 时，优先写成 `$$ ... $$`。
- 当前默认执行器若无法稳定自动还原公式，也必须至少保留：
  - 公式空位（推荐）
  - 公式局部截图（可选）
  - 公式对应的原文定位（页码或相邻图示）
  - 公式对应的自然语言解释与代码对照线索
- 如果公式识别不稳定，可同时保留局部截图，供人工对照：

```markdown
$$
\mathcal{L}=\mathcal{L}_{rec}+\lambda\mathcal{L}_{mem}
$$

![[papers/{paper-slug}/equation-region-01.png]]
```

- 公式必须配自然语言解释，避免只堆符号。

#### 3.3 代码对照线索

每篇深读论文至少提炼：

- 哪个公式最可能对应 `loss` 实现
- 哪个图最可能对应 `model/backbone/head/memory module`
- 哪个异常分数公式最可能对应 `score` / `metric` / `inference`

这部分写成文本线索，供 `/query-with-code` 使用。

### 步骤 4：落盘到 wiki

#### 4.1 source 页追加块

在 `wiki/sources/摘要-{slug}.md` 中，除常规摘要外，优先补这些章节：

```markdown
## 关键图示
- ![[papers/{paper-slug}/figure-01.png]]
- 图 1：整体架构图，展示模块边界与数据流。

## 关键公式
### 公式 1：训练目标
- 原文定位：第 N 页附近的 `loss / objective / equation` 段落。
- 原文描述：摘录该公式在正文中的一句作用说明，帮助回查原文。
$$
...
$$
- 解释：该式对应训练阶段的总目标。

## 代码对照线索
- `loss`：优先对照训练脚本中的总损失聚合处。
- `memory score`：优先对照推理阶段的异常分数计算函数。
```

如果当前只拿到了“公式空位 / 局部截图 / 代码对照线索”，这是**可接受的第一阶段结果**；不要为了追求自动 LaTeX 而阻塞整篇论文的深读与入库。

#### 4.2 entity / concept 页追加块

当公式或图对某个方法实体 / 概念具有高复用价值时，在相关页追加：

```markdown
## 关键公式
$$
...
$$

## 关键图示
![[papers/{paper-slug}/figure-01.png]]
```

规则：

- 只写**高复用**公式，不要把论文里所有符号都搬进 entity/concept。
- entity/concept 中的公式必须回链 source 页。

### 步骤 5：与 ingest / query-with-code 联动

- 如果用户先执行 `/paper-deep-reading`，后续 `/ingest` 应复用其结构化结论，而不是重新从零读论文。
- 如果用户直接执行 `/ingest` 处理论文，默认先跑 `paper_deep_read.py`，再由 `ingest` 继续补摘要、entity、concept、index、log 和归档。
- `/query-with-code` 在分析论文时，应优先读取：
  - `## 关键公式`
  - `## 关键图示`

### 步骤 5.1：自动回归口径

至少覆盖以下 4 类自动化场景，避免文档和实现再次漂移：

1. **完整命中**：同一篇论文同时存在高价值方法图、补充图和高价值表格时，输出应稳定为 `2 图 + 1 表`。
2. **缺表**：没有高价值表格时，不生成低价值 `table-01.png`，而是通过 `selection_deficit.missing.table` 显式报告缺额。
3. **罗马数字 caption**：`Table II`、`Fig. IV` 这类正文编号要能被召回、排序并参与最终选择。
4. **中文 caption**：`图1/图 1/表1/表 1` 要能被召回，并生成中英 query 变体。
5. **确定性重跑**：同一 PDF 连跑两次，规则模式下入选 `query/page_number/kind/value_bucket/selection_rank` 必须一致。

简化理解：

- 单独调用 `paper-deep-reading` = 先做证据层
- 调用 `ingest` 处理论文 = `ingest -> paper-deep-reading -> ingest 收口`

### 步骤 6：更新索引与日志

如果新增或明显增强了 wiki 页面，必须同步：

1. 通过 `write_index.py` 更新 `wiki/index.md` 完整注册表
2. `wiki/log.md` append-only 记录

示例：

```bash
python ".agents/scripts/write_index.py" \
  --index-path "<index_path>" \
  --section "Sources" \
  --page "摘要-{slug}" \
  --description "论文的核心摘要一句话。"
```

日志示例：

```markdown
## [YYYY-MM-DD] ingest | 深读论文并补充关键图示与公式
- **变更**: 更新 [[摘要-{slug}]]、[[EntityName]]；新增 `assets/papers/{paper-slug}/...`
- **冲突**: 无
```

---

## 强制约束

- 禁止修改 `raw/` 中 PDF 正文。
- 禁止把图片写回 `raw/`；图片只能写 `assets/`。
- 禁止只保存截图而不保存可检索的公式文本。
- 禁止只保存公式而不解释其在训练/推理中的作用。
- 禁止在 `wiki/` 页面里使用普通相对路径图片链接；统一用 `![[...]]`。
- 禁止为低价值装饰图（如论文首页、作者头像）创建 assets 产物。

---

## 推荐输出结构

```markdown
## 核心摘要
- 问题 / 方法 / 结论

## 关键图示
- ![[papers/{paper-slug}/figure-01.png]]
- 图示含义

## 关键公式
$$
...
$$
- 变量解释
- 训练 / 推理作用

## 代码对照线索
- 公式 -> loss / score / module
- 图示 -> model / forward / data flow

## 关联连接
- [[EntityName]]
- [[ConceptName]]
```

---

## 关联连接

- [[摘要-*.md]] — 深读结果优先沉淀位置
- [[wiki/index.md]] — 注册表更新入口
- [[wiki/log.md]] — 变更日志
- [[AGENTS.md]] — raw/assets/wiki 权限约束
