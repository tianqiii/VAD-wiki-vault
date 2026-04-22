---
title: "BiSP"
type: entity
tags: [方法, 视频异常检测, 预测式]
sources: ["raw/09-archive/Lyu et al. - 2026 - Bidirectional skip-frame prediction for video anomaly detection with intra-domain disparity-driven a.pdf", "raw/09-archive/Le和Nguyen - 2026 - Attention-guided bidirectional memory autoencoder for video anomaly detection.pdf", "raw/09-archive/Li 等 - 2026 - STNMamba mamba-based spatial-temporal normality learning for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## 定义
BiSP 是一类通过双向跳帧预测放大异常误差的视频异常检测方法实体。

## 关键信息
- 训练阶段分别执行前向与后向跳帧预测，测试阶段用双向上下文共同预测中间帧。
- 通过方差通道注意力与上下文空间注意力强化动作模式与对象尺度建模。
- 核心目标是拉大正常与异常的预测误差差距，而不是仅追求更平滑的帧预测。
- 作为“预测式双向建模”代表，BiSP 常被后续工作在相关工作中引用，用来对比更复杂的记忆增强与时空融合方案（例如 ABMA、STNMamba；用户指出二者引用 BiSP）。

## 关联连接
- [[BidirectionalSkipFramePrediction]] — 其核心机制概念。
- [[VideoAnomalyDetection]] — 所属任务。
- [[摘要-bidirectional-skip-frame-prediction-for-video-anomaly-detection-with-intra-domain-disparity-driven-attention]] — 来源论文。
- [[bisp-fusion-strategies]] — BiSP 融合优先级综合总结。
- [[摘要-attention-guided-bidirectional-memory-autoencoder-for-video-anomaly-detection]] — 相关工作引用 BiSP 的代表之一。
- [[摘要-stnmamba-mamba-based-spatial-temporal-normality-learning-for-video-anomaly-detection]] — 用户指出其相关工作引用 BiSP。
- [[bisp-abma-stnmamba-comparison]] — BiSP 与 ABMA、STNMamba 的方法比较。
