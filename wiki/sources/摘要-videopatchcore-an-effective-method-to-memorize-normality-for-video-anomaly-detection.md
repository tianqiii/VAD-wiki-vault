---
title: "摘要-videopatchcore-an-effective-method-to-memorize-normality-for-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Ahn et al. - 2024 - VideoPatchCore An Effective Method to Memorize Normality for Video Anomaly Detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Sunghyun Ahn，Youngwan Jo，Kijung Lee，Sanghyun Park
- **年份**: 2025
- **期刊/会议**: Lecture Notes in Computer Science（图书章节/会议论文集条目）
- **DOI / arXiv**: DOI: 10.1007/978-981-96-0908-6_18；arXiv: 未在公开信息中找到
- **备注**: 文件名中的年份为 2024；Crossref/DOI 记录的出版年份为 2025。

## 核心摘要
这篇论文提出 VideoPatchCore，把图像异常检测中的 PatchCore 扩展到了视频域。方法不再训练重建器，而是直接利用预训练 CLIP 编码器提取局部流与全局流特征，并通过空间、时间和高层语义三类记忆库来存储正常模式。作者的关键观点是：传统记忆增强 VAD 难点不只是“是否用记忆”，而是“如何让记忆规模足够小且仍覆盖正常模式”，因此引入 coreset subsampling 压缩记忆。整体结果表明，该方法在保持训练自由和实现简单的同时，仍能在多个基准上取得有竞争力的性能。

## 论文问题
- 如何在不增加额外训练成本的前提下，把记忆增强思想有效迁移到视频异常检测。
- 如何避免记忆库规模过大导致部署成本上升，同时又尽量覆盖复杂正常模式。

## 方法要点
- 使用预训练 CLIP 编码器抽取局部流与全局流特征，避免再训练专门的生成式模型。
- 把正常模式拆成空间记忆、时间记忆和高层语义记忆三类记忆库，以覆盖不同粒度的异常线索。
- 用 coreset subsampling 压缩记忆规模，强调“小记忆库也要保住正常模式覆盖能力”。

## 实验与局限
- 文中结论是：该方法在多个 VAD 基准上兼顾了训练自由、实现简单与有竞争力的性能。
- 这一路线更依赖预训练特征质量与记忆设计，若正常模式跨度过大，记忆覆盖与压缩之间仍存在权衡。

## 关联连接
- [[VideoPatchCore]] — 论文提出的核心方法实体。
- [[MemoryAugmentedVideoAnomalyDetection]] — 该工作属于记忆增强路线。
- [[VideoAnomalyDetection]] — 其问题背景是通用视频异常检测。
