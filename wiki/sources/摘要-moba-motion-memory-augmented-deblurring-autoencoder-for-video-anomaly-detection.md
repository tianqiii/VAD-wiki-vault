---
title: "摘要-moba-motion-memory-augmented-deblurring-autoencoder-for-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测, 记忆增强, 伪异常]
sources: ["raw/09-archive/Lyu 等 - 2024 - Moba motion memory-augmented deblurring autoencoder for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Jiahao Lyu；Minghua Zhao；Jing Hu；Xuewen Huang；Shuangli Du；Cheng Shi；Zhiyong Lv
- **年份**: 2026
- **期刊/会议**: Knowledge-Based Systems（Vol. 335, 115218）
- **DOI / arXiv**: DOI: 10.1016/j.knosys.2025.115218
- **链接**: https://doi.org/10.1016/j.knosys.2025.115218

## 核心摘要
这篇论文提出 MoBA（Motion memory-augmented deBlurring Autoencoder），把无监督 VAD 重新表述为“**去模糊（deblurring）学习正常模式**”的问题：训练时对外观图像加入高斯模糊作为伪异常扰动，并用注意力机制让模型更关注可恢复的正常结构；同时引入**运动记忆模块**，在训练阶段用运动特征写入记忆项，在测试阶段用外观分支去查询记忆项以“检索出更背景无关的正常运动”，从而拉大正常/异常运动差距。论文强调该设计不仅提高异常可分性，也在跨数据集（zero-shot）评估中表现更稳健。

## 论文问题
- 自编码器容易“过度泛化”重建异常：如何限制其对异常的重建能力？
- 跨场景/跨数据集时背景差异显著：如何让记忆模块更关注与异常相关的运动线索而非背景？

## 方法要点
- **Gaussian blur 伪异常**：训练时对外观输入进行模糊扰动，把 VAD 转换为“学习去模糊的正常特征”。
- **MRCA（多尺度残差通道注意力）**：用于 skip connection，尽量避免把异常特征“直通”到解码器。
- **Motion Memory**：写入阶段记录正常运动分布；读出阶段用外观查询检索出更“正常”的运动表征。
- **跨域评估**：强调 zero-shot 跨数据集检测能力。

## 实验与局限
- 论文在 Ped2、Avenue、ShanghaiTech、UBnormal 上报告了 AUC 结果，并给出跨数据集验证。
- 方法依赖“运动特征质量”（论文比较了前景差分/光流两种训练侧输入），复杂背景下前景差分可能引入噪声。

## 关联连接
- [[MoBA]] — 论文提出的方法实体。
- [[MemoryAugmentedVideoAnomalyDetection]] — 显式记忆模块路线。
- [[PseudoAnomalyGeneration]] — 以模糊扰动作为伪异常的一类实例。
- [[VideoAnomalyDetection]] — 上位任务。
