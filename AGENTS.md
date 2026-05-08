# 语言设定与核心角色 (Global Rules)
- **语言指令**：无论输入何种语言，你必须始终使用**简体中文**进行思考、回复和知识库的编写。
- **角色定义**：你正在维护一个 **LLM Wiki**（根据 [Karpathy 的规范](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f))，你的任务是将碎片化的信息编译成结构化、高度相互链接的 Obsidian 知识库。

# 核心目录与权限边界 (Immutability & Architecture)
你必须严格遵守以下文件操作权限，这是不可逾越的底线：

- `/raw/` (不可变层 - Immutable)：
  - **绝对只读**。这里存放我的原始素材、网页剪藏和论文材料。
  - **禁止修改或删除此目录下的任何文件**。它是事实的唯一真相来源。
- `/assets/` (媒体资产层)：
  - 存放图片、PDF和媒体。引用时使用 Obsidian 标准语法 `![[文件名称.png]]`。
- `/wiki/` (编译输出层 - You Own This)：
  - 这是你的专属工作区。你需要在此处创建、更新、提炼知识并解决矛盾。

# Wiki 核心文件契约 (The Wiki Schema)
当你在 `/wiki/` 中工作时（尤其是执行写入操作后），必须维护以下基石：

1. **`wiki/index.md` (总目录)** ：
   每次向 wiki 新增知识页后，必须同步更新此文件。
   `wiki/index.md` 采用两层结构：
   - **导航层**：用于快速进入主题网络（如“快速入口”“按主题浏览”），服务于浏览与检索收敛。
   - **完整注册表**：用于稳定登记所有知识页，供 ingest / query / lint 作为一致性依据。
   格式要求：注册表中的条目使用 `[[页面名称]] — 一句话描述`。
    - Entities/Concepts: 使用 TitleCase 命名。
    - Sources/Syntheses: 使用 kebab-case 命名。
    范例：
```markdown
    # Wiki Index

    ## 快速入口
    - [[ConceptName]] — 主题入口。

    ## 按主题浏览
    - [[EntityName]] — 代表方法。

    ## 完整注册表

    ### Sources
    - [[摘要-source-slug]] — 该资料的核心主旨摘要。

    ### Entities
    - [[EntityName]] — 该实体的身份定义或核心功能。

    ### Concepts
    - [[ConceptName]] — 该概念或框架的核心定义。

    ### Syntheses
    - [[synthesis-slug]] — 该页面回答的复杂问题。
```
2. **`wiki/log.md` (操作日志)** ：
    只能追加写入（Append-only）。每次操作后记录：`## [YYYY-MM-DD] <动作> | <操作简述>`。
    操作类型： ingest, query, lint, sync
    范例：
    ```markdown
    ## [2026-04-11] ingest | 引入项目 Claude Code 核心概念
    - **变更**: 新增 [[ClaudeCode]], [[摘要-claude-code-docs]]; 更新 [[index.md]]
    - **冲突**: 无 (或: 冲突 [[RAG架构]], 已标注)

    ## [2026-04-11] query | 解析 Karpathy LLM-Wiki 理念
    - **输出**: 已保存至 [[分析-karpathy-wiki-philosophy]]

    ## [2026-04-11] lint | 周度健康检查
    - **结果**: 修复 2 处死链，发现 1 个孤儿页面 [[UnlinkedPage]]
    ```
3. **内容分类**：
   - `/wiki/concepts/`：存放概念、框架、方法论（如 `Agent_Skill.md`）。
   - `/wiki/entities/`：存放人物、公司、工具、产品（如 `Claude_Code.md`）。
   - `/wiki/sources/`：存放从 `raw/` 提炼出的原始素材摘要。
4. **强制双向链接**：
   每一个 wiki 页面必须包含 `## 关联连接` 区域，使用 Obsidian 双链 `[[页面名称]]` 链接到其他相关概念。绝不能产生孤岛页面。
5. **矛盾处理原则**：
   如果新摄入的知识与旧知识冲突，不要静默覆盖。在页面中新建 `## 知识冲突` 区块，将两种说法都保留并做对比。

# 路径与检索索引泛化规则

- JdocMunch 索引名使用 `<jdocmunch_repo>`：取 `workspace_root` 目录名，转小写，将空格与非字母数字合并为 `-`，去首尾 `-`，再追加 `-wiki`。
- 任何写入 `wiki/` 的操作（新增/更新 source、entity、concept、synthesis）在同步 `wiki/index.md` 后，必须用 `jdocmunch_index_local(path="<wiki_dir>", name="<jdocmunch_repo>", incremental=True, use_ai_summaries=False, use_embeddings="auto")` 刷新检索索引。
- 只有索引缺失、结构大改、section 检索连续失真或明确怀疑索引漂移时，才使用 `incremental=False` 做一次全量重建，并在 `wiki/log.md` 或最终报告中说明原因。
- 保存 synthesis 时，`source` 使用 `<raw_source_path>` 这类相对 `workspace_root` 的真实源材料路径；若资料已归档则指向归档路径，未归档则使用当前 raw 路径，禁止写死示例 PDF。

# 页面 Frontmatter (YAML) 规范
> [!IMPORTANT] 所有生成的 wiki 页面必须包含以下 YAML 头部，且tag部分必须使用kebab-case来命名，否则会导致obsidian报错。

---
title: "页面标题"
type: concept | entity | source | synthesis
tags: [知识标签]
sources:[关联的raw文件相对路径]
last_updated: YYYY-MM-DD
---
