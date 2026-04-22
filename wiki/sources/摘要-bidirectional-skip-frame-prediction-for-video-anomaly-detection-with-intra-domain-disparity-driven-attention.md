---
title: "摘要-bidirectional-skip-frame-prediction-for-video-anomaly-detection-with-intra-domain-disparity-driven-attention"
type: source
tags: [来源, 论文, 视频异常检测]
sources: ["raw/09-archive/Lyu et al. - 2026 - Bidirectional skip-frame prediction for video anomaly detection with intra-domain disparity-driven a.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Jiahao Lyu，Minghua Zhao，Jing Hu，Runtao Xi，Xuewen Huang，Shuangli Du，Cheng Shi，Tian Ma
- **年份**: 2026
- **期刊/会议**: Pattern Recognition
- **DOI / arXiv**: DOI: 10.1016/j.patcog.2025.112010；arXiv: 2407.15424

## 核心摘要
这篇论文提出 BiSP，一种双向跳帧预测的视频异常检测方法。作者认为，异常检测的关键在于拉大正常与异常之间的域内差异，因此在训练阶段使用前向和后向跳帧分别预测目标帧，在测试阶段再让双向上下文共同预测中间帧，以放大异常误差。为进一步强化这种差异，论文还设计了方差通道注意力和上下文空间注意力，分别针对动作模式与对象尺度建模。实验结果表明，这种“跳帧 + 双向预测 + 双注意力”的组合在多个无监督 VAD 数据集上优于文中的对比方法。

## 论文问题
- 如何通过预测任务更明显地拉开正常样本与异常样本的域内差异。
- 如何让预测式异常检测同时捕捉动作模式与对象尺度变化。

## 方法要点
- 在训练阶段使用前向和后向跳帧分别预测目标帧，在测试阶段用双向上下文共同预测中间帧。
- 用这种跳帧预测策略放大异常样本的预测误差，使正常/异常边界更清晰。
- 进一步加入方差通道注意力和上下文空间注意力，分别建模动作模式与对象尺度。

## 实验与局限
- 论文结果表明，这种“跳帧 + 双向预测 + 双注意力”的组合在多个无监督 VAD 数据集上优于文中的对比方法。
- 该路线的表现依赖预测任务设计与视频帧率/动作节奏的匹配程度，跨场景迁移时可能需要重新权衡跳帧策略。

## 关联连接
- [[BiSP]] — 论文提出的核心方法实体。
- [[BidirectionalSkipFramePrediction]] — 该方法体现了这一设计思想。
- [[VideoAnomalyDetection]] — 属于预测式无监督异常检测路线。
