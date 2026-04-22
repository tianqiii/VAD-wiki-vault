---
title: "VideoPatchCore"
type: entity
tags: [方法, 视频异常检测, 记忆增强]
sources: ["raw/09-archive/Ahn et al. - 2024 - VideoPatchCore An Effective Method to Memorize Normality for Video Anomaly Detection.pdf"]
last_updated: 2026-04-20
---

## 定义
VideoPatchCore 是把 PatchCore 异常检测思想扩展到视频域的训练自由方法实体。

## 关键信息
- 使用预训练 CLIP 编码器抽取局部流与全局流特征。
- 通过空间、时间与高层语义三类记忆库存储正常模式。
- 利用 coreset subsampling 压缩记忆规模，在覆盖正常模式与部署成本之间折中。

## 关联连接
- [[MemoryAugmentedVideoAnomalyDetection]] — 所属方法路线。
- [[TrainingFreeVideoAnomalyDetection]] — 满足免训练部署特征。
- [[摘要-videopatchcore-an-effective-method-to-memorize-normality-for-video-anomaly-detection]] — 来源论文。
