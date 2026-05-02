# LLM Wiki 知识库

本项目是一个基于 [Karpathy 的 LLM Wiki 理念](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 构建的 Obsidian 知识库。

## 核心理念

将碎片化的信息编译成**结构化、高度相互链接**的知识网络，便于 AI 辅助学习和研究。

## 目录结构

```

🏛️ 你的知识库文件夹 (LLM-Wiki-Vault)
├── 🖼️ assets/                   ← 统一媒体资源层：存放图片、PDF、附件（Obsidian设置附件路径至此）
│
├── 📥 raw/                      ← 原始资料收件箱（只读事实层，文件处理后移动至 archive）
│   ├── 📄 01-articles/          ← 网页剪藏、技术文章 (.md)
│   ├── 🎓 02-papers/            ← 论文、深度研报、PDF文档
│   ├── 🎙️ 03-transcripts/       ← 视频/播客转录文本、会议记录
│   ├── 💡 04-meeting_notes/     ← 头脑风暴或会议纪要等
│   └── 🗃️ 09-archived/           ← 已归档区：`/ingest` 执行成功后，源文件自动移动至此
│
├── 🧠 wiki/                     ← 知识编译输出层（LLM 拥有完全写权限，人类阅读层）
│   ├── 📑 index.md              ← 全局索引入口：上层是导航层（快速入口/按主题浏览），下层是完整注册表
│   ├── 📜 log.md                ← 行为流水线：以 Grep-friendly 格式记录 ingest/query 历史
│   ├── 🏗️ concepts/             ← 抽象层：方法论、架构模式、第一性原理 
│   ├── 👥 entities/             ← 实体层：人名、公司、工具软件、项目 
│   ├── 🔍 sources/              ← 摘要层：针对 raw 文件的一对一核心观点提炼 
│   └── 💎 syntheses/            ← 综合层：针对复杂提问生成的深度研究报告 
│
├── 🤖 AGENTS.md                 ← 全局心智规范：定义语言协议、读写权限与 Wiki Schema
│
└── ⚙️ .agents/                  ← Claude Code 官方配置目录
    └── 🛠️ skills/               ← Agent Skill中心
        ├── ⚙️ ingest/           ← 自定义：编译收件箱 raw 文件到 wiki，并执行 09-archived 归档
        ├── 📚 paper-deep-reading/ ← 自定义：深读论文 PDF，抽图到 assets，沉淀公式空位/LaTeX 草稿与代码对照线索，并为 query-with-code 预埋结构化证据
        ├── 🔎 query/            ← 自定义：优先通过 JDocMunch 做 section-level 检索，再精读少量候选段落/页面并生成带双链引用的回答；`index.md` 仅作为 fallback
        ├── 🔎 query-with-code/  ← 自定义：可以对代码和对应论文进行分析
        ├── 🩺 lint/             ← 自定义：知识体检，检查死链、孤儿页、完整注册表缺失与知识冲突
        ├── 🔌 excalidraw-diagram ← 开源skill：创建更生动的excalidraw
        ├── 🔌 mermaid-visualizer ← 开源skill：创建更生动的mermaid
        ├── 🔌 obsidian-canvas-creator ← Obsidian官方：调用 Obsidian 原生 API 创建canvas画布
        ├── 🔌 obsidian-markdown  ← Obsidian官方：使用obsidian的markdown格式
        ├── 🔌 obsidian-cli/     ← Obsidian官方：调用 Obsidian 原生 API 进行检索、打开页面
        └── 🪄 defuddle/         ← Obsidian官方：将网页 URL 自动清理并转化为 Markdown 存入 raw/
```


## 使用方式

配置`JDocMunch MCP`：
```json
"mcp": {
  "jdocmunch": {
    "type": "local",
    "command": [
    "uvx",
    "jdocmunch-mcp",
    ],
    "enabled": true
  },
}
```
在 Obsidian 中打开本 vault，使用Claude Code或者Claudian插件执行操作。

### 常用命令

- `/query <问题>` — 在知识库中搜索相关内容；默认先调用 `JDocMunch` 的 `search_sections -> get_section/get_sections` 做 section-level 检索，必要时再回退到 `index.md` / 本地脚本
- `/query-with-code <问题>，<代码仓库地址>` — 在知识库中搜索对应论文和代码
- `/paper-deep-reading <pdf路径>` — 先做论文证据层：默认只在正文主论文范围内召回图表候选，按“先解释方法，再证明效果/效率”的保守策略排序，再以 `2 图 + 1 表` 软配额落盘到 `assets/`，并在 wiki/source 中沉淀关键公式空位 / LaTeX 草稿与代码对照线索
- `/ingest` — 将新的原始资料编译到知识库；当输入是论文 PDF 时，默认先调用 `paper_deep_read.py`，再完成摘要、实体/概念、索引、日志与归档
- `/lint` — 检查知识库健康度（死链、孤儿页面）

### 本地辅助脚本

- `python .agents/scripts/pdf_tool.py extract-text <pdf>` — 抽取论文全文文本（优先 `pdftotext`，失败回退 `pymupdf`；当前默认未接入 MinerU）
- `python .agents/scripts/pdf_tool.py find <pdf> "Figure 1" --mode auto` — 查找锚点位置与页码（先 PDF 文本，失败再 OCR）
- `python .agents/scripts/pdf_tool.py render-page <pdf> --page 3 --output /tmp/page-3.png` — 渲染整页截图
- `python .agents/scripts/pdf_tool.py snapshot-query-preview <pdf> "Table II" --preset table --mode auto` — 只返回候选元数据，不渲染 PNG，适合预览正文图表候选
- `python .agents/scripts/pdf_tool.py snapshot-query <pdf> "Figure 1" --output assets/papers/foo/figure-01.png --preset figure --mode auto` — 按查询自动裁图（支持 Figure/Fig.、罗马数字、跨页候选打分与 OCR fallback）
- `python .agents/scripts/pdf_tool.py snapshot-rect <pdf> --page 3 --rect 10,20,500,700 --output assets/papers/foo/figure-01.png` — 按矩形精确裁图
- `python .agents/scripts/paper_deep_read.py <pdf>` — 生成 `wiki/sources/摘要-*.md` 的深读骨架、文本缓存、图示占位与代码对照线索，并执行“正文候选召回 + 保守版价值排序 + `2 图 + 1 表` 软配额”

### 论文图表自动选择口径

- `pdf_tool.py` 负责截图质量与定位质量，例如 `snapshot-query-preview`、`snapshot-query` 返回的 `score`，它不表示论文内容价值。
- `paper_deep_read.py` 负责论文证据价值排序，会基于正文候选的 `query/snippet/page_number/kind` 生成独立的 `value_bucket`、`value_score` 和 `selection_reason`。
- 默认候选范围只扫主论文正文，遇到 `References`、`Appendix`、`Appendices`、`Supplementary`、`Supplemental` 后停止，不把这些边界后的图表纳入默认候选池。
- caption 召回支持 `Figure`、`Fig.`、`Table`、`Tab.`，编号同时支持阿拉伯数字和罗马数字，例如 `Figure 2`、`Fig. IV`、`Table II`。
- 默认排序采用保守版策略，优先保留解释方法的架构图、训练框架图、目标函数图，其次再保留证明效果、效率或权衡关系的图表。
- 落盘目标配额是 `2 图 + 1 表`。这是软配额，不是硬凑数。缺少高价值表格时允许返回缺额，并通过 `selection_deficit` 明确记录，不会为了补满数量强行保留低价值 filler。

### 自动回归重点

- 完整命中场景：存在高价值方法图、补充图和高价值表格时，结果应为 `2 图 + 1 表`。
- 缺表场景：没有达到阈值的高价值表格时，不生成低价值 `table-01.png`，而是返回 `selection_deficit.missing.table` 缺额信息。
- 罗马数字场景：`Table II`、`Fig. IV` 这类正文 caption 需要被正确召回并参与排序。
- 确定性重跑场景：同一 PDF 连跑两次，入选项的 `query/page_number/kind/value_bucket/selection_rank` 应保持一致。

## 索引设计

当前 `wiki/index.md` 采用两层结构：

- **导航层**：`快速入口`、`按主题浏览`，用于帮助人和 Agent 先缩小主题范围，而不是一次性展开整个知识库。
- **完整注册表**：`Sources / Entities / Concepts / Syntheses`，用于维护稳定登记，供 `/ingest`、`/query`、`/lint` 等工作流使用。

这套设计的目标是：
- 避免把 `index.md` 写成一篇越来越长的总综述
- 避免 query 阶段一次性读取太多页面，降低上下文爆炸
- 让 lint 只对“完整注册表”做一致性校验，而不把导航层误判为注册来源

当前 `/query` 的主路径已经调整为“**优先通过 JDocMunch 检索 wiki 内容的相关 sections，再精读少量候选段落或页面**”，而不是默认整篇读取 `index.md`。

`wiki/index.md` 现在主要承担两类职责：
- **元数据 / 注册表入口**：提供导航层与完整注册表，服务 `/ingest`、`/lint` 和 query 的结构化 fallback
- **query fallback**：仅在 JDocMunch 不可用、命中为空/失真，或用户问题本身是在问索引结构时，才退回 `search_index.py` 或局部读取 `wiki/index.md`

说明：JDocMunch 的增强型上下文工具（如 `get_section_context`）受安装版本影响，不应当作所有环境都稳定存在的基线能力；本仓库默认依赖 `search_sections + get_section/get_sections + toc/outline` 这一组更稳健的公共能力。

## 知识来源

- 学术论文（来自Google Scholar）
