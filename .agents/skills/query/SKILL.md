---
name: query
description: 在本地 Wiki 知识库中回答问题。默认走 JdocMunch-first：优先检索 `wiki/sources|entities|concepts|syntheses` 的相关 sections；仅在 JdocMunch 不可用、命中失真/为空、或用户在问索引结构时，才回退到 `search_index.py` 或局部读取 `wiki/index.md`。回答必须使用 `[[wikilink]]` 引用来源。
user-invocable: true
---

# query 技能

## 核心目标
基于本地 Wiki 知识库的 `sources / entities / concepts / syntheses` 四个内容目录，通过 JdocMunch 的 section-level 精准检索来回答问题。JdocMunch 先对本地文档建索引（`index_local`），然后按 heading 层级切分为 Section，支持 hybrid 检索（BM25 + 语义融合，`use_embeddings: auto` 时任一 embedding provider 配置即启用语义层）。默认不走整篇铺读，只在必要时升级为页面级精读或回退到 `search_index.py`。所有回答必须附带 `[[wikilink]]` 引用，高价值回答可固化为 `synthesis`。

---

## 何时触发

- 用户输入 `/query <问题>`
- 用户要求"帮我查一下"、"搜索知识库里关于 X 的内容"
- 用户要求"找笔记 / 看知识库 / 搜我的记录"
- 用户询问"这个知识库里有没有关于 X 的内容"
- 用户要求对知识库中的内容做对比、总结、分析
- 用户要求基于知识库生成方案、推荐、建议

如果用户问题完全不涉及本地知识库（如纯粹问天气、翻译句子），不走 /query，直接降级为通用回答。

---

## 工作流

### 步骤 0：路径引导

```bash
python ".agents/scripts/router.py" query "<用户问题>"
```

读取 JSON，获取 `wiki_dir`、`raw_dir`、`index_path`、`log_path`。

### 步骤 1：主路径 — JdocMunch-first

#### 检索语料

| 类别 | 目录 | 索引名 |
|---|---|---|
| 主检索语料 | `wiki/sources/` `wiki/entities/` `wiki/concepts/` `wiki/syntheses/` | `llm-wiki-sources` `llm-wiki-entities` `llm-wiki-concepts` `llm-wiki-syntheses` |
| 非主检索语料 | `wiki/index.md` `wiki/log.md` | — |

#### 推荐索引参数

- `incremental: true`
- `use_ai_summaries: false`
- `use_embeddings: auto`

`use_embeddings: auto` 的含义：任一 embedding provider（`OPENAI_API_KEY`、`GOOGLE_API_KEY`、或本地 `sentence-transformers`）配置时自动启用语义层，与 BM25 做 hybrid 融合；均未配置时退化为纯 BM25 关键词检索。

##### Section ID 格式

JdocMunch 的 section ID 是稳定且可读的，格式为 `{repo}::{doc_path}::{ancestor-chain/slug}#{level}`，例如 `llm-wiki-concepts::concepts/SSM.md::定义/核心公式#2`。同一篇文档里新增一个标题不会干扰其他分支的 section ID，可以在日志或引用中直接使用。

#### JdocMunch 调用链

1. `search_sections` — 先搜索，不急着拿全文。返回 section 摘要、标题、层级和 `section_id`
2. `get_section` — 只取命中 section 的精确片段（byte-offset 读取，不读全文）
3. `get_section_context` — 命中证据不充分时，补祖先标题链和子 section 摘要，再决定是否取全文
4. `get_sections` — 需要同时取多个 section 时用批量接口，减少往返

##### 结构导航（搜索不足时使用）

- `get_toc` — 查看某个索引下所有 section 的扁平列表
- `get_document_outline` — 只看一个文档的 section 层级，不取内容
- `get_toc_tree` — 按文档查看嵌套的 section 树

#### 问题类型 → 搜索顺序

| 问题类型 | 搜索顺序 |
|---|---|
| 主题 / 关系 / 比较 | `syntheses → entities → concepts → sources` |
| 具体方法 / 实体 | `entities → concepts → sources → syntheses` |
| 论文出处 / 元信息 / 实验细节 | `sources → entities → syntheses` |
| 知识库结构问题 | 不走 JdocMunch，直接跳到步骤 2 |

#### JdocMunch 升降级规则

- 默认先综合命中的 sections，不做无差别铺读。
- **不要因为一个索引没命中就整页铺读**：先换更合适的内容索引重试。
- 如果 `search_sections` 命中不足，先试 `get_toc` / `get_document_outline` 按结构导航找相关 section，再 `get_section` 取证。
- 如果结果里 `log.md` 或其他辅助文件靠前，先收窄索引范围，而不是扩大读取范围。

