---
title: "BidirectionalSkipFramePrediction"
type: concept
tags: [预测式检测, 跳帧预测, 视频异常检测]
sources: ["raw/09-archive/Lyu et al. - 2026 - Bidirectional skip-frame prediction for video anomaly detection with intra-domain disparity-driven a.pdf"]
last_updated: 2026-04-20
---

## 定义
BidirectionalSkipFramePrediction 是一种通过前后双向上下文预测目标帧、并利用跳帧设置主动放大异常预测误差的预测式异常检测思路。

## 关键信息
- 它的设计目标不是单纯提升预测精度，而是刻意拉开正常样本与异常样本的域内差异。
- 跳帧策略决定模型更关注动作节奏变化而非相邻帧平滑过渡。
- 在本库里，它是预测式无监督 VAD 的一个清晰机制节点。

## 关联连接
- [[BiSP]] — 当前代表方法实体。
- [[VideoAnomalyDetection]] — 所属任务。
- [[摘要-bidirectional-skip-frame-prediction-for-video-anomaly-detection-with-intra-domain-disparity-driven-attention]] — 方法来源。
