---
title: "SelfDistillationForVideoAnomalyDetection"
type: concept
tags: [自蒸馏, teacher-student, 视频异常检测]
sources: ["raw/09-archive/Ristea et al. - 2024 - Self-distilled masked auto-encoders are efficient video anomaly detectors.pdf"]
last_updated: 2026-04-26
---

## 定义
SelfDistillationForVideoAnomalyDetection 指在视频异常检测中使用 teacher-student 式自蒸馏，让模型通过内部表示、重建结果或分数差异学习更敏感的异常判别边界。

## 关键信息
- 与只依赖单一路径重建误差相比，自蒸馏提供了额外的“模型内对照信号”，有助于放大正常与异常之间的细微差异。
- 这类机制通常与轻量主干、重建式目标或 anomaly map 监督结合，用较低额外成本换取更稳的异常定位能力。
- 在本库当前网络里，它主要用来解释 AEDMAE 为什么能在高吞吐设置下仍维持较强异常敏感性。

## 关联连接
- [[AEDMAE]] — 该概念在当前知识库中的代表方法实体。
- [[VideoAnomalyDetection]] — 该机制的应用任务。
- [[摘要-self-distilled-masked-auto-encoders-are-efficient-video-anomaly-detectors]] — 来源论文。
