---
title: "ProDiscVAD"
type: entity
tags: [方法, 视频异常检测, 弱监督]
sources: ["raw/09-archive/Zhu et al. - 2025 - ProDisc-VAD An Efficient System for Weakly-Supervised Anomaly Detection in Video Surveillance Appli.pdf"]
last_updated: 2026-04-20
---

## 定义
ProDiscVAD 是一种通过正常原型交互与极值伪实例对比学习提纯监督信号的弱监督 VAD 方法实体。

## 关键信息
- 先用 Prototype Interaction Layer 建立受控正常性原型基线。
- 再用 PIDE 只挑最高分和最低分实例施加对比约束，减少中间噪声片段的干扰。
- 该方法强调“提纯监督信号”比继续堆更重主干更关键。

## 关联连接
- [[WeaklySupervisedVideoAnomalyDetection]] — 所属任务设定。
- [[PseudoLabelSelfTraining]] — 与伪标签提纯密切相关。
- [[摘要-prodisc-vad-an-efficient-system-for-weakly-supervised-anomaly-detection-in-video-surveillance-applications]] — 来源论文。
