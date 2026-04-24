---
name: query
description: 在本地 Wiki 知识库中回答问题。默认走 JdocMunch-first：优先检索 `wiki/sources|entities|concepts|syntheses` 的相关 sections；仅在 JdocMunch 不可用、命中失真/为空、或用户在问索引结构时，才回退到 `search_index.py` 或局部读取 `wiki/index.md`。回答必须使用 `[[wikilink]]` 引用来源。
user-invocable: true
---

# query 技能

## 目标
- 基于本地 wiki 回答问题
- 默认少量取证，不整库铺读
- 高价值回答可固化为 synthesis

## 触发
- `/query <问题>`
- 自然语言询问“我的笔记/知识库/记录里关于 X”

## 降级
如果问题是纯通用知识，且本地知识库无相关内容：

> 本地知识库中未找到相关内容，以下为通用知识回答：[直接回答]

---

## 执行顺序

### 0. 路径引导

```bash
python ".agents/scripts/router.py" query "<用户问题>"
```

读取 JSON：`wiki_dir / raw_dir / index_path / log_path`

### 1. 主路径：JdocMunch-first

#### 主检索语料
- `wiki/sources/`
- `wiki/entities/`
- `wiki/concepts/`
- `wiki/syntheses/`

#### 非主检索语料
- `wiki/index.md`
- `wiki/log.md`

#### 推荐索引名
- `llm-wiki-sources`
- `llm-wiki-entities`
- `llm-wiki-concepts`
- `llm-wiki-syntheses`

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
| 主题 / 关系 / 比较 | `syntheses -> entities -> concepts -> sources` |
| 具体方法 / 实体 | `entities -> concepts -> sources -> syntheses` |
| 论文出处 / 元信息 / 实验细节 | `sources -> entities -> syntheses` |
| 知识库结构问题 | 不走 JdocMunch，直接 fallback |

#### JdocMunch 升降级规则
- 默认先综合命中的 sections
- 不要因为一个索引没命中就整页铺读；先换更合适的内容索引
- 如果结果里 `log.md` 或其他辅助文件靠前，先收窄索引范围，而不是扩大读取范围

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

### 3. 页面/段落读取规则

- 默认优先读少量 sections
- 只有证据不足时才升级为整页 Read
- 整页 Read 默认只读最相关的 **2-4 个页面**

#### 整页 Read 优先级
- 主题 / 比较 / 关系：`concept / synthesis`
- 具体方法 / 实体：`entity`，再补 `concept / source`
- 实验细节 / DOI / 数据集：`source`

---

## 回答规则

### 引用
- 必须使用 `[[页面名称]]`
- 同页信息不要过度重复引用
- 原文摘录用 `> 引用内容`

### 结构
优先输出：
- 直接结论
- 关键依据
- 必要时补充对比 / 风险 / 例外

---

## 高价值内容固化

满足以下任一情况时，询问是否保存为 synthesis：
- 回答超过 2 段
- 具有分析 / 对比 / 总结性

固定话术：

> 这是一个有价值的总结，是否需要我将其保存到 wiki/syntheses/ 目录？

用户同意后：
- 新建 synthesis
- 更新 `wiki/index.md`
- 必要时补导航层

---

## 日志

查询结束后必须追加：

```markdown
## [YYYY-MM-DD] query | <操作简述>
- **输出**: <引用页面列表或"即时回答未保存">
```

---

## 硬约束
- 禁止凭记忆回答
- 禁止静默回答“本地无内容”场景
- 禁止全库铺读
- `index.md` 现在是 fallback，不是默认第一跳

---

## 关联连接
- [[wiki/index.md]] — fallback 元数据入口
- [[wiki/log.md]] — 操作日志
- [[AGENTS.md]] — 全局规范
