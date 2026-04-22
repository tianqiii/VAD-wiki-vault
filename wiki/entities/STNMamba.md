---
title: "STNMamba"
type: entity
tags: [方法, 视频异常检测, 状态空间模型, 记忆增强]
sources: ["raw/09-archive/Li 等 - 2026 - STNMamba mamba-based spatial-temporal normality learning for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## 定义
STNMamba 是一种把 Mamba/状态空间模型用于无监督视频异常检测的双编码器方法，通过多层级的时空交互与记忆库存储正常原型来学习空间-时间正常性。

## 关键信息
- 空间编码器用多尺度 MS-VSSB 提取不同尺度的外观特征；时间编码器用 CA-VSSB 对相邻帧 RGB 差分建模运动。
- STIM 在多层级融合时空特征并配套记忆库，存储正常时空原型，推理时在图像域与特征域联合打分。
- 论文强调在性能与效率（FLOPs/参数量/FPS）之间取得更好的折中。

## 关联连接
- [[摘要-stnmamba-mamba-based-spatial-temporal-normality-learning-for-video-anomaly-detection]] — 来源。
- [[StateSpaceModel]] — 上位概念。
- [[SpatialTemporalConsistency]] — 关键建模目标。
- [[VideoAnomalyDetection]] — 上位任务。
- [[bisp-abma-stnmamba-comparison]] — 与 BiSP、ABMA 的方法比较。
