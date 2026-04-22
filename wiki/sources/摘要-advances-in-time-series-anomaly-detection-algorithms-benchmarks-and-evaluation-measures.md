---
title: "摘要-advances-in-time-series-anomaly-detection-algorithms-benchmarks-and-evaluation-measures"
type: source
tags: [来源, 论文, 时间序列]
sources: ["raw/09-archive/Paparrizos et al. - 2025 - Advances in time-series anomaly detection algorithms, benchmarks, and evaluation measures.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: John Paparrizos，Paul Boniol，Qinghua Liu，Themis Palpanas
- **年份**: 2025
- **期刊/会议**: ACM SIGKDD 2025（Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining）
- **DOI / arXiv**: DOI: 10.1145/3711896.3736565；arXiv: 未在公开信息中找到

## 核心摘要
这篇 KDD 2025 教程综述从过程视角系统梳理了时间序列异常检测方法，把主流方法归纳为距离型、密度型和预测型三大类，并进一步细分为邻近、聚类、图、树、编码、预测与重建等路线。文章同时强调，评价一个异常检测器不能只看单一 AUC，因为点异常与区间异常、监督与无监督、数据域差异都会显著改变结果排序。作者还总结了近年的关键结论：不存在通用最优检测器，统计方法依旧稳健，而更复杂的神经网络并不总能稳定胜出。对本地知识库最有价值的是，它提供了理解视频异常检测时的更上层框架：视频方法可以看作时序异常检测在视觉数据上的一种特化。

## 论文问题
- 如何从更上层的方法论视角统一理解时间序列异常检测的主要算法谱系与评价问题。
- 为什么异常检测方法的优劣不能被单一指标或单一数据域简单概括。

## 方法要点
- 把主流时间序列异常检测方法归纳为距离型、密度型和预测型三大类。
- 再进一步细分为邻近、聚类、图、树、编码、预测与重建等路线，用于建立方法论地图。
- 强调评价框架本身就是研究问题，不能只依赖单一 AUC 排序。

## 实验与局限
- 该文作为教程综述，价值不在提出新模型，而在于总结：不存在通用最优检测器，复杂神经网络也不总能稳定胜出。
- 它提供的是上位框架而非具体实现方案，因此更适合作为方法论参照，而不是直接迁移成某个具体检测器。

## 关联连接
- [[TimeSeriesAnomalyDetection]] — 该综述直接定义与组织该概念。
- [[VideoAnomalyDetection]] — 视频异常检测可借用其方法论与评价观点。
- [[StateSpaceModel]] — 长序列建模是文中讨论的重要趋势。
