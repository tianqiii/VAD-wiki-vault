---
title: bisp-abma-stnmamba-comparison
type: synthesis
tags:
  - 综合分析
  - 视频异常检测
  - BiSP
  - ABMA
  - STNMamba
  - 方法比较
sources:
  - raw/09-archive/Lyu et al. - 2026 - Bidirectional skip-frame prediction for video anomaly detection with intra-domain disparity-driven a.pdf
  - raw/09-archive/Le和Nguyen - 2026 - Attention-guided bidirectional memory autoencoder for video anomaly detection.pdf
  - raw/09-archive/Li 等 - 2026 - STNMamba mamba-based spatial-temporal normality learning for video anomaly detection.pdf
last_updated: 2026-04-22
---

## 核心结论
[[ABMA]] 和 [[STNMamba]] 都不是在简单复刻 [[BiSP]]，而是各自承接了 BiSP 所代表的“预测式/双向时空建模”路线中的一部分核心思想，再用新的结构重新组织。[[ABMA]] 承接的是“利用过去/未来双向上下文增强异常可分性”这条主线；[[STNMamba]] 承接的则是 BiSP 所代表的“双流预测式视频异常检测框架”在时空建模上的问题意识，并进一步把重点转向高效长序列建模与多层级时空一致性。

## BiSP 的核心基线角色
[[BiSP]] 的核心方法可以压缩成三点：第一，训练时做前向/后向跳帧预测，测试时用双向上下文共同预测中间帧；第二，通过这种双向预测任务主动放大正常与异常之间的预测误差；第三，再用方差通道注意力与上下文空间注意力增强动作模式与对象尺度建模。也就是说，BiSP 的价值不只在“双向”两个字，而在于它把“双向上下文”明确绑定到了“异常误差放大”这一检测目标上。

## ABMA 承接了 BiSP 的什么
[[ABMA]] 承接的是 [[BiSP]] 的“双向上下文增强异常可分性”思想，而不是其具体的“跳帧预测”实现。BiSP 用双向跳帧预测让异常更难被准确预测；ABMA 则把这种思路转写成“过去记忆 + 未来记忆”的双向记忆结构，并继续保留“past/future 双向信息共同参与异常评分”的框架。因此，从知识库现有证据看，ABMA 对 BiSP 的引用重点更像是：**认可双向时序建模在放大正常/异常差异上的作用**。

## ABMA 相对 BiSP 的创新点
- **从双向预测变成双向记忆**：BiSP 主要通过任务设计放大预测误差；ABMA 则把过去/未来分别存入记忆子空间，显式约束正常模式的表示边界。
- **把异常分数从图像域扩展到特征域**：BiSP 的重点仍是预测误差，ABMA 则额外加入“潜空间到记忆项的距离”。
- **引入伪异常训练机制**：ABMA 用 skip-frame 合成伪异常，并通过正常损失与异常损失共同压制模型对异常样本的重建/预测能力。
- **双向建模与注意力/记忆更深度耦合**：BiSP 已有双注意力，但 ABMA 更强调“记忆读取 + 空间注意力 + 双向误差”的整体协同。

## STNMamba 承接了 BiSP 的什么
[[STNMamba]] 对 [[BiSP]] 的承接更偏“方法谱系层面”。从本地知识库现有摘要看，它并不是去复用 BiSP 的跳帧策略或双注意力细节，而是把 BiSP 所代表的“空间/时间分开建模，再通过预测任务做异常检测”的双流路线视为相关工作背景。STNMamba 想解决的问题恰好是这类方法的局限：现有双流方法通常在瓶颈处一次性融合，难以在多层级上显式建模时空一致性。

## STNMamba 相对 BiSP 的创新点
- **从预测任务主导转向骨干建模主导**：BiSP 的核心是跳帧预测任务；STNMamba 的核心是用 [[StateSpaceModel]] / Mamba 作为高效时空建模骨干。
- **强调多层级时空一致性**：BiSP 更像单条双向预测链路；STNMamba 用 STIM 在多个层级持续融合空间与时间特征，显式建模 [[SpatialTemporalConsistency]]。
- **引入多层记忆库存储正常时空原型**：这使 STNMamba 的“正常性建模”比 BiSP 更偏向原型约束，而不只是让异常预测失败。
- **效率导向更强**：STNMamba 明确把“降低 FLOPs/参数量、保持 FPS”作为设计目标之一，这与 BiSP 的主要卖点不同。

## 对比总结
如果把 [[BiSP]] 视为“**双向预测式异常误差放大器**”，那么 [[ABMA]] 更像“**双向记忆增强版 BiSP**”，它把双向思想继续深化到记忆与训练目标层；而 [[STNMamba]] 更像“**高效时空骨干版后继路线**”，它承接的是 BiSP 所在方法家族的问题设定，但真正的突破点在于 Mamba 驱动的时空一致性建模，而不在跳帧预测本身。

## 关联连接
- [[BiSP]] — 本页比较的起点方法。
- [[ABMA]] — 双向记忆 + 注意力路线。
- [[STNMamba]] — Mamba/SSM + 多层级时空一致性路线。
- [[BidirectionalSkipFramePrediction]] — BiSP 所代表的机制概念。
- [[StateSpaceModel]] — STNMamba 的关键上位概念。
- [[SpatialTemporalConsistency]] — STNMamba 的核心建模目标。
