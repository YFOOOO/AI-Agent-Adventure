# 学习日志：Datawhale Hello Agent - 5分钟实现第一个智能体

**日期**: 2025-12-13
**来源**: [Datawhale Hello Agent - 1.3 动手体验](https://datawhalechina.github.io/hello-agents/#/./chapter1/%E7%AC%AC%E4%B8%80%E7%AB%A0%20%E5%88%9D%E8%AF%86%E6%99%BA%E8%83%BD%E4%BD%93?id=_13-%e5%8a%a8%e6%89%8b%e4%bd%93%e9%aa%8c%ef%bc%9a5-%e5%88%86%e9%92%9f%e5%ae%9e%e7%8e%b0%e7%ac%ac%e4%b8%80%e4%b8%aa%e6%99%ba%e8%83%bd%e4%bd%93)

## 1. 项目概述
今天完成了第一个基于 **ReAct (Reasoning + Acting)** 范式的智能体——“智能旅行助手”。该智能体能够理解用户自然语言请求，自主规划任务，调用外部工具查询天气和搜索景点，最终给出旅行建议。

## 2. 核心技术点
- **ReAct 范式**: 深入理解了 `Thought` (思考) -> `Action` (行动) -> `Observation` (观察) 的循环机制。
- **工具调用 (Tool Use)**:
    - `get_weather`: 集成 `wttr.in` 获取实时天气。
    - `get_attraction`: 集成 `Tavily` 进行语义搜索。
- **LLM 集成**: 使用 OpenAI 兼容接口（智谱 GLM-4-Flash）作为智能体的大脑。
- **正则解析**: 手动实现对 LLM 输出的结构化解析，提取 Action 和参数。

## 3. 实践方法论 (Engineering-Driven)
本次学习采用了**工程化驱动**的工作流，而非简单的脚本编写：

1.  **文档先行 (`docs.md`)**: 
    - 沉淀了环境配置、API Key 管理和依赖库信息，确保环境可复现。
2.  **设计分离 (`spec.md`)**: 
    - 将 **System Prompt** 和 **工具定义** 独立于代码之外。
    - 这种“Prompt 即代码”的设计理念有助于专注于优化智能体的行为规范。
3.  **交互验证 (`travel_agent_demo.ipynb`)**: 
    - 利用 Jupyter Notebook 的交互性，分步调试 Agent 的思考过程。
    - 能够清晰地看到 Agent 如何因“幻觉”或逻辑错误而失败，并即时调整 Prompt。

## 4. 学习心得
- **本地环境的重要性**: 相比于云端 Playground，本地运行代码让我对 Agent 的底层逻辑（如 HTTP 请求、字符串解析）有了更直观的掌控。
- **结构化思维**: 将设计 (Spec) 与实现 (Code) 分离，不仅让代码更清晰，也为未来扩展更复杂的 Multi-Agent 系统打下了基础。
- **调试技巧**: 观察中间的 `Thought` 输出是调试 Agent 行为的关键，它揭示了模型是如何“理解”任务的。

## 5. 下一步计划
- 尝试将 Notebook 代码重构为模块化的 Python 脚本 (`agent.py`, `tools.py`)。
- 探索如何动态加载 `spec.md` 中的 Prompt。
- 为工具函数添加简单的单元测试。