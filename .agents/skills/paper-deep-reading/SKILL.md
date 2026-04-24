---
name: paper-deep-reading
description: 深读 `raw/02-papers/` 中的论文 PDF，抽取关键图片到 `assets/`，把关键公式转成 LaTeX 写入 `wiki/sources/` 或相关实体/概念页，并为后续 `/query-with-code` 预埋公式-代码对照线索。默认推荐 MinerU，必要时回退 Marker。
user-invocable: true
---

# paper-deep-reading 技能

## 目标

- 深读论文 PDF，而不是只做 3-5 句摘要。
- 把**关键图片**沉淀到 `assets/`，便于 Obsidian 直接嵌入。
- 把**关键公式**转成 LaTeX，便于后续 `/query-with-code` 对照 loss、模块和推理公式。
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
- `python ".agents/scripts/pdf_tool.py" find <pdf> "Figure 1"` — 找锚点页码与矩形
- `python ".agents/scripts/pdf_tool.py" render-page <pdf> --page 3 --output /tmp/page-3.png` — 渲染整页
- `python ".agents/scripts/pdf_tool.py" snapshot-query <pdf> "Figure 1" --output "assets/papers/{slug}/figure-01.png" --preset figure` — 按 query 裁图
- `python ".agents/scripts/pdf_tool.py" snapshot-rect <pdf> --page 3 --rect x0,y0,x1,y1 --output "assets/papers/{slug}/figure-01.png"` — 按矩形裁图
- `python ".agents/scripts/paper_deep_read.py" <pdf>` — 生成 `wiki/sources/` 草稿页、文本缓存和 `assets/papers/{slug}/` 图示骨架

### 步骤 1：确认输入与边界

- 输入优先级：
  1. `raw/02-papers/*.pdf`
  2. 用户明确给出的本地 PDF 绝对路径
  3. 已归档论文对应的 `wiki/sources/` 页面（只做补全，不回读 `raw/09-archive/`）
- `raw/` 视为事实层：**禁止修改 PDF 正文**。
- 图片产物写入 `assets/`；知识产物写入 `wiki/`。

### 步骤 2：论文解析后端选择

默认推荐：

1. **MinerU**：优先用于论文 Markdown、公式 LaTeX、图片块抽取。
2. **Marker**：当更看重 Python 可编程性、chunk/JSON 检索结构时作为回退。
3. 外部仓库 `paper-deep-reading-skill` 的 `pdf_tool.py`：适合作为锚点搜索、页面截图、局部重裁的补刀工具，不作为主导出格式。

选择规则：

- 需要**公式 + 图 + Markdown**一起稳定产出 → 优先 MinerU。
- 需要**chunk / JSON tree / 检索友好结构** → 优先 Marker。
- 只需补抓某张图、某个定理框、某个表格 → 可直接借用 `pdf_tool.py` 一类截图工作流。

### 步骤 3：抽取产物

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
$$
...
$$
- 解释：该式对应训练阶段的总目标。

## 代码对照线索
- `loss`：优先对照训练脚本中的总损失聚合处。
- `memory score`：优先对照推理阶段的异常分数计算函数。
```

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
  - `## 代码对照线索`

简化理解：

- 单独调用 `paper-deep-reading` = 先做证据层
- 调用 `ingest` 处理论文 = `ingest -> paper-deep-reading -> ingest 收口`

### 步骤 6：更新索引与日志

如果新增或明显增强了 wiki 页面，必须同步：

1. `wiki/index.md` 完整注册表
2. `wiki/log.md` append-only 记录

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
