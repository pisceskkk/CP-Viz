# vLLM PCP & DCP

从框架视图到 attention 数据流的中文技术分享。以 Ascend ModelRunnerV2 的普通 GQA attention 为主线，用 13 页可交互图解讲清 token 工作分工、KV 保存归属和输出合并。

- [在线演示](https://pisceskkk.github.io/CP-Viz/)
- [讲解提纲](docs/speaker-notes.md)
- [DCP 通信与组合模式](docs/dcp_communication_patterns.md)
- [图与文稿的维护方式](docs/scripts.md)

## 阅读与演示

打开 `index.html`。使用方向键或顶部选页控件翻页；“连续阅读”展开全部页面；每页的“讲解备注”提供口头讲解背景。

每个 tensor 块、操作块和箭头都是源码链接，指向固定 commit 的具体行区间。图中数值和形状是教学例子，适用范围标在对应页面中。

画布支持缩放、平移和高度调整。启用“编辑布局”后，可以拖动节点、拖动右下角调整尺寸，箭头跟随节点。布局保存在当前浏览器，可导出 JSON、导入或重置。通过这些控件可为不同投影尺寸调整图的布局。

## 代码基线

| 仓库 | 固定提交 |
| --- | --- |
| vllm-ascend | [3b433e2f027c](https://github.com/vllm-project/vllm-ascend/tree/3b433e2f027ceb47897a1343ce01174c077d5e1f) |
| vLLM | [a98247ab4db6](https://github.com/vllm-project/vllm/tree/a98247ab4db686ee03c66d5feb3c761e52a2f8ab) |

配对依据为该 Ascend 提交的 `.github/vllm-main-verified.commit`。讲解范围和通信组约束均以这些版本为准。具体模型、KV 格式与运行模式的支持情况仍需查阅对应后端。

## 构建

运行 `python build.py`，从 `src/deck.json` 和 `src/source-map.json` 生成 `index.html` 与讲解提纲。构建只需要 Python 标准库；页面使用本地 CSS 和 JavaScript。

本地预览可在仓库目录运行 `python -m http.server 8000`，然后访问 `http://localhost:8000`。将构建后的仓库作为 GitHub Pages 静态站点发布即可。
