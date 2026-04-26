---
title: "PseudoAnomalyGeneration"
type: concept
tags: [伪异常生成, 开放集, 视频异常检测]
sources: ["raw/09-archive/Rai et al. - 2024 - Video Anomaly Detection via Spatio-Temporal Pseudo-Anomaly Generation  A Unified Approach.pdf", "raw/09-archive/Lyu 等 - 2024 - Moba motion memory-augmented deblurring autoencoder for video anomaly detection.pdf", "raw/09-archive/Le和Nguyen - 2026 - Attention-guided bidirectional memory autoencoder for video anomaly detection.pdf", "raw/09-archive/Ristea et al. - 2024 - Self-distilled masked auto-encoders are efficient video anomaly detectors.pdf"]
last_updated: 2026-04-24
---

## 定义
PseudoAnomalyGeneration 指从正常样本出发合成“接近异常但不完全等于真实异常”的伪异常样本，用于收紧正常边界并提升开放集异常检测的泛化能力。

## 关键信息
- 与固定补丁或固定速度扰动不同，较好的伪异常生成应尽量覆盖空间和时间两个维度的不规则性。
- 该概念的收益取决于生成样本是否足够贴近真实开放集异常边界。
- 在本库中，它是连接扩散模型修补、光流 mixup 扰动与统一异常评分的重要概念节点。
- MoBA 与 ABMA 展示了两类更“训练导向”的伪异常：前者用高斯模糊扰动把任务转化为去模糊学习正常，后者用 skip-frame 合成伪异常并在损失中显式抑制对伪异常的重建。
- AEDMAE 则展示了另一种更直接的开放集监督方式：把 UBnormal 异常动作片段叠加到正常视频中，并联合学习 anomaly map 与 frame-level 分类信号。

## 关联连接
- [[PseudoAnomalyGenerationVAD]] — 代表方法实体。
- [[MoBA]] — 高斯模糊伪异常 + 运动记忆。
- [[ABMA]] — skip-frame 伪异常 + 双向记忆。
- [[AEDMAE]] — 合成异常叠加 + anomaly map 监督。
- [[VideoAnomalyDetection]] — 主要应用任务。
- [[摘要-video-anomaly-detection-via-spatio-temporal-pseudo-anomaly-generation-a-unified-approach]] — 来源论文。
