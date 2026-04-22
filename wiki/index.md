# Wiki Index

## 索引说明

这个索引分成两层：
- **导航层**：给人快速进入主题网络，而不是在长列表里逐条找。
- **注册层**：保留完整页面登记，方便 ingest / query / lint 作为稳定入口使用。

当前知识库规模：
- Sources：16
- Entities：14
- Concepts：13
- Syntheses：2

## 快速入口
- [[VideoAnomalyDetection]] — 当前知识库最核心的主题入口，统摄无监督、弱监督、训练自由与多模态 VAD。
- [[WeaklySupervisedVideoAnomalyDetection]] — 视频级粗标注学习路线入口。
- [[TrainingFreeVideoAnomalyDetection]] — 免训练部署与大模型推理路线入口。
- [[TimeSeriesAnomalyDetection]] — 从更上位方法论理解异常检测的入口。

## 按主题浏览
- [[StateSpaceModel]] — 高效长序列建模与 VAD 结合的代表概念。
- [[MultimodalVideoAnomalyDetection]] — 音视频、多视角与 MLLM 增强路线。
- [[PseudoLabelSelfTraining]] — 弱监督 VAD 中最关键的监督提纯机制。
- [[RailwayIntrusionDetection]] — 与 VAD 相邻的安全关键应用场景入口。
- [[VADMamba]] — 状态空间模型路线的代表方法实体。
- [[EventVAD]] — 训练自由事件级推理路线的代表方法实体。

## 完整注册表

### Sources
- [[摘要-advances-in-time-series-anomaly-detection-algorithms-benchmarks-and-evaluation-measures]] — 从更上位方法论梳理时间序列异常检测算法与评测框架。
- [[摘要-attention-driven-pseudo-label-self-training-for-weakly-supervised-video-anomaly-detection]] — 提出同步式注意力驱动伪标签自训练的弱监督 VAD 方法。
- [[摘要-bidirectional-skip-frame-prediction-for-video-anomaly-detection-with-intra-domain-disparity-driven-attention]] — 用双向跳帧预测与双注意力放大异常误差的无监督 VAD 方法。
- [[摘要-ds-ib-net-ultra-lightweight-weakly-supervised-video-anomaly-detection-through-synergistic-dual-streams-and-information-bottleneck]] — 通过双流信息瓶颈兼顾轻量化与弱监督检测能力。
- [[摘要-eventvad-training-free-event-aware-video-anomaly-detection]] — 先做事件切分再做 MLLM 推理的训练自由 VAD 方法。
- [[摘要-m2vad-multiview-multimodality-transformer-based-weakly-supervised-video-anomaly-detection]] — 多视角多模态弱监督 VAD 的 Transformer 路线。
- [[摘要-prodisc-vad-an-efficient-system-for-weakly-supervised-anomaly-detection-in-video-surveillance-applications]] — 以原型交互和极值伪实例提纯监督信号的高效弱监督方法。
- [[摘要-railway-intrusion-detection-based-on-machine-vision-a-survey-challenges-and-perspectives]] — 从应用场景梳理铁路入侵检测方法与长期挑战的综述。
- [[摘要-unsupervised-video-anomaly-detection-using-video-vision-transformer-and-adversarial-training]] — 结合 ViViT、光流预测和对抗训练的无监督 VAD 方法。
- [[摘要-vadmamba-exploring-state-space-models-for-fast-video-anomaly-detection]] — 把状态空间模型引入 VAD 并强调高效推理的样板论文。
- [[摘要-video-anomaly-detection-via-spatio-temporal-pseudo-anomaly-generation-a-unified-approach]] — 通过时空伪异常生成统一开放集视频异常检测。
- [[摘要-videopatchcore-an-effective-method-to-memorize-normality-for-video-anomaly-detection]] — 用多粒度记忆库记住正常模式的训练自由 VAD 方法。
- [[摘要-attention-guided-bidirectional-memory-autoencoder-for-video-anomaly-detection]] — 双向记忆 + 注意力 + 伪异常训练的记忆增强 VAD 方法。
- [[摘要-moba-motion-memory-augmented-deblurring-autoencoder-for-video-anomaly-detection]] — 去模糊伪异常 + 运动记忆检索的跨域稳健 VAD 方法。
- [[摘要-stnmamba-mamba-based-spatial-temporal-normality-learning-for-video-anomaly-detection]] — 用 Mamba/SSM 学习时空一致性并配套记忆库的高效 VAD 方法。
- [[摘要-vadclip-adapting-vision-language-models-for-weakly-supervised-video-anomaly-detection]] — 冻结 CLIP + 双分支对齐的弱监督 VAD 方法。

