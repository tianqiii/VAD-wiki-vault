---
title: "InformationBottleneck"
type: concept
tags: [信息瓶颈, 轻量化, 表征学习]
sources: ["raw/09-archive/Zhu et al. - 2025 - DS-IB Net Ultra-Lightweight Weakly-Supervised Video Anomaly Detection through Synergistic Dual Stre.pdf"]
last_updated: 2026-04-20
---

## 定义
InformationBottleneck 是一种通过压缩输入中的冗余信息、保留与目标预测最相关信息来提升表示效率与泛化性的建模思想。

## 关键信息
- 在 DSIB-Net 中，它被用于压缩正常动态中的冗余信息，从而降低计算开销。
- 这类设计通常需要额外机制补偿被压缩掉但对异常有用的瞬时细节。
- 在本库里，它更像“效率优化路线”的共性思想节点，而不是只属于单一模型实现。

## 关联连接
- [[DSIBNet]] — 该概念在当前库中的方法代表。
- [[WeaklySupervisedVideoAnomalyDetection]] — 主要应用设定。
- [[摘要-ds-ib-net-ultra-lightweight-weakly-supervised-video-anomaly-detection-through-synergistic-dual-streams-and-information-bottleneck]] — 来源论文。
