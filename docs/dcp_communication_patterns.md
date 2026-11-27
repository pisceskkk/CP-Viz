# DCP 通信与组合模式

本文对应 vLLM `a98247ab4db686ee03c66d5feb3c761e52a2f8ab` 与 vllm-ascend `3b433e2f027ceb47897a1343ce01174c077d5e1f`，沿普通 GQA attention 解释通信的语义。

## 分片后的 attention

DCP 让各 rank 保存和读取不同的 KV 序列子集。为同一 query/head 计算完整 attention 时，参与者先获得所需 query heads，然后各自计算局部已归一化输出 Oᵢ 与 softmax 分母的对数 LSEᵢ。交换部分结果后，按各子集在全局分母中的份额加权合并。

这个过程要求相同 query/head、相同打分尺度与可见性规则；KV 子集互不重叠且覆盖目标可见范围。具体 collective 服务于这些语义，取决于组布局与后端实现。[query 传输](https://github.com/vllm-project/vllm-ascend/blob/3b433e2f027ceb47897a1343ce01174c077d5e1f/vllm_ascend/attention/context_parallel/common_cp.py#L180-L210)、[结果交换](https://github.com/vllm-project/vllm-ascend/blob/3b433e2f027ceb47897a1343ce01174c077d5e1f/vllm_ascend/attention/context_parallel/common_cp.py#L213-L243)、[合并定义](https://github.com/vllm-project/vllm-ascend/blob/3b433e2f027ceb47897a1343ce01174c077d5e1f/vllm_ascend/attention/context_parallel/common_cp.py#L324-L335)。

## 历史与当前

Chunked prefill 将参与计算的 KV 逻辑范围分成历史前缀和当前 chunk。历史各分片与当前的因果分支共同构成完整可见上下文；对同一输出 query/head，当前贡献只计一次。当前 KV 可以已经写入物理缓存，计算仍须按逻辑范围区分历史与当前。[组合流程](https://github.com/vllm-project/vllm-ascend/blob/3b433e2f027ceb47897a1343ce01174c077d5e1f/vllm_ascend/attention/context_parallel/attention_cp.py#L652-L712)。

普通单 token decode 可在一次本地 attention 中覆盖含当前位置的本地 KV。多 query、因果与投机策略也可能采用历史/当前拆分路径。[decode 流程](https://github.com/vllm-project/vllm-ascend/blob/3b433e2f027ceb47897a1343ce01174c077d5e1f/vllm_ascend/attention/context_parallel/attention_cp.py#L471-L529)。

## PCP 与 DCP 共同启用

PCP 分配本轮 token 工作，DCP 组织 KV 序列分片。组合 prefill 的历史路径会先跨 PCP 汇集并恢复 query 的逻辑排列，传输需要的独立 query heads；结果交换后选择本地 query 对应的贡献，再与当前分支合并。[历史 query 准备](https://github.com/vllm-project/vllm-ascend/blob/3b433e2f027ceb47897a1343ce01174c077d5e1f/vllm_ascend/attention/context_parallel/attention_cp.py#L531-L542)。

| 配置范围 | DCP 协作组 |
| --- | --- |
| PCP=1 | 复用 TP ranks；DCP 大小需整除 TP |
| PCP>1，DCP=1 | 采用 PCP 的 token 工作分工 |
| PCP>1，DCP=PCP | DCP 覆盖 PCP 轴 |
| PCP>1，DCP=TP×PCP | DCP 覆盖整个 TP×PCP 域 |

这些是固定版本的组大小约束。实际后端与模型还可有附加限制。[配置检查](https://github.com/vllm-project/vllm/blob/a98247ab4db686ee03c66d5feb3c761e52a2f8ab/vllm/config/parallel.py#L585-L598)、[通信组构造](https://github.com/vllm-project/vllm/blob/a98247ab4db686ee03c66d5feb3c761e52a2f8ab/vllm/distributed/parallel_state.py#L2216-L2251)。
