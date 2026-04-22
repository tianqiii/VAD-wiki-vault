---
title: "MemoryAugmentedVideoAnomalyDetection"
type: concept
tags: [记忆增强, 视频异常检测, 检索]
sources: ["raw/09-archive/Ahn et al. - 2024 - VideoPatchCore An Effective Method to Memorize Normality for Video Anomaly Detection.pdf", "raw/09-archive/Le和Nguyen - 2026 - Attention-guided bidirectional memory autoencoder for video anomaly detection.pdf", "raw/09-archive/Lyu 等 - 2024 - Moba motion memory-augmented deblurring autoencoder for video anomaly detection.pdf", "raw/09-archive/Li 等 - 2026 - STNMamba mamba-based spatial-temporal normality learning for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## 定义
MemoryAugmentedVideoAnomalyDetection 指通过显式记忆库存储正常模式，并在检测时用检索或相似性偏差识别异常的视频异常检测路线。

## 关键信息
- 这一路线的核心不是生成未来帧，而是记住正常性的覆盖边界。
- 真正难点在于记忆库压缩与正常模式覆盖之间的平衡。
- VideoPatchCore 展示了如何把图像 PatchCore 思想扩展到视频，并利用多粒度记忆库存储正常模式。
- ABMA 与 STNMamba 分别展示了“记忆 + 双向时序/时空一致性”的组合方式；MoBA 则从“去模糊学习正常”视角把记忆库与运动线索绑定。

## 关联连接
- [[VideoPatchCore]] — 代表方法实体。
- [[ABMA]] — 双向记忆 + 注意力路线。
- [[MoBA]] — 运动记忆 + 去模糊路线。
- [[STNMamba]] — 多层级时空融合 + 记忆库路线。
- [[TrainingFreeVideoAnomalyDetection]] — 往往与免训练部署需求相容。
- [[VideoAnomalyDetection]] — 所属任务。
