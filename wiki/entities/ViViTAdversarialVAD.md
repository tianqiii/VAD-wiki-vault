---
title: "ViViTAdversarialVAD"
type: entity
tags: [方法, 视频异常检测, 对抗训练]
sources: ["raw/09-archive/Kobayashi et al. - 2025 - Unsupervised video anomaly detection using video vision transformer and adversarial training.pdf"]
last_updated: 2026-04-20
---

## 定义
ViViTAdversarialVAD 是一种结合 ViViT、未来帧预测、光流幅值预测与对抗训练的无监督视频异常检测方法实体。

## 关键信息
- 生成器同时预测未来帧和光流幅值，以增强时序与运动建模。
- U-Net 判别器的中层特征被用于再加权差分图，压制静态区域噪声。
- 它代表了“预测式建模 + 对抗式显著性细化”的复杂无监督路线。

## 关联连接
- [[VideoAnomalyDetection]] — 所属任务。
- [[StateSpaceModel]] — 与高效时序路线形成对照。
- [[摘要-unsupervised-video-anomaly-detection-using-video-vision-transformer-and-adversarial-training]] — 来源论文。
