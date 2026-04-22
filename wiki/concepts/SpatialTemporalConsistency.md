---
title: "SpatialTemporalConsistency"
type: concept
tags: [时空一致性, 视频理解, 视频异常检测]
sources: ["raw/09-archive/Li 等 - 2026 - STNMamba mamba-based spatial-temporal normality learning for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## 定义
SpatialTemporalConsistency 指视频中**空间外观模式**与**时间运动模式**在多尺度、多层级上的一致性约束：正常事件通常在外观与运动上呈现稳定的耦合结构，而异常会破坏这种耦合与连续性。

## 关键信息
- 单纯的重建/预测误差可能被背景冗余、模型过度泛化或局部噪声稀释；显式建模“时空一致性”可以更直接地把注意力放在“正常耦合模式被破坏”上。
- 多层级一致性常见于视频理解：浅层反映局部纹理/短期运动，深层反映语义与长期行为；因此仅在瓶颈处融合容易丢失关键信息。

## 关联连接
- [[STNMamba]] — 在多层级上显式建模时空一致性的代表方法。
- [[StateSpaceModel]] — 高效长序列建模常被用于承载时序一致性学习。
- [[VideoAnomalyDetection]] — 该概念在 VAD 中的落地场景。
