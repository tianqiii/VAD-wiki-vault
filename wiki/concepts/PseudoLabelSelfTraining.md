---
title: "PseudoLabelSelfTraining"
type: concept
tags: [伪标签, 自训练, 弱监督]
sources: ["raw/09-archive/Zhu et al. - 2025 - ProDisc-VAD An Efficient System for Weakly-Supervised Anomaly Detection in Video Surveillance Appli.pdf", "raw/09-archive/Yang et al. - 2026 - Attention-driven pseudo-label self-training for weakly supervised video anomaly detection.pdf"]
last_updated: 2026-04-20
---

## 定义
PseudoLabelSelfTraining 指模型先从粗监督或当前预测中生成片段级伪标签，再利用这些伪标签迭代训练分类器或定位器，以逐步逼近更细粒度监督。

## 关键信息
- 在弱监督 VAD 中，关键不只是“生成伪标签”，而是控制噪声放大与错误累积。
- ProDiscVAD 偏向用极值样本提纯监督信号；ADPLGVAD 则把伪标签生成与分类训练改成同步协同优化。
- 后续若继续吸收相关论文，该页适合作为弱监督路线的共性机制节点。

## 关联连接
- [[WeaklySupervisedVideoAnomalyDetection]] — 主要应用场景。
- [[ProDiscVAD]] — 极值伪实例提纯路线。
- [[ADPLGVAD]] — 注意力驱动同步自训练路线。
- [[摘要-prodisc-vad-an-efficient-system-for-weakly-supervised-anomaly-detection-in-video-surveillance-applications]] — 代表来源之一。
