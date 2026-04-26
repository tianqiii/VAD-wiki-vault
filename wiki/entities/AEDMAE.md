---
title: "AEDMAE"
type: entity
tags: [方法, 视频异常检测, 自蒸馏, 伪异常生成]
sources: ["raw/09-archive/Ristea et al. - 2024 - Self-distilled masked auto-encoders are efficient video anomaly detectors.pdf"]
last_updated: 2026-04-26
---

## 定义
AEDMAE 是一条面向高吞吐视频异常检测的轻量方法路线，把 frame-level masked autoencoder、自蒸馏和 anomaly map 监督结合起来，在保持效率的同时提高对异常区域的敏感性。

## 关键信息
- 该方法强调用更轻量的 masked autoencoder 维持较高吞吐，而不是单纯追求更大的时空主干。
- 它把 teacher-student 式自蒸馏引入 VAD 训练，用表示差异增强异常敏感性。
- 在本库现有上下文里，它还与伪异常/合成异常监督相连：通过把异常动作片段叠加到正常视频中，为 anomaly map 与 frame-level 分类提供更直接的监督信号。

## 关联连接
- [[摘要-self-distilled-masked-auto-encoders-are-efficient-video-anomaly-detectors]] — 来源论文。
- [[SelfDistillationForVideoAnomalyDetection]] — 关键训练机制。
- [[PseudoAnomalyGeneration]] — 合成异常监督在 VAD 中的相关概念。
- [[VideoAnomalyDetection]] — 上位任务入口。
