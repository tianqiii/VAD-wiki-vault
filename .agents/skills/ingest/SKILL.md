---
name: ingest
description: 将 raw/ 未归档资料编译为 Obsidian LLM Wiki 并归档。凡用户说 ingest、入库、摄入、导入、整理 raw、处理论文/文章/PDF、加入知识库、生成 source/entity/concept、为 query-with-code 准备证据层时必须使用。禁止读取 raw/09-archived。
user-invocable: true
---

# ingest 技能

## 目标与边界

把 `raw/` 未处理资料编译进 `wiki/`：创建/更新 `sources/entities/concepts`，同步 `wiki/index.md` 与 `wiki/log.md`，成功后归档到 `raw/09-archived/`。

硬边界：禁止读取 `raw/09-archived/`；禁止修改源文件正文；禁止使用你自己的知识；输出简体中文；所有 wiki 页必须有 `## 关联连接`。Entity 用 TitleCase；source/concept/synthesis 用 kebab-case。

## 触发与批处理

- `/ingest`：扫描 `raw/` 中除 `09-archived/` 外的未处理资料。
- `/ingest <path>`：只处理指定文件。
- 多文件逐个处理；每个文件完成 source/entity/concept/index/log/archive 后再处理下一个。
- 若用户路径位于 `raw/09-archived/`，立即拒绝读取并说明归档层只读。

Slug：取源文件名去扩展名，小写，将空格与非字母数字合并为 `-`，去首尾 `-`。`source`、assets、`.cache/agents/papers/{slug}/`、`paper_deep_read.py` 必须同 slug。

## 主流程

1. **路径解析**
   ```bash
   python ".agents/scripts/router.py" ingest
   ```
   读取 `workspace_root/wiki_dir/raw_dir/index_path/log_path`；若 `missing_paths` 非空，停止。记录当前文件绝对路径，所有产出绑定该文件。

2. **类型判定与重复防护**
   - `raw/02-papers/*.pdf`：论文模式，先跑 `paper_deep_read.py`，再补知识网络。
   - `raw/01-articles/*.md`、`.md`、`.txt`：通用模式，读全文编译。
   - 其他格式：跳过并报告，不猜测解析。
   - 处理前检查 `wiki/sources/摘要-{slug}.md`；若存在且 `sources` 指向当前文件或同名归档文件，复用，不重复创建。

3. **提炼与写入**
   - source：`wiki/sources/摘要-{slug}.md`。
   - entity：明确命名的方法/系统/工具/人物/机构 → `wiki/entities/`。
   - concept：只在无法复用既有概念且有跨资料复用价值时 → `wiki/concepts/`。
   - PDF 深读失败：保留 source 骨架并标注 `需要人工补读`，不归档。

4. **同步 index/log 并归档**
   ```bash
   python ".agents/scripts/write_index.py" --index-path "<index_path>" --section "Sources" --page "摘要-foo" --description "一句话摘要"
   python ".agents/scripts/write_log.py" --log-path "<log_path>" --action ingest --summary "<操作简述>" --detail "变更=..." --detail "冲突=无"
   ```
   仅当 source/entity/concept/index/log 全部就绪且 PDF 深读未失败（无 PDF 提取失败）时归档。归档成功后，把 source/entity/concept frontmatter 中旧 `raw/02-papers/` 的 `sources:` 更新为 `raw/09-archived/`；`wiki/` 不得残留 `raw/02-papers/` 的 `sources:` 引用。

## PDF 论文模式

`ingest` 只做总编排；`paper-deep-reading` / `paper_deep_read.py` 负责 PDF 文本抽取、锚点检索、图示裁图、source 骨架、表格描述、公式空位。若用户已先运行 `/paper-deep-reading`，且 `wiki/sources/摘要-{slug}.md` 已含 `## 关键图示`，复用既有 source 和 assets，不重新生成。

所有 `paper_deep_read.py` 调用都带 `--progress --preview-timeout 10`。只有用户要求快看/粗筛/机器卡顿时才加 `--max-candidates N`。

默认规则直出：
```bash
python ".agents/scripts/paper_deep_read.py" "<pdf路径>" --progress --preview-timeout 10
```