### Entities
- [[ADPLGVAD]] — 注意力驱动的同步式伪标签自训练弱监督 VAD 方法。
- [[BiSP]] — 利用双向跳帧预测放大异常误差的无监督 VAD 方法。
- [[DSIBNet]] — 通过双流信息瓶颈实现超轻量弱监督 VAD 的方法。
- [[EventVAD]] — 先事件切分再 MLLM 推理的训练自由 VAD 方法。
- [[M2VAD]] — 多视角多模态 Transformer 式弱监督 VAD 方法。
- [[ProDiscVAD]] — 以正常原型和极值伪实例提纯监督信号的高效弱监督方法。
- [[PseudoAnomalyGenerationVAD]] — 统一生成时空伪异常并聚合多信号评分的无监督方法。
- [[VADMamba]] — 把状态空间模型用于高效视频异常检测的混合检测方法。
- [[VideoPatchCore]] — 以记忆库压缩和 CLIP 特征为核心的训练自由 VAD 方法。
- [[ViViTAdversarialVAD]] — 结合 ViViT、光流预测与对抗训练的无监督方法。
- [[ABMA]] — 双向记忆 + 注意力的记忆增强 VAD 方法。
- [[MoBA]] — 去模糊伪异常 + 运动记忆检索的 VAD 方法。
- [[STNMamba]] — Mamba/SSM 驱动的时空一致性学习 VAD 方法。
- [[VadCLIP]] — 冻结 CLIP + 对齐分支的弱监督 VAD 方法。

### Concepts
- [[BidirectionalSkipFramePrediction]] — 通过双向跳帧预测主动放大正常/异常差异的机制概念。
- [[InformationBottleneck]] — 通过压缩冗余表征提升效率的表示学习思想。
- [[MemoryAugmentedVideoAnomalyDetection]] — 用显式记忆库存储正常模式的 VAD 路线。
- [[MultimodalVideoAnomalyDetection]] — 同时利用音频、光流、文本或大模型推理的 VAD 路线。
- [[PseudoAnomalyGeneration]] — 从正常样本构造近异常样本以提升开放集泛化的机制概念。
- [[PseudoLabelSelfTraining]] — 从粗标签中生成并迭代修正片段伪标签的训练机制。
- [[RailwayIntrusionDetection]] — 面向高安全铁路场景的视觉入侵检测任务。
- [[StateSpaceModel]] — 以高效长序列建模为特征的时序模型家族。
- [[TimeSeriesAnomalyDetection]] — 视频异常检测可借鉴的更上位异常检测方法论框架。
- [[TrainingFreeVideoAnomalyDetection]] — 不针对目标数据集专门训练的 VAD 路线。
- [[VideoAnomalyDetection]] — 在视频序列中识别异常行为或事件的核心任务。
- [[WeaklySupervisedVideoAnomalyDetection]] — 只依赖视频级粗标签训练异常定位模型的任务设定。
- [[SpatialTemporalConsistency]] — 用多层级时空一致性刻画正常耦合模式的建模目标。

### Syntheses
- [[bisp-fusion-strategies]] — 总结 BiSP 与长序列建模、显著性细化、伪异常生成和记忆增强路线的融合优先级。
- [[bisp-abma-stnmamba-comparison]] — 比较 ABMA、STNMamba 相对 BiSP 的承接关系与创新差异。
