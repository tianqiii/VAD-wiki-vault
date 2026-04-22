---
title: "VideoAnomalyDetection"
type: concept
tags: [视频异常检测, 监控, 视觉]
sources: ["raw/09-archive/Rai et al. - 2024 - Video Anomaly Detection via Spatio-Temporal Pseudo-Anomaly Generation  A Unified Approach.pdf", "raw/09-archive/Ahn et al. - 2024 - VideoPatchCore An Effective Method to Memorize Normality for Video Anomaly Detection.pdf", "raw/09-archive/Kobayashi et al. - 2025 - Unsupervised video anomaly detection using video vision transformer and adversarial training.pdf", "raw/09-archive/Lyu et al. - 2025 - VADMamba Exploring State Space Models for Fast Video Anomaly Detection.pdf", "raw/09-archive/Lyu et al. - 2026 - Bidirectional skip-frame prediction for video anomaly detection with intra-domain disparity-driven a.pdf", "raw/09-archive/Cao et al. - 2024 - Railway Intrusion Detection Based on Machine Vision A Survey, Challenges, and Perspectives.pdf"]
last_updated: 2026-04-20
---

## 定义
VideoAnomalyDetection 是在视频序列中识别异常行为、事件或入侵目标的任务，核心难点在于异常开放集、正常模式跨度大、标注稀缺以及长时序建模成本高。

## 关键信息
- 当前知识网络覆盖无监督、弱监督、训练自由、多模态与高效时序建模等多条路线。
- 预测式、重建式、记忆增强式、伪异常生成式与原型/伪标签学习式方法是当前主要分支。
- 该概念页应作为本知识库围绕 VAD 相关论文的总入口页。

## 关联连接
- [[TimeSeriesAnomalyDetection]] — 上位方法论框架。
- [[WeaklySupervisedVideoAnomalyDetection]] — 视频级弱标注分支。
- [[TrainingFreeVideoAnomalyDetection]] — 免训练推理分支。
- [[MultimodalVideoAnomalyDetection]] — 音视频与大模型增强分支。
- [[VideoPatchCore]] — 记忆增强路线代表方法。
- [[VADMamba]] — 状态空间模型路线代表方法。
- [[EventVAD]] — 训练自由事件级推理方法。
- [[摘要-video-anomaly-detection-via-spatio-temporal-pseudo-anomaly-generation-a-unified-approach]] — 统一伪异常生成路线。