复杂版面用 agent 两阶段：中文/中英混排、`图/表` caption、双栏密集、图表相邻、同页多图、排序不稳、后续要 `/query-with-code`、或出现 `selection_deficit/skipped_candidates`。
```bash
python ".agents/scripts/paper_deep_read.py" "<pdf路径>" --selection-mode agent --progress --preview-timeout 10
python ".agents/scripts/paper_deep_read.py" "<pdf路径>" --selection-mode agent --progress --preview-timeout 10 --selected-slot figure-01 --selected-slot table-01
```

图表公式规则：
- 图片写入 `assets/papers/{slug}/`，Wiki 用 `![[papers/{slug}/figure-01.png]]`。
- 入库前验图：不得截到正文交叉引用页，不混入相邻图，caption/坐标轴/图例完整；同编号多次命中时先 `pdf_tool.py find` 消歧，再用真实 caption 页 `snapshot-query --page N` 重裁。
- 原始文件中的表格在 `## 表格速览` 使用markdown格式转录/描述；每篇 1-2 张关键表，对比表优先，消融表次之。
- 公式转写：优先从 `.cache/agents/papers/{slug}/source_text.txt` 转写 LaTeX；保留 `原文定位/原文描述/解释/证据`。找不到写“未在文本缓存中找到，需人工回查 PDF”；模糊/截断用 `%` 占位说明原因；禁止凭 metadata 或经验猜公式。

## 页面结构

Source frontmatter 固定 5 字段；Metadata 放正文。创建时可暂指向当前 raw 路径，归档后改为 `raw/09-archived/{文件名}`：
```markdown
---
title: "摘要-{slug}"
type: source
tags: [来源]
sources: ["raw/09-archived/{文件名}"]
last_updated: YYYY-MM-DD
---
```

论文 source 用以下区块：`## Metadata`、`## 核心摘要`、`## 关键图示`、`## 表格速览`、`## 关键公式`、`## 代码对照线索`、`## 关联连接`。

表格速览：标题写 `### Table N — 英文标题（第 N 页）`；列名保留英文；本文方法/最优值加粗；脚注用 `>`；定位写 `- **出处**: 第 N 页 Table N。`；禁止猜数值、中文重命名列名、空表格或只写“待补”。转录失败用 warning callout 保留关键 snippet。

代码对照线索只写待核验映射：`loss/score/module` → 可能对应文件或函数；必须说明依据页码/公式/图表。

Entity/concept frontmatter 同样含 `title/type/tags/sources/last_updated`。正文至少含 `## 定义`、`## 关键信息`、`## 关联连接`，并回链 source。

## 证据与概念复用

写入前按断言强度处理：
- 事实型：作者、年份、venue、数据集、指标、数值、公式名、组件；必须能定位，找不到写 `未在正文中找到` 或不写。
- 解释型：问题、机制、实验结论、局限；必须附页码、图表 caption、段落或 source 骨架线索。
- 推断型：代码映射、概念归类；必须写 `可能/待核验` 并说明依据。

证据格式：`- 证据：第 N 页 Fig. X caption；第 M 页方法段落。` 没有证据锚点的高价值断言，不写成确定语气。

Concept 新建是最后手段。先检索 `wiki/concepts/`、`wiki/index.md` 和相关页面：同义词/翻译不同则复用并补别名；新资料只是案例则增量写入既有 concept；子机制只有跨多篇资料复用时才独立成页；不确定时合并到最接近页面并注明来源限定。

发现知识冲突时暂停并报告，让用户选择“保留并标注 / 新覆盖旧 / 放弃本次”。

## 快速自检

- [ ] 未读 `raw/09-archived/`，未修改源文件正文。
- [ ] source frontmatter 为 5 字段；Metadata 在正文；归档后 `sources:` 指向 `raw/09-archived/`。
- [ ] 高价值事实有证据，或标注 `未在正文中找到/待核验`。
- [ ] 图示已验图并消歧 caption；表格不截图；公式已转写或说明原因。
- [ ] concept 复用优先；source/entity/concept 双向链接，无孤岛页。
- [ ] `index.md` 完整注册表与 `log.md` 已更新；PDF 深读失败未归档。
