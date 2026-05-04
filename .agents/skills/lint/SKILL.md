---
name: lint
description: 检查 Obsidian LLM Wiki 健康状态。凡用户输入 /lint、/scan、/health，或要求检查知识库状态、健康度、死链、孤儿页面、完整注册表、frontmatter、raw 路径残留、知识冲突时必须使用。默认只读报告；只有用户明确要求修复时才修改 wiki。
user-invocable: true
---

# lint 技能

## 目标

对 `wiki/` 做只读健康检查，找出结构性问题并给出可执行修复建议。默认不改文件；报告后等待用户确认再修复。

## 流程

1. **解析路径**
   ```bash
   python ".agents/scripts/router.py" lint
   ```
   读取 `wiki_dir/raw_dir/log_path`。若有 `missing_paths`，停止并报告。

2. **运行确定性底座**
   ```bash
   python ".agents/scripts/lint.py" --wiki-dir "<wiki_dir>" --raw-dir "<raw_dir>" --json
   ```
   以脚本 JSON 为事实来源；不要在脚本已有结果之外重复铺读全库。脚本退出码 `1` 表示存在 P0，不是工具失败。

   需要单独查看 tag 池或预览 tag 浏览层时：
   ```bash
   python ".agents/scripts/wiki_tags.py" --wiki-dir "<wiki_dir>" --index-path "<index_path>" --json
   python ".agents/scripts/wiki_tags.py" --wiki-dir "<wiki_dir>" --index-path "<index_path>" --print-tag-index
   ```

3. **必要时少量复核**
   仅在脚本输出不清楚、用户要求解释、或准备修复时读取相关页面。`wiki/index.md` 只看 `## 完整注册表`；导航层（快速入口/按主题浏览）不参与注册完整性判断。

   若环境中可用 `rg`， 则可将其作为维护排查辅助，不替代 JdocMunch/query 主路径。适用场景：查旧路径、旧 tag、页面名、术语或 workflow 过期文案残留：
   ```bash
   rg -n "<旧tag|旧路径|页面名|术语>" "wiki" ".agents/skills" ".agents/scripts"
   ```

4. **输出报告**
   按 P0/P1 分组，先列最需要处理的问题，再给下一步建议。

## 检查项

`lint.py` 当前覆盖：

- Frontmatter：缺失 YAML、缺少 `title/type/tags/sources/last_updated`、非法 `type`。
- Tags：空 tags、非 kebab-case tag、疑似拼写错误 tag、近似重复 tag。
- Tag index：`wiki/index.md` 顶部 `tags: [...]` 与实际页面 frontmatter tag 池不一致；详细 tag 反查由 `wiki_tags.py --print-tag-index` 按需输出，不写入人读目录。
- Summary：tag 反查使用完整注册表中的 `[[页面]] — 一句话描述`；缺失或空摘要会报告。
- 关联区块：缺少 `## 关联连接`。
- 死链：`[[页面]]` 指向不存在页面；忽略 raw 路径、资产链接、`index/log`。
- 孤儿页：没有任何其他 wiki 页面链接到该页。
- 完整注册表：文件存在但未登记，或登记了不存在页面；只以 `## 完整注册表` 为准。
- 顶部规模统计：Sources/Entities/Concepts/Syntheses 数量与实际目录不一致。
- 归档路径残留：仍引用 `raw/02-papers/`，应改为 `raw/09-archived/`。
- 知识冲突：存在 `## 知识冲突` 区块，需要人工审阅。

## 严重级别

- **P0**：破坏可导航性或注册一致性；包括 frontmatter 缺失、死链、完整注册表缺失/悬挂等。修复优先级最高。
- **P1**：影响质量但不一定阻断使用；包括孤儿页、缺少关联连接、规模统计错误、旧 raw 路径、知识冲突、tag 格式/拼写/tag index 不一致等。
- **P2**：仅在后续脚本支持时使用；当前通常为空。

## 报告格式

```markdown
## 知识库健康检查 — YYYY-MM-DD

### 结论
- 共检查 N 个内容页；发现 X 个 P0、Y 个 P1。

### P0：需要优先修复
- `[type] path/to/page.md`：问题说明；建议修复方式。

### P1：建议改进
- `[type] path/to/page.md`：问题说明；建议修复方式。

### 下一步
- 建议先处理 ...
- 如需我自动修复，请确认修复范围。
```

如果没有问题，明确写“未发现结构性问题”。

## 修复规则

- 默认只读；用户明确说“修复/同步/补全”后才修改。
- 只修 lint 指向的问题，不顺手重写无关内容。
- 常见自动修复：补 `index.md` 完整注册表、修旧 `raw/02-papers/` sources 路径、补缺失 `## 关联连接` 的最小回链、修规模统计。
- tag 修复默认只报告，不静默删除或重命名已有 tag。只有用户明确要求同步 tag 池时，才运行 `wiki_tags.py --update-index` 写入 `index.md` 顶部 `tags: [...]`；详细 tag 反查用 `--print-tag-index` 临时查看，不写入 `index.md`。
- 知识冲突不自动合并；需要用户判断。
- 修复后重新运行 `lint.py --json` 验证。

## 日志

检查完成后追加 `wiki/log.md`：

```bash
python ".agents/scripts/write_log.py" --log-path "<log_path>" --action lint --summary "<检查简述>" --detail "P0=<数量>" --detail "P1=<数量>"
```

如果执行了修复，再追加 `sync`：

```bash
python ".agents/scripts/write_log.py" --log-path "<log_path>" --action sync --summary "修复了 N 个问题" --detail "P0修复=<数量>" --detail "P1修复=<数量>"
```

## 快速自检

- [ ] 已先跑 `router.py lint`，路径有效。
- [ ] 已跑 `lint.py --json`，报告基于脚本事实。
- [ ] 已确认 tag 池可扫描；空 tag、非法 tag、疑似拼写、tag index 不一致和缺 summary 均由脚本报告。
- [ ] 未在用户确认前修改文件。
- [ ] 报告区分 P0/P1，并给出具体路径与修复建议。
- [ ] 若修复，已复跑 lint 并写入 `sync` 日志。
