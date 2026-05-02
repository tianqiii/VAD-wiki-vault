---
name: query-with-code
description: 论文-代码对照分析。凡用户说 /query-with-code、对照论文和代码、梳理模型/loss/训练/推理、找模块位置、判断论文代码差异、生成复现/缝合方案时必须使用。默认 JdocMunch-first 检索 Wiki 证据；失败回退 search_index.py。需论文（标题/PDF/知识库条目）和代码（GitHub/本地路径）。
user-invocable: true
---

# query-with-code 技能

## 触发

- `/query-with-code`
- 对照论文和代码解释实现
- 找模块位置、梳理模型/loss/训练/推理/dataset/eval
- 判断论文与代码差异、生成复现/重构/缝合建议

缺输入时追问：> 还缺论文（标题/PDF/知识库条目）和代码（GitHub/本地路径），补上后我会做对照分析。

## 流程

1. **路径解析**
   ```bash
   python ".agents/scripts/router.py" query "<问题>"
   ```
   读取 `wiki_dir/raw_dir/index_path/log_path`。

2. **Wiki 检索：JdocMunch-first**

   检索 `wiki/sources|entities|concepts|syntheses`，调用链：`search_sections → get_section → get_section_context`。索引名必须显式唯一：当前 vault 用 `vad-vault-wiki`。若 `Repo not found`，先重建再重试；仍失败才回退。回答中说明失败的是检索层，不是 Wiki 缺失。

   ```python
   jdocmunch_index_local(
     path="/home/nini/Documents/Vaults/VAD-vault/wiki",
     name="vad-vault-wiki",
     incremental=False, use_ai_summaries=False, use_embeddings="auto"
   )
   ```

   搜索顺序：论文理解/方法对照 → `sources→entities→concepts→syntheses`；公式/模块/loss/score 对照 → `sources→entities→concepts→syntheses`；方法比较/融合 → `syntheses→entities→concepts→sources`。整页 Read 限 2-4 个最相关页面。

3. **Fallback：search_index.py**
   JdocMunch 不可用/命中为空/失真时：
   ```bash
   python ".agents/scripts/search_index.py" --index-path "<index_path>" --query "<问题>"
   ```
    取前 3-5 个候选页；仍不足才局部读 `wiki/index.md`。双重失败时声明：> 本地知识库未命中可用条目，以下将仅基于你提供的材料与代码仓库进行对照分析。不伪造知识库引用。Wiki 有相关页面时必须用 `[[wikilink]]` 引用。

4. **代码入口定位**
   本地代码：找入口/配置/模型/数据/训练/评估目录，沿调用链分析。远程仓库：先读 README 和目录结构。检查表：train/eval/infer 入口、yaml/json/argparse 配置、model/backbone/head/loss、dataset/dataloader/transforms、metric/eval loop。

5. **论文-代码对齐**

   必须显式回答：程序入口 → 数据流 → forward 主路径 → loss → 推理/评估 → 核心 vs 工程包装 → 实现变体/简化。

   如 Wiki 已有深读结果，优先利用 `## 关键公式`、`## 关键图示`、`## 代码对照线索`。额外回答：哪个公式对应代码 loss/criterion；哪个打分公式对应 score/metric/anomaly map；哪张结构图映射模块边界；若公式与实现不一致，差异在哪里（参数化/归一化/损失聚合/推理后处理）。

6. **缝合建议（按需）**

   仅用户明确要求时。判断任务兼容、模块互补、代码落点、改造成本。输出 2-4 个候选，各附互补点/落点/收益/风险 + MVP。不能明确模块落点时只给方法级建议。

7. **收敛到实现**
   用户目标偏"写代码"时，输出模块拆分、数据流/伪代码、重构建议、最小可复现版本构成。

## 输出结构

```markdown
## 论文层
问题 / 方法 / 结论 / 局限

## 代码层
入口 / 模型 / 训练 / 推理 / loss / dataset

## 论文-代码对照
模块 A -> 文件 / 类 / 函数

## 公式-代码对照
公式 N -> loss.py / trainer / forward

## 图示-代码对照
图 N 模块边界 -> model.py / backbone / head

## 一致与差异
核心是否如实落地；工程包装 vs 仓库特有改动

## 缝合对象（按需）
候选 / 互补点 / 落点 / 收益 / 风险 / MVP

## 重写指南（按需）
模块拆分 / 最小可复现版本
```

## 强制约束

- 禁止跳过 JdocMunch（`index.md` 是 fallback）
- 禁止全库铺读（section 优先，整页限 2-4 页）
- 禁止论文-代码脱节（必须显式映射）
- 禁止忽略 Wiki 中已有 `关键公式 / 关键图示 / 代码对照线索`
- 禁止空泛缝合（无互补点/落点/收益/风险不推荐）
- 禁止盲读仓库（先入口和关键模块）
- 禁止凭记忆猜论文（依赖 Wiki + 论文 + 代码）
- 禁止把框架胶水当论文创新

## 高价值固化与日志

回答有复用价值时询问：> 是否需要保存到 `wiki/syntheses/`？

同意后：
```bash
python ".agents/scripts/write_synthesis.py" \
  --workspace-root "<root>" --slug "<slug>" --summary "<一句话>" \
  --content-file "<tmp>" --tag "综合分析" \
  --source "raw/09-archived/foo.pdf" \
  --related "Entity" --related "Concept" \
  --log-summary "保存 <主题> 代码对照综合页"
```

```bash
python ".agents/scripts/write_log.py" --log-path "<log_path>" --action query --summary "<简述>" --detail "输出=<引用列表>"
```
