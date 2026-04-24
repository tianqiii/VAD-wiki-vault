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
│   └── 🗃️ 09-archive/           ← 已归档区：`/ingest` 执行成功后，源文件自动移动至此
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
        ├── ⚙️ ingest/           ← 自定义：编译收件箱 raw 文件到 wiki，并执行 09-archive 归档
        ├── 🔎 query/            ← 自定义：优先在 index 上做命中搜索，再精读少量候选页面并生成带双链引用的回答
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

- `/query <问题>` — 在知识库中搜索相关内容 会调用 `JDocMunch` 的工具来查找内容
- `/query-with-code <问题>，<代码仓库地址>` — 在知识库中搜索对应论文和代码
- `/ingest` — 将新的原始资料编译到知识库
- `/lint` — 检查知识库健康度（死链、孤儿页面）

## 索引设计

当前 `wiki/index.md` 采用两层结构：

- **导航层**：`快速入口`、`按主题浏览`，用于帮助人和 Agent 先缩小主题范围，而不是一次性展开整个知识库。
- **完整注册表**：`Sources / Entities / Concepts / Syntheses`，用于维护稳定登记，供 `/ingest`、`/query`、`/lint` 等工作流使用。

这套设计的目标是：
- 避免把 `index.md` 写成一篇越来越长的总综述
- 避免 query 阶段一次性读取太多页面，降低上下文爆炸
- 让 lint 只对“完整注册表”做一致性校验，而不把导航层误判为注册来源

当前 `/query` 已开始向“**优先搜索 index 命中条目，再精读候选页**”演进，而不是默认整篇读取 `index.md`。

## 知识来源

- 学术论文（来自Google Scholar）
