---
title: "TimeSeriesAnomalyDetection"
type: concept
tags: [时间序列, 异常检测, 方法论]
sources: ["raw/09-archive/Paparrizos et al. - 2025 - Advances in time-series anomaly detection algorithms, benchmarks, and evaluation measures.pdf"]
last_updated: 2026-04-20
---

## 定义
TimeSeriesAnomalyDetection 指在时间相关数据中识别偏离正常模式的点、区间或事件，是更广义的异常检测母任务，视频异常检测可视为其在视觉时空信号上的特化。

## 关键信息
- 现有综述通常把方法归纳为距离型、密度型与预测/重建型三大路线。
- 评价不能只依赖单一 AUC，因为点异常、区间异常、监督设定与数据域差异会显著改变结果排序。
- 对本库的价值在于提供上位方法论框架，帮助把视频异常检测放到更通用的异常检测谱系中理解。

## 关联连接
- [[摘要-advances-in-time-series-anomaly-detection-algorithms-benchmarks-and-evaluation-measures]] — 方法论来源综述。
- [[VideoAnomalyDetection]] — 视频异常检测是该任务在视觉数据上的特化。
- [[StateSpaceModel]] — 长序列建模是近年重要趋势。
