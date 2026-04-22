---
title: "MoBA"
type: entity
tags: [方法, 视频异常检测, 记忆增强, 去模糊]
sources: ["raw/09-archive/Lyu 等 - 2024 - Moba motion memory-augmented deblurring autoencoder for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## 定义
MoBA（Motion memory-augmented deBlurring Autoencoder）是一种通过“去模糊学习正常模式 + 运动记忆检索”来提升异常可分性与跨域稳健性的无监督视频异常检测方法。

## 关键信息
- 训练时对外观图像施加高斯模糊作为伪异常扰动，把检测问题转化为“恢复正常清晰结构”的学习。
- 运动记忆模块在训练时写入正常运动原型，测试时用外观查询记忆项以检索更背景无关的正常运动。
- 方法强调 zero-shot 跨数据集评估能力。

## 关联连接
- [[摘要-moba-motion-memory-augmented-deblurring-autoencoder-for-video-anomaly-detection]] — 来源。
- [[MemoryAugmentedVideoAnomalyDetection]] — 所属路线。
- [[PseudoAnomalyGeneration]] — 伪异常构造视角。
- [[VideoAnomalyDetection]] — 上位任务。
