---
name: ingest
description: 将 raw/ 目录原始资料编译到 wiki/（sources/entities/concepts），完成后归档到 raw/09-archive/。支持 `/ingest`（扫描所有未归档文件）或 `/ingest <path>`（处理指定文件）。触发词：摄取/导入/收入资料、把论文 PDF 放入 raw/02-papers/ 生成 Obsidian 知识网络。禁止读取 raw/09-archive/。
user-invocable: true
---

# ingest 技能

## 目录约定

`raw/` 是收件箱，`wiki/` 是编译输出层。

| 目录 | 用途 |
|---|---|
| `raw/01-articles/` | 网页剪藏 Markdown |
| `raw/02-papers/` | 论文 PDF |
| `raw/09-archive/` | 已处理归档（**禁止读取**） |
| `wiki/sources/` | 资料摘要 |
| `wiki/entities/` | 实体（人物/公司/工具/方法） |
| `wiki/concepts/` | 概念（框架/方法论/理论） |

## 触发条件

- `/ingest`：扫描 `raw/` 所有非 `09-archive/` 子目录
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
| `raw/02-papers/*.pdf` | 论文模式 | **先调用 `paper_deep_read.py` 生成证据层**，再补摘要 / entity / concept / index / log | 深读脚本失败时保留 source 骨架并标注 `需要人工补读`，**不归档** |
| `raw/01-articles/*.md` | 通用模式 | 全文读取 | 正常继续 |
| 其他可读文本资料 | 通用模式 | 全文读取 | 正常继续 |

#### 论文模式默认子流程（强制）

当输入是 `raw/02-papers/*.pdf` 时，`ingest` 不再自己从零做图示/公式工作，而是把这部分交给 `paper-deep-reading` 的本地执行器：

```bash
python ".agents/scripts/paper_deep_read.py" "<pdf路径>"
```

`ingest` 在论文模式下的职责是：

1. 调用 `paper_deep_read.py` 生成证据层（`assets/papers/{slug}/`、`source` 骨架、文本缓存）
2. 在已有骨架上补：核心摘要、实体、概念、知识链接
3. 更新 `wiki/index.md`、`wiki/log.md`
4. 确认成功后再归档到 `raw/09-archive/`

也就是说：

- `ingest` = 总流程 / 编排层
- `paper-deep-reading` = 论文证据层 / 子流程

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
  - 关键公式（优先 loss、异常分数、核心模块公式，转写为 LaTeX）
  - 代码对照线索（公式/图示最可能映射到代码仓的哪些模块）

#### Metadata 固定规则

- 能确认 → 写具体值
- 不能确认 → 写 `未在正文中找到`
- 不允许：
  - 估计年份
  - 猜会议名 / 期刊名
  - 用文件名硬推导正式发表 venue

### 步骤 3：创建 source 页

#### 通用模板（`wiki/sources/摘要-{slug}.md`）

```markdown
---
title: "摘要-{slug}"
type: source
tags: [来源]
sources: ["raw/09-archive/{文件名}"]
last_updated: YYYY-MM-DD
---

## 核心摘要
[3-5 句：问题→方法→证据→局限]

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
$$
...
$$
- 解释：该式负责什么，最可能对应哪个代码层模块。

## 代码对照线索
- `loss`：对照训练脚本中的总损失聚合处。
- `score`：对照推理阶段的异常分数函数。
```

短规则：如果 `paper_deep_read.py` 已经生成 `## 关键图示 / 关键公式 / 代码对照线索`，`ingest` 只补充和修正，不重排、不覆盖用户已填写公式。

#### source 强制规则

- `sources` 必为数组
- 归档后路径必须指向 `raw/09-archive/`
- frontmatter 保持极简（仅 5 字段）
- metadata 只放正文 `## Metadata`，不放 frontmatter

### 步骤 4：知识网络化（entity / concept）

| 条件 | 动作 |
|---|---|
| 提取到明确命名的方法 / 系统 | 建 `entity` |
| 论文是 survey / tutorial | 通常不建 `entity` |
| 概念可跨论文复用 | 建 `concept` |
| 只是一次性短语 | 不建 `concept` |
| 页面不存在 | 创建 |
| 页面已存在 | 增量合并 |
| 发现知识冲突 | 立即暂停并报告 |

#### 页面模板

```markdown
---
title: "页面名称"
type: entity | concept
tags: [标签]
sources: ["raw/09-archive/{文件名}"]
last_updated: YYYY-MM-DD
---

## 定义
[核心定义]

## 关键信息
[提取的详细信息]

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

此时补充要求：

- 图片写入 `assets/papers/{slug}/`
- wiki 页面中用 `![[papers/{slug}/figure-01.png]]` 引用
- 公式优先保存为 LaTeX，而不是只保留截图

#### ingest 与 paper-deep-reading 的边界

- `paper-deep-reading` 负责：PDF 文本抽取、锚点检索、图示裁图、source 骨架与公式空位
- `ingest` 负责：知识提炼、entity/concept 建立、索引更新、日志更新、归档
- 禁止两边都重复生成同一批图示或重复初始化同一个 source 页结构

### 步骤 5：更新索引与日志

1. **完整注册表（必须）**：`wiki/index.md` 的 `## 完整注册表`
2. **导航层（按需）**：只补入口价值高的页面；拿不准只更注册表
3. **日志**：`wiki/log.md` append-only

```markdown
## [YYYY-MM-DD] ingest | 操作简述
- **变更**: 新增 [[PageName]]; 更新 [[index.md]]
- **冲突**: 无 (或: 冲突 [[Page]], 已暂停)
```

### 步骤 6：归档 + 路径一致性

确认 `source / entity / concept / index / log` 全部就绪后，移动源文件到 `raw/09-archive/`。

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

- 禁止读取 `raw/09-archive/` 下任何文件
- 禁止归档 PDF 提取失败的源文件
- 禁止修改源文件内部文字
- 禁止将论文 metadata 塞入 frontmatter
- 所有 wiki 页面必有 `## 关联连接`
- 简体中文输出，entity 用 TitleCase，source/concept/synthesis 用 kebab-case

---

## 快速自检

- [ ] source 页符合模板（frontmatter + 二级标题）
- [ ] entity/concept 有 `定义 / 关键信息 / 关联连接`
- [ ] `index.md` 完整注册表已登记，导航层已判断是否补录
- [ ] `log.md` 已 append
- [ ] `wiki/` 中无 `raw/02-papers/` 的 `sources:` 引用
- [ ] PDF 提取失败已标注且未归档
