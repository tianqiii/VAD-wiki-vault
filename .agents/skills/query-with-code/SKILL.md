---
name: query-with-code
description: 结合本地 Wiki 知识与论文代码仓库做论文-代码对照分析。默认走 JdocMunch-first：优先检索 `wiki/sources|entities|concepts|syntheses` 的相关 sections；仅在 JdocMunch 不可用、命中失真/为空、或用户在问索引结构时，才回退到 `search_index.py` 或局部读取 `wiki/index.md`。需要用户提供论文（标题/PDF/知识库条目）和代码地址（GitHub/本地路径）。
user-invocable: true
---

# query-with-code 技能

## 目标
- 做论文层 + 代码层 + 对照层分析
- 需要时补缝合建议与 MVP 方案
- 结论要推进到“能写代码”的颗粒度

## 触发
- `/query-with-code`
- 对照论文和代码解释实现
- 找模块位置、梳理模型/loss/训练/推理/dataset/eval
- 判断论文与代码差异
- 生成复现路径 / 重构建议 / 缝合建议

## 最少输入
- 必需：论文（标题 / PDF / 知识库条目）+ 代码（GitHub 链接 / 本地路径）
- 建议：重点层面（模型/loss/训练/推理）、关键文件、优化目标（精度/效率/泛化/轻量化）

### 缺输入追问

> 还缺论文（标题/PDF/知识库条目）和代码（GitHub/本地路径），补上后我会做对照分析。如果能再补一句侧重（模型/loss/训练/推理/缝合），结果会更聚焦。

---

## 执行顺序

### 0. 路径引导

```bash
python ".agents/scripts/router.py" query "<用户问题>"
```

读取 JSON：`wiki_dir / raw_dir / index_path / log_path`

### 1. 主路径：知识库检索 — JdocMunch-first

#### 检索语料

| 类别 | 目录 | 索引名 |
|---|---|---|
| 主检索语料 | `wiki/sources/` `wiki/entities/` `wiki/concepts/` `wiki/syntheses/` | `llm-wiki-sources` `llm-wiki-entities` `llm-wiki-concepts` `llm-wiki-syntheses` |
| 非主检索语料 | `wiki/index.md` `wiki/log.md` | — |


#### 推荐索引参数
- `incremental: true`
- `use_ai_summaries: false`
- `use_embeddings: auto`

#### JdocMunch 调用链
1. `search_sections`
2. `get_section`
3. 必要时 `get_section_context`

#### 问题类型 → 搜索顺序
| 问题类型 | 搜索顺序 |
|---|---|
| 论文理解 / 方法对照 | `sources -> entities -> concepts -> syntheses` |
| 方法比较 / 融合建议 | `syntheses -> entities -> concepts -> sources` |
| 论文细节 / 实验 / 数据集 | `sources -> entities -> syntheses` |
| 公式 / 模块 / loss / score 对照 | `sources -> entities -> concepts -> syntheses` |
| 知识库结构问题 | 不走 JdocMunch，直接 fallback |

#### 升降级规则
- 默认先综合命中的 sections
- 不因单索引空就整页铺读；先换更合适的内容索引
- 如果结果里 `log.md` 或其他辅助文件靠前，先收窄索引范围
- 只有证据不足时才升级整页 Read，且整页限最相关 **2-4 页**

#### 本地知识库未命中时
如果知识库里没有该论文相关内容，必须先明确说明：

> 本地知识库中未找到该论文的现成条目，以下将以你提供的论文信息和代码仓库为主进行分析。

如果知识库已有相关页面，回答中必须使用 `[[wikilink]]` 引用。

### 2. fallback：search-index-first

当出现以下任一情况时回退：
- JdocMunch 不可用
- section 命中为空
- section 命中明显失真
- 用户问题在问索引结构 / 注册表 / 知识库规模

```bash
python ".agents/scripts/search_index.py" --index-path "<index_path>" --query "<用户问题>"
```

规则：
- 取前 3-5 个候选页
- 仍不整篇铺读 `index.md`
- 只有 fallback 也不足时，才局部读取 `wiki/index.md`

### 3. 双重失败收口

如果：
- JdocMunch 不可用或失真
- 且 `search_index.py` 也无法给出有效候选

则必须明确说明：

> 本地知识库未命中可用条目，以下将仅基于你提供的论文材料与代码仓库进行对照分析。

此时：
- 不要伪造知识库引用
- 论文层分析只依赖用户给的 PDF / 标题
- 代码层分析只依赖用户给的 GitHub / 本地仓库

