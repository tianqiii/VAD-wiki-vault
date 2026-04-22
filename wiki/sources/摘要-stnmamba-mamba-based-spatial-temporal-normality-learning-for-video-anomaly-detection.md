---
title: "摘要-stnmamba-mamba-based-spatial-temporal-normality-learning-for-video-anomaly-detection"
type: source
tags: [来源, 论文, 视频异常检测, 状态空间模型, 记忆增强]
sources: ["raw/09-archive/Li 等 - 2026 - STNMamba mamba-based spatial-temporal normality learning for video anomaly detection.pdf"]
last_updated: 2026-04-22
---

## Metadata
- **作者**: Zhangxun Li；Mengyang Zhao；Xuan Yang；Yang Liu；Jiamu Sheng；Xinhua Zeng；Tian Wang；Kewei Wu；Yu-Gang Jiang
- **年份**: 2026
- **期刊/会议**: IEEE Transactions on Multimedia
- **DOI / arXiv**: DOI: 10.1109/TMM.2026.3664969；arXiv: 2412.20084
- **链接**: https://doi.org/10.1109/TMM.2026.3664969

## 核心摘要
这篇论文提出 STNMamba，把 Mamba/状态空间模型用于无监督视频异常检测的“时空正常性学习”。方法采用**空间-时间双编码器**：空间编码器用多尺度的 Vision Space State Block 提取不同尺度外观特征；时间编码器用通道注意力增强的 VSS Block 对相邻帧 RGB 差分建模，从而更轻量地获取运动模式。核心设计是 STIM（Spatial-Temporal Interaction Module）：在多层级上把空间/时间特征映射到统一空间，再结合多层记忆库存储“正常时空原型”，推理时在图像域（预测误差/PSNR）与特征域（到记忆项距离）联合打分。论文强调在保持较低 FLOPs/参数量的同时在 Ped2/Avenue/ShanghaiTech 上获得有竞争力的 AUC。

## 论文问题
- Transformer 二次复杂度影响部署：如何在长序列建模上更高效地学习时空正常模式？
- 现有双流方法常在瓶颈处一次性融合：如何在多层级建模“时空一致性”，避免浅层/深层信息断裂？

## 方法要点
- **MS-VSSB / CA-VSSB**：分别面向多尺度外观与关键运动通道的建模。
- **STIM + 记忆库**：每个层级进行时空融合并配套记忆库，存储正常原型。
- **异常分数**：PSNR（图像域）与到最近记忆项的距离（特征域）加权融合。

## 实验与局限
- 论文报告在三大基准（Ped2、Avenue、ShanghaiTech）上兼顾效率与性能。
- 依赖 RGB 差分作为运动输入：对长时间跨度的复杂运动可能需要更强的时序建模与更稳健的融合策略。

## 关联连接
- [[STNMamba]] — 论文提出的方法实体。
- [[StateSpaceModel]] — 以 Mamba/SSM 为代表的高效长序列建模路线。
- [[SpatialTemporalConsistency]] — 论文主打的多层级时空一致性建模目标。
- [[VideoAnomalyDetection]] — 上位任务。
- [[BiSP]] — 用户指出 STNMamba 在相关工作中引用 BiSP（双流预测式路线）。
