---
title: "ADPLGVAD"
type: entity
tags: [方法, 视频异常检测, 弱监督]
sources: ["raw/09-archive/Yang et al. - 2026 - Attention-driven pseudo-label self-training for weakly supervised video anomaly detection.pdf"]
last_updated: 2026-04-20
---

## 定义
ADPLGVAD 是一种注意力驱动、同步式伪标签自训练的弱监督视频异常检测方法实体。

## 关键信息
- 其双分支框架把伪标签生成和片段分类训练改成同步协同优化。
- 第一分支利用自注意力、交叉注意力与去噪策略生成更干净的片段级伪标签。
- 第二分支用多尺度时间特征交互模块训练分类器，并持续反向修正伪标签质量。

## 关联连接
- [[PseudoLabelSelfTraining]] — 核心机制概念。
- [[WeaklySupervisedVideoAnomalyDetection]] — 所属任务设定。
- [[摘要-attention-driven-pseudo-label-self-training-for-weakly-supervised-video-anomaly-detection]] — 来源论文。
