## [2026-04-20] ingest | 补全 12 篇视频异常检测相关论文的主题层、全局索引并完成归档
- **变更**: 新增 [[VideoAnomalyDetection]]、[[WeaklySupervisedVideoAnomalyDetection]]、[[TrainingFreeVideoAnomalyDetection]] 等概念页；新增 [[VADMamba]]、[[EventVAD]]、[[VideoPatchCore]] 等方法实体页；更新 [[index]]；归档 12 篇原始论文 PDF
- **冲突**: 无

## [2026-04-20] query | 分析 BiSP 方法适合与哪些路线融合
- **输出**: [[BiSP]], [[BidirectionalSkipFramePrediction]], [[VADMamba]], [[ViViTAdversarialVAD]], [[PseudoAnomalyGenerationVAD]], [[VideoPatchCore]], [[StateSpaceModel]], [[PseudoAnomalyGeneration]]

## [2026-04-20] query | 保存 BiSP 融合建议综合页
- **输出**: 已保存至 [[bisp-fusion-strategies]]

## [2026-04-22] sync | 为 12 篇论文摘要补齐 Metadata
- **变更**: 更新 12 个 `wiki/sources/摘要-*.md`，新增 `## Metadata`（作者/年份/期刊或会议/DOI或arXiv），并同步更新 last_updated

## [2026-04-22] ingest | 引入 4 篇新论文（含 2 篇引用 BiSP）并补齐主题层与索引
- **变更**: 新增 sources：[[摘要-attention-guided-bidirectional-memory-autoencoder-for-video-anomaly-detection]]、[[摘要-moba-motion-memory-augmented-deblurring-autoencoder-for-video-anomaly-detection]]、[[摘要-stnmamba-mamba-based-spatial-temporal-normality-learning-for-video-anomaly-detection]]、[[摘要-vadclip-adapting-vision-language-models-for-weakly-supervised-video-anomaly-detection]]；新增 entities：[[ABMA]]、[[MoBA]]、[[STNMamba]]、[[VadCLIP]]；新增 concept：[[SpatialTemporalConsistency]]；更新 [[BiSP]]、[[StateSpaceModel]]、[[MemoryAugmentedVideoAnomalyDetection]]、[[WeaklySupervisedVideoAnomalyDetection]]、[[PseudoAnomalyGeneration]] 与 [[index.md]]
- **冲突**: 无

## [2026-04-22] query | 比较 ABMA、MoBA 相对 BiSP 的引用点与创新点
- **输出**: [[摘要-attention-guided-bidirectional-memory-autoencoder-for-video-anomaly-detection]], [[摘要-moba-motion-memory-augmented-deblurring-autoencoder-for-video-anomaly-detection]], [[摘要-bidirectional-skip-frame-prediction-for-video-anomaly-detection-with-intra-domain-disparity-driven-attention]]

## [2026-04-22] query | 比较 ABMA、STNMamba 相对 BiSP 的引用点与创新点
- **输出**: [[摘要-attention-guided-bidirectional-memory-autoencoder-for-video-anomaly-detection]], [[摘要-stnmamba-mamba-based-spatial-temporal-normality-learning-for-video-anomaly-detection]], [[摘要-bidirectional-skip-frame-prediction-for-video-anomaly-detection-with-intra-domain-disparity-driven-attention]]

## [2026-04-22] query | 保存 ABMA、STNMamba 与 BiSP 的对比综合页
- **输出**: 已保存至 [[bisp-abma-stnmamba-comparison]]

## [2026-04-26] query | 铁路场景异常检测实用路线——以 BiSP 为基座的五步迭代
- **输出**: [[BiSP]], [[bisp-fusion-strategies]], [[VADMamba]], [[ViViTAdversarialVAD]], [[PseudoAnomalyGenerationVAD]], [[VideoPatchCore]], [[摘要-railway-intrusion-detection-based-on-machine-vision-a-survey-challenges-and-perspectives]]

## [2026-04-24] ingest | paper-deep-reading 为 摘要-self-distilled-masked-auto-encoders-are-efficient-video-anomaly-detectors 生成图示与公式骨架
- **变更**: 新增或更新 [[摘要-self-distilled-masked-auto-encoders-are-efficient-video-anomaly-detectors]]；新增 `assets/papers/self-distilled-masked-auto-encoders-are-efficient-video-anomaly-detectors/...`
- **冲突**: 无

## [2026-04-24] ingest | 摄入 Self-Distilled Masked Auto-Encoders 论文并接入 VAD 概念网络
- **变更**: 更新 [[摘要-self-distilled-masked-auto-encoders-are-efficient-video-anomaly-detectors]]；新增 [[AEDMAE]]、[[SelfDistillationForVideoAnomalyDetection]]；更新 [[PseudoAnomalyGeneration]]、[[VideoAnomalyDetection]] 与 [[index.md]]
- **冲突**: 无

## [2026-04-25] query | 回答铁路场景异常检测面临的困难和挑战
- **输出**: [[摘要-railway-intrusion-detection-based-on-machine-vision-a-survey-challenges-and-perspectives]], [[RailwayIntrusionDetection]], [[VideoAnomalyDetection]], [[摘要-advances-in-time-series-anomaly-detection-algorithms-benchmarks-and-evaluation-measures]]

## [2026-04-26] sync | 恢复 Self-Distilled / AEDMAE 缺失页面以修复 lint 阻塞
- **变更**: 新增 [[摘要-self-distilled-masked-auto-encoders-are-efficient-video-anomaly-detectors]]、[[AEDMAE]]、[[SelfDistillationForVideoAnomalyDetection]]；保持 [[index.md]] 注册表与规模统计一致
- **冲突**: 无
