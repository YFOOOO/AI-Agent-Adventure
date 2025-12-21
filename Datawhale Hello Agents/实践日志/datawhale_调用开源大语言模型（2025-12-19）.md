# 学习日志：Datawhale Hello Agents - 调用开源大语言模型

**日期**: 2025-12-19
**来源**: [Datawhale Hello Agents - 3.2.3 调用开源大语言模型（在线预览）](https://datawhalechina.github.io/hello-agents/#/./chapter3/%E7%AC%AC%E4%B8%89%E7%AB%A0%20%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E5%9F%BA%E7%A1%80?id=_323-%e8%b0%83%e7%94%a8%e5%bc%80%e6%ba%90%e5%a4%a7%e8%af%ad%e8%a8%80%e6%a8%a1%e5%9e%8b)

## 1. 项目概述
今天完成了在本地环境（macOS/Apple Silicon）下部署和调用开源大语言模型（Open Source LLMs）的实践。主要使用 Hugging Face 的 `transformers` 库，成功加载并运行了 `Qwen/Qwen1.5-0.5B-Chat` 模型，实现了基础的对话功能。

## 2. 核心技术点
- **Transformers 库**: 掌握了使用 `AutoTokenizer` 和 `AutoModelForCausalLM` 加载模型和分词器的标准流程。
- **本地硬件加速**:
    - 在 macOS 环境下，成功利用 `mps` (Metal Performance Shaders) 后端替代 `cuda` 进行 GPU 加速推理。
    - 验证了轻量级模型（0.5B参数）在个人电脑（Mac mini）上的可行性。
- **对话模板应用**: 学习了使用 `tokenizer.apply_chat_template` 将对话历史（Messages）转换为模型可理解的 Prompt 格式。
- **生成参数控制**: 实践了 `max_new_tokens` 等参数对生成长度的控制，并了解了 `attention_mask` 在避免生成警告中的作用。

## 3. 实践过程 (Engineering-Driven)
本次学习延续了工程化驱动的思路，通过文档、代码与调试的闭环来巩固知识：

1.  **知识沉淀 (`调用开源大语言模型.md`)**:
    - 系统整理了调用开源模型的核心概念、环境准备及标准代码模板。
    - 记录了硬件资源要求及网络环境配置（如使用 `hf-mirror.com` 镜像）。

2.  **部署指南 (`Qwen1.5-0.5B-Chat部署.md`)**:
    - 针对特定模型（Qwen1.5-0.5B）编写了详细的部署说明。
    - 分析了模型的硬件需求（显存/内存）及适用场景，明确了其作为轻量级实验模型的定位。

3.  **交互验证 (`demo.ipynb`)**:
    - 在 Jupyter Notebook 中编写并调试了完整的加载与推理代码。
    - **问题解决**:
        - 解决了 `transformers` 库缺失的报错。
        - 修复了 `IProgress` 进度条警告（通过 `ipywidgets`）。
        - 优化了设备检测逻辑，增加了对 macOS `mps` 的支持。
        - 修正了 `generate` 函数缺少 `attention_mask` 的警告。
    - 最终成功实现了与模型的中文对话，验证了模型的可用性。

## 4. 学习心得
- **开源生态的便利性**: Hugging Face 提供了统一且强大的接口，极大降低了使用不同开源模型的门槛。无论是 Llama 还是 Qwen，调用方式高度一致。
- **本地部署的价值**: 相比于 API 调用，本地部署虽然需要关注硬件资源，但提供了更高的数据隐私安全性和零成本的推理能力，非常适合开发阶段的调试和验证。
- **小模型的潜力**: 0.5B 参数的模型虽然规模极小，但在简单指令遵循和流畅度上表现惊人，为在端侧设备（如笔记本、手机）上运行 Agent 提供了可能。

## 5. 下一步计划
- 尝试加载更大参数规模的模型（如 Qwen2.5-7B-Instruct），对比其在推理能力上的提升。
- 探索使用 `vLLM` 或 `Ollama` 等工具部署 OpenAI 兼容的本地 API 服务，以便接入更复杂的 Agent 框架。
- 结合之前的 ReAct Agent 实践，尝试将后端 LLM 替换为本地运行的开源模型。