### 4. 代码源入口定位

| 场景 | 必做动作 |
|---|---|
| 本地代码 | 找入口、配置、模型、数据、训练、评估目录，再沿调用链分析 |
| 远程仓库 | 先读 README 和目录结构，再定位最接近论文模块的实现文件 |

#### 代码层检查表
- 入口：train / eval / infer script
- 配置：yaml/json/argparse/hydra
- 模型：model / backbone / head / loss
- 数据：dataset / dataloader / transforms
- 评估：metric / eval loop

### 5. 论文-代码对齐

必须显式回答：
- 论文核心模块 → 对应文件 / 类 / 函数
- 程序从哪里启动
- 数据如何进入模型
- forward 主路径怎么走
- loss 在哪里算
- 推理 / 评估在哪里
- 哪些是论文核心，哪些是工程包装
- 是否存在实现变体 / 简化 / 魔改

如果知识库中已经存在论文深读结果，还必须优先利用这些证据：

- `## 关键公式`
- `## 关键图示`
- `## 代码对照线索`

并在回答里额外显式回答：

- 哪个公式最可能对应代码里的 `loss` / `criterion`
- 哪个打分公式最可能对应 `score` / `metric` / `anomaly map`
- 哪张结构图最能映射 `model/backbone/head/memory` 的模块边界
- 如果论文公式和仓库实现不一致，差异发生在参数化、归一化、损失聚合还是推理后处理

### 6. 缝合建议（按需）

仅当用户明确要求时执行。

| 维度 | 判断内容 |
|---|---|
| 任务兼容 | 无监督 / 弱监督 / 训练自由 / 多模态是否兼容 |
| 模块互补 | backbone / 时序建模 / loss / 数据增强 / 异常评分 / 记忆模块 / 多模态入口 |
| 代码落点 | 替换 backbone / 加 branch / 加 loss / score fusion / 重写训练流程 |
| 改造成本 | 低 / 中 / 高 |

输出要求：
- 2-4 个候选对象
- 每个候选的互补点、模块落点、收益、风险
- 一个 MVP 缝合方案

如果不能明确模块落点，只能给方法级建议，不能假装给实现级建议。

### 7. 收敛到实现

当用户目标偏“写代码”时，最后必须输出：
- 模块拆分建议
- 数据流 / 伪代码
- 重构建议
- 最小可复现版本构成

---

## 推荐输出结构

```markdown
## 论文层
- 问题 / 方法 / 结论 / 局限

## 代码层
- 入口 / 模型 / 训练 / 推理 / loss / dataset

## 论文-代码对照
- 模块 A -> 路径 / 类 / 函数

## 公式-代码对照
- 公式 1 -> `loss.py` / `trainer.py` / `forward`

## 图示-代码对照
- 图 1 中的模块边界 -> `model.py` / `backbone.py` / `head.py`

## 一致与差异
- 核心是否如实落地
- 哪些是工程包装 / 仓库特有改动

## 缝合对象（按需）
- 候选 / 互补点 / 落点 / 收益 / 风险 / MVP

## 重写指南（按需）
- 模块拆分 / 最小可复现版本
```

---

## 强制约束
- 禁止跳过 JdocMunch（`index.md` 是 fallback）
- 禁止全库铺读（section 优先，整页限 2-4 页）
- 禁止论文-代码两层脱节（必须显式映射）
- 禁止忽略知识库中已经存在的 `关键公式 / 关键图示 / 代码对照线索`
- 禁止空泛缝合建议（无互补点/落点/收益/风险不推荐）
- 禁止盲读整个仓库（先入口和关键模块，再深读）
- 禁止凭记忆猜论文（依赖知识库 + 论文 + 代码）
- 禁止把框架胶水当论文创新

---

## 高价值结果固化

满足以下任一情况时，询问是否保存为 `wiki/syntheses/`：
- 回答超过 2 段
- 具有对照 / 总结 / 实现指导价值

固定话术：

> 这是一个有价值的总结，是否需要我将其保存到 `wiki/syntheses/` 目录？

用户同意后：
- 新建 kebab-case synthesis 页面
- 更新 `wiki/index.md`
- 更新 `wiki/log.md`

---

## 日志

```markdown
## [YYYY-MM-DD] query | <操作简述>
- **输出**: <引用页面列表 或 "即时回答未保存">
```

---

## 关联连接
- [[wiki/index.md]] — fallback 元数据入口
- [[wiki/log.md]] — 操作日志
- [[AGENTS.md]] — 全局规范
