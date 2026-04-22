---
title: "bisp-fusion-strategies"
type: synthesis
tags: [综合分析, 视频异常检测, BiSP, 方法融合]
sources: ["raw/09-archive/Lyu et al. - 2026 - Bidirectional skip-frame prediction for video anomaly detection with intra-domain disparity-driven a.pdf", "raw/09-archive/Lyu et al. - 2025 - VADMamba Exploring State Space Models for Fast Video Anomaly Detection.pdf", "raw/09-archive/Kobayashi et al. - 2025 - Unsupervised video anomaly detection using video vision transformer and adversarial training.pdf", "raw/09-archive/Rai et al. - 2024 - Video Anomaly Detection via Spatio-Temporal Pseudo-Anomaly Generation  A Unified Approach.pdf", "raw/09-archive/Ahn et al. - 2024 - VideoPatchCore An Effective Method to Memorize Normality for Video Anomaly Detection.pdf"]
last_updated: 2026-04-20
---

## 核心结论
围绕 [[BiSP]] 的方法融合，最值得优先尝试的不是“再找一个同样做预测的方法简单堆叠”，而是针对它已经暴露出来的短板做定向补强。基于本地知识库，最优先的融合对象依次是：[[VADMamba]]、[[ViViTAdversarialVAD]]、[[PseudoAnomalyGenerationVAD]]、[[VideoPatchCore]]。

## 分析框架
[[BiSP]] 的核心强项是用双向跳帧预测主动放大正常与异常之间的预测误差，并用方差通道注意力和上下文空间注意力分别建模动作模式与对象尺度。它的潜在短板也很明确：效果依赖跳帧策略与视频帧率、动作节奏的匹配程度。基于这一点，融合判断的关键不在“谁和 BiSP 最像”，而在“谁最能补它现在最缺的能力”。

## 优先级 1：与 [[VADMamba]] 融合
这是最值得优先尝试的路线。[[VADMamba]] 的价值在于把 [[StateSpaceModel]] 引入视频异常检测，用更强的长序列建模与更高的推理效率支撑未来帧预测和光流重建双任务。若把 [[BiSP]] 的“差异放大式跳帧预测目标”装进这类长序列骨干中，就有机会同时补上 BiSP 对动作节奏敏感的问题和部署效率问题。

## 优先级 2：与 [[ViViTAdversarialVAD]] 融合
这条路线最适合补“误差图提纯”。[[BiSP]] 擅长把异常误差做大，但未必总能保证异常区域足够显著；[[ViViTAdversarialVAD]] 则通过未来帧预测、光流幅值预测和对抗式显著性细化来压制动态背景噪声。两者结合时，一个负责制造更强的异常差距，一个负责把真正异常区域从复杂背景中提纯出来。

## 优先级 3：与 [[PseudoAnomalyGenerationVAD]] 融合
这条路线最适合补“开放集边界”。[[PseudoAnomalyGenerationVAD]] 通过 [[PseudoAnomalyGeneration]] 从正常样本构造更贴近真实异常边界的时空伪异常，再统一聚合多类异常信号。若与 [[BiSP]] 结合，可以把“训练时主动制造更难的异常邻域”和“检测时放大预测误差”结合起来，从而减轻 BiSP 对具体跳帧设计的依赖。

## 优先级 4：与 [[VideoPatchCore]] 融合
这条路线最适合补“正常性参照”。[[VideoPatchCore]] 属于 [[MemoryAugmentedVideoAnomalyDetection]] 路线，用多粒度记忆库存储正常模式，强调正常边界覆盖而不是预测未来帧。若与 [[BiSP]] 融合，可以同时利用预测误差和记忆偏离度两类信号，减少单纯依赖预测失败所带来的场景敏感性。

## 简化建议
- 若目标是补 **长时依赖与效率**，优先选 [[VADMamba]]。
- 若目标是补 **显著性细化与动态背景鲁棒性**，优先选 [[ViViTAdversarialVAD]]。
- 若目标是补 **开放集泛化与异常边界建模**，优先选 [[PseudoAnomalyGenerationVAD]]。
- 若目标是补 **正常性建模与稳健性**，优先选 [[VideoPatchCore]]。

## 关联连接
- [[BiSP]] — 本页讨论的核心方法实体。
- [[BidirectionalSkipFramePrediction]] — BiSP 的机制概念。
- [[VADMamba]] — 最优先的长序列建模融合对象。
- [[ViViTAdversarialVAD]] — 预测式显著性细化融合对象。
- [[PseudoAnomalyGenerationVAD]] — 开放集边界增强融合对象。
- [[VideoPatchCore]] — 记忆增强与正常性建模融合对象。