### 步骤 2：fallback — search-index-first

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

### 步骤 3：页面 / 段落读取规则

- 默认优先读少量 sections
- 只有证据不足时才升级为整页 Read
- 整页 Read 默认只读最相关的 **2-4 个页面**

#### 整页 Read 优先级

| 问题类型 | 优先读 | 再补读 |
|---|---|---|
| 主题 / 比较 / 关系 | `concept` / `synthesis` | — |
| 具体方法 / 实体 | `entity` | `concept` / `source` |
| 实验细节 / DOI / 数据集 | `source` | — |

### 步骤 4：降级 — 无本地内容时

如果问题属于纯通用知识、且本地知识库在所有检索路径下均无相关内容：

> 本地知识库中未找到相关内容，以下为通用知识回答：[直接回答]

---

## 推荐输出结构

优先使用这个结构回答：

```markdown
## 结论
2~3句详细的核心结论。

## 关键依据
- 依据 1（引用 [[页面名称]]）
- 依据 2（引用 [[页面名称]]）

> 原文摘录

## 补充说明
- 对比 / 风险 / 例外（按需添加）
```

如果问题简单、结论单一，可裁剪为单段落回答，但仍需保留 `[[wikilink]]` 引用。

---

## 回答规则

### 引用
- 必须使用 `[[页面名称]]` 双链
- 同页信息不要过度重复引用
- 原文摘录用 `> 引用内容`

### 搜索策略
- 默认少量取证，不整库铺读
- 利用 JdocMunch section 级检索精确定位
- 只在证据不足时升级为页面级读取

---

## 强制约束

- **禁止凭记忆回答**：所有结论必须来自本地知识库的实际检索结果
- **禁止静默回答"本地无内容"**：必须明确输出降级提示语后，再给通用知识回答
- **禁止全库铺读**：优先 section 级检索，整页 Read 仅限 2-4 个最相关页面
- **禁止以 `index.md` 作为默认第一跳**：`index.md` 现在是 fallback，JdocMunch 搜索才是主路径
- **禁止在 JdocMunch 可用时跳过它**：必须先尝试 JdocMunch，再决定是否回退

---

## 最佳提问方式示例

### 示例 1：标准查询
> /query Transformer 的各代变体有哪些，优缺点对比

### 示例 2：聚焦单一实体
> /query BiSP 方法的核心思想和已知短板是什么

### 示例 3：方法融合分析
> /query 基于 BiSP 的基础，知识库里有哪些可融合的思路或方法，帮我整合成一份 PRD

### 示例 4：全局概览
> /query 这个知识库主要覆盖了哪些研究方向和论文

### 示例 5：概念查询
> /query 解释什么是 State Space Model，和 Transformer 的关系是什么

---

## 高价值内容固化

满足以下任一情况时，主动询问用户是否保存为 synthesis：

- 回答超过 2 段
- 具有分析 / 对比 / 总结性
- 明显具有被重复使用的价值

固定话术：

> 这是一个有价值的总结，是否需要我将其保存到 `wiki/syntheses/` 目录？

用户同意后：

- 统一通过 `write_synthesis.py` 写入页面、登记 `index.md`、追加 `log.md`
- 必要时通过 `--nav-section` 同步补导航层（快速入口、按主题浏览）

固化示例：

```bash
python ".agents/scripts/write_synthesis.py" \
  --workspace-root "<workspace_root>" \
  --slug "<synthesis-slug>" \
  --summary "<一句话总结>" \
  --content-file "<tmp-content-file>" \
  --tag "综合分析" \
  --source "raw/09-archived/foo.pdf" \
  --related "BiSP" \
  --related "StateSpaceModel" \
  --log-summary "保存 <主题> 综合页"
```

---

## 日志

查询结束后调用 `write_log.py` 追加日志：

```bash
python ".agents/scripts/write_log.py" \
  --log-path "<log_path>" \
  --action query \
  --summary "<操作简述>" \
  --detail "输出=<引用页面列表>"
```

生成的日志条目格式为：

```markdown
## [YYYY-MM-DD] query | <操作简述>
- **输出**: <引用页面列表>
```

---

## 关联连接

- [[wiki/index.md]] — fallback 元数据入口与完整注册表
- [[wiki/log.md]] — 查询与沉淀日志
- [[AGENTS.md]] — 知识库全局架构规范
