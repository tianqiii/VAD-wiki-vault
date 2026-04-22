---
title: "ABMA"
type: entity
tags: [方法, 视频异常检测, 记忆增强, 双向]
sources: ["raw/09-archive/Le和Nguyen - 2026 - Attention-guided bidirectional memory autoencoder for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## 定义
ABMA（Attention-guided Bidirectional Memory Autoencoder）是一种将双向记忆模块与空间注意力嵌入自编码器的无监督/弱监督混合训练式视频异常检测方法，通过“过去/未来双向上下文”放大异常造成的时序不一致。

## 关键信息
- 双向记忆（past/future）只用正常特征更新，避免记忆库被异常污染。
- 采用 skip-frame 合成伪异常，并在目标函数中显式抑制模型对伪异常的重建/预测能力。
- 异常分数融合图像域误差与潜空间到最近记忆项距离，并取双向最大值增强敏感性。

## 关联连接
- [[摘要-attention-guided-bidirectional-memory-autoencoder-for-video-anomaly-detection]] — 来源。
- [[MemoryAugmentedVideoAnomalyDetection]] — 所属路线。
- [[VideoAnomalyDetection]] — 上位任务。
- [[bisp-abma-stnmamba-comparison]] — 与 BiSP、STNMamba 的方法比较。
