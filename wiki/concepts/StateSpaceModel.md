---
title: "StateSpaceModel"
type: concept
tags: [状态空间模型, 时序建模, 高效推理]
sources: ["raw/09-archive/Paparrizos et al. - 2025 - Advances in time-series anomaly detection algorithms, benchmarks, and evaluation measures.pdf", "raw/09-archive/Lyu et al. - 2025 - VADMamba Exploring State Space Models for Fast Video Anomaly Detection.pdf", "raw/09-archive/Li 等 - 2026 - STNMamba mamba-based spatial-temporal normality learning for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## 定义
StateSpaceModel 指一类以状态演化方式建模长序列依赖的时序模型家族，近年常以 Mamba 等实现进入视觉与异常检测任务，用线性复杂度换取更好的长序列效率。

## 关键信息
- 在本库语境下，它是连接时间序列异常检测方法论与高效视频异常检测实现的重要桥梁。
- 相比 Transformer 路线，状态空间模型更强调长序列推理成本与部署效率。
- VADMamba 体现了把该类模型引入 VAD 后，如何结合未来帧预测与光流重建形成混合检测框架。
- STNMamba 展示了另一条路线：以 Mamba/SSM 作为时空建模骨干，并在多层级时空融合中引入记忆库来存储正常原型。

## 关联连接
- [[TimeSeriesAnomalyDetection]] — 上位异常检测方法论。
- [[VADMamba]] — 当前库中的代表方法实体。
- [[STNMamba]] — 将 Mamba/SSM 用于时空一致性学习的 VAD 方法实体。
- [[VideoAnomalyDetection]] — 该概念在视频异常检测中的应用场景。
- [[摘要-vadmamba-exploring-state-space-models-for-fast-video-anomaly-detection]] — 具体论文来源。
