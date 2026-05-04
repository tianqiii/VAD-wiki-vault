---
name: query
description: 在本地 Wiki 中回答问题。凡用户说 /query、查知识库、搜笔记、找论文信息、对比方法、生成方案时必须使用。默认 JdocMunch section 级检索，失败才回退 search_index.py 或局部读 index.md。回答必须带 [[wikilink]] 引用。
user-invocable: true
---

# query 技能

## 触发

- `/query <问题>`
- "查一下 / 搜索知识库 / 找笔记 / 看我的记录"
- "知识库里有没有 / 关于 X 的内容"
- 对比、总结、分析、方案生成类请求
- 不涉及本地知识库的纯通用问题不走 query，直接回答。

## 流程

1. **路径解析**
   ```bash
   python ".agents/scripts/router.py" query "<问题>"
   ```
   读取 `wiki_dir/raw_dir/index_path/log_path`。若 `missing_paths` 非空，停止。

2. **主路径：JdocMunch-first**

   检索前先判断问题需要的材料类型，再推断相关 tags：
   - 方法/系统/工具/人物 → `entities` 为主，必要时补 `concepts/sources`。
   - 概念、方法谱系、任务定义、对比框架 → `concepts/syntheses` 为主。
   - 论文出处、实验、图表、公式、证据锚点 → `sources` 为主。
   - 复杂综合、路线图、方案生成 → `syntheses` 为主，再回查 `entities/concepts/sources`。

   先读取 tag 池与完整注册表摘要，得到当前可用 tags 和页面一句话描述：
   ```bash
   python ".agents/scripts/wiki_tags.py" --wiki-dir "<wiki_dir>" --index-path "<index_path>" --json
   ```
   根据问题选择 1-N 个相关 tags；如果同时涉及视频异常检测和铁路入侵检测，应同时使用 `video-anomaly-detection` 与 `railway-intrusion-detection` 或当前 tag 池中的等价现有 tag。

   检索 `wiki/sources|entities|concepts|syntheses`，调用链：`search_sections` → `get_section` → `get_section_context`（证据不足时补祖先链和子 section 摘要）。批量取用 `get_sections` 减少往返。必要时 `get_toc` / `get_document_outline` 按结构导航。

   索引名必须显式唯一：当前 vault 用 `{vault-name}-wiki`，禁止依赖默认 `local/wiki`。若 `list_repos` 可见但 `search_sections` 报 `Repo not found`，先重建索引再重试。重建仍失败才回退。回答中说明失败的是 JdocMunch 检索层，不是 Wiki 缺失。

   ```python
   jdocmunch_index_local(
     path="/home/nini/Documents/Vaults/VAD-vault/wiki",
     name="vad-vault-wiki",
     incremental=False,
     use_ai_summaries=False,
     use_embeddings="auto"
   )
   ```

   搜索顺序：主题/关系/比较 → `syntheses→entities→concepts→sources`；方法/实体 → `entities→concepts→sources→syntheses`；论文出处/实验 → `sources→entities→syntheses`；索引结构问题 → 直接到步骤 3。JdocMunch 检索时优先按 type 对应目录收敛，再按推断出的 tags 过滤或加权；不要先读全库。

   升降级：不因单索引空就铺读全库；命中不足先换索引重试；辅以 TOC/outline 导航；`index/md` 排前时先收窄索引范围。

3. **Fallback：search-index-first**

   JdocMunch 不可用、命中为空/失真、或用户问索引结构/注册表时：
   ```bash
   python ".agents/scripts/search_index.py" --index-path "<index_path>" --wiki-dir "<wiki_dir>" --query "<问题>" --type concept --tag video-anomaly-detection
   ```
   依据问题替换或重复传入 `--type` / `--tag`。取前 3-5 个候选页；仍不足才局部读取 `wiki/index.md`。

4. **读取深度控制**

   默认 section 级精读；整页 Read 限最相关的 2-4 页。主题/比较优先读 concept/synthesis；方法/实体优先读 entity；实验/Dataset 优先读 source。

5. **无命中收口**

   所有路径均无相关内容时：
   > 本地知识库中未找到相关内容，以下为通用知识回答：

## 输出

优先用此结构；简单问题可裁为单段落，但必须带 `[[wikilink]]`：

```markdown
## 结论
2-3 句核心结论。

## 关键依据
- 依据 1（[[页面]]）
- 依据 2（[[页面]]）
> 原文摘录

## 补充说明
对比 / 风险 / 例外（按需）。
```

## 强制约束

- 禁止凭记忆回答；所有结论来自检索结果。
- 禁止跳过 JdocMunch（可用时必须先尝试）。
- 禁止全库铺读；section 优先，整页限 2-4 个。
- `index.md` 是 fallback，不是主入口。
- 必须用 `[[wikilink]]` 引用；未命中时明确输出降级提示。

## 高价值结果固化

回答超过 2 段或有复用价值时，询问用户：
> 这是一个有价值的总结，是否需要我将其保存到 `wiki/syntheses/` 目录？

用户同意后：
```bash
python ".agents/scripts/write_synthesis.py" \
  --workspace-root "<workspace_root>" \
  --slug "<slug>" --summary "<一句话>" \
  --content-file "<tmp-file>" \
  --tag "<topic-tag>" \
  --source "raw/09-archived/foo.pdf" \
  --related "Entity" --related "Concept" \
  --log-summary "保存 <主题> 综合页"
```


## 日志

```bash
python ".agents/scripts/write_log.py" --log-path "<log_path>" --action query --summary "<简述>" --detail "输出=<引用页面列表>"
```

## 收尾

**落盘后运行确定性底座检查**
```bash
python ".agents/scripts/lint.py" --wiki-dir "<wiki_dir>" --raw-dir "<raw_dir>" --json
```
   以脚本 JSON 为事实来源；不要在脚本已有结果之外重复铺读全库。脚本退出码 `1` 表示存在 P0，不是工具失败。
