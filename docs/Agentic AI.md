# 学习 Agent

## 参考文档
1. **Datawhale:** [Hello Agent](https://github.com/datawhalechina/hello-agents)
    - [在线阅读](https://datawhalechina.github.io/hello-agents/#/)
2. [500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects)
3. **Nir Diamant:**  [GenAI Agents](https://github.com/NirDiamant/GenAI_Agents)
4. [The Hugging Face Agents Course](https://hf.co/learn/agents-course)
5. **Microsoft:** [AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners)
6. **Ed Donner:** [6 周学会 AI 智能体](https://github.com/ed-donner/agents)


## 实战学习工作流 (Methodology)

采用 **"工程化驱动 (Engineering-Driven)"** 的学习路径，将智能体开发拆解为设计、文档与实现三个阶段，而非单纯的代码堆砌。

### 1. 知识内化 (Docs)
- **文件**: `docs.md`
- **目的**: 技术沉淀与环境配置。
- **内容**: 记录核心依赖库（如 `openai`, `langchain`）、API 接入方式、环境变量配置以及关键技术原理（如 ReAct 范式）。

### 2. 架构设计 (Spec)
- **文件**: `spec.md`
- **目的**: 定义智能体的“大脑”与“手脚”，实现**Prompt 与代码逻辑的分离**。
- **内容**:
    - **System Prompt**: 明确 Agent 的角色、任务边界及输出格式（如 Thought-Action）。
    - **Tools Definition**: 规范工具函数的输入参数、输出结构及功能描述。

### 3. 原型验证 (Playground)
- **文件**: `*.ipynb` (Jupyter Notebook)
- **目的**: 交互式开发与调试。
- **内容**:
    - **分步执行**: 逐步验证工具调用逻辑。
    - **可观测性**: 利用 Notebook 特性清晰观察 Agent 的思考链（Thought -> Action -> Observation）。
    - **快速迭代**: 在不重启整个应用的情况下调整 Prompt 和参数。

### 4. 架构驱动开发 (Architecture-Driven) - v2.0
随着项目复杂度增加，引入 **Core-Logic Separation** 架构，将工作流升级为标准化范式：

1.  **Scaffold (脚手架)**:
    - 直接复制 `template/core` 作为基建。
    - *收益*: 起步即拥有统一的 Client、鲁棒的解析器和漂亮的 UI。

2.  **Design (设计 - Spec)**:
    - **Pattern Selection**: 决定使用哪种模式？(ReAct? Reflection? Planning?)
    - **Interface Definition**: 定义 `agent_logic.py` 中的 Prompt 和 Tools。
    - *收益*: 先想清楚“怎么思考”，再写代码。

3.  **Implement (实现 - Logic)**:
    - 编写 `agent_logic.py`。
    - 只关注业务逻辑（Prompt 调优、工具实现），不关心底层。
    - *收益*: 代码纯粹，易于维护。

4.  **Orchestrate (编排 - Flow)**:
    - 在 Notebook 中引用 `core` 和 `logic`。
    - 编写循环逻辑（或调用 `patterns/` 中的通用循环）。
    - *收益*: 可视化调试，快速验证。


## 实战经验

- 2025-12-13 Datawhale Hello Agent - 5分钟实现第一个智能体

| 实战总结 (基础构建篇) | 补充建议 (进阶思维篇) |
| :--- | :--- |
| **1. 确立工程化工作流**<br>建立“文档(Docs) -> 设计(Spec) -> 验证(Playground)”的闭环。先沉淀知识与定义接口，再进行代码实现，避免了盲目编程带来的混乱。 | **1. Prompt 即代码 (Prompt as Code)**<br> 在 Agent 开发中，System Prompt 定义了智能体的行为协议和思考方式。将 Prompt 从业务代码中剥离出来（如存放在 `spec.md`），像对待代码一样对其进行版本管理和迭代，是构建稳定智能体的关键。 |
| **2. 规范环境变量配置**<br>掌握安全开发规范。使用 `.env` 文件管理 API Key，坚决避免将敏感密钥硬编码在代码中，这是从 Demo 走向生产环境的安全基石。 | **2. 本地环境优于云端沙盒**<br>虽然云端 Playground 上手快，但本地开发环境（VS Code + Python）能让你掌控底层细节（如 API 鉴权、依赖管理、网络请求），这对于理解 Agent 如何与真实世界交互至关重要，也为后续的工程化部署打下基础。 |
| **3. 交互式开发与调试**<br>利用 Jupyter Notebook “所见即所得”的特性。分步执行代码，实时验证工具调用逻辑，极大地降低了调试 Agent 复杂行为的门槛。 | **3. 可观测性是调试的核心**<br> Agent 的行为具有不确定性。通过 Jupyter Notebook 或日志系统，完整记录 `Thought` (思考) -> `Action` (行动) -> `Observation` (观察) 的全过程，才能有效定位是模型推理能力不足（Thought 错误）还是工具调用失败（Action 错误）。 |
---

- 2025-12-14 Agentic AI (DeepLearning) - Chart Generation (Reflection Pattern)

| 实战总结 (多模态协作篇) | 补充建议 (工程化架构篇) |
| :--- | :--- |
| **1. 模型能力各司其职**<br>在多步骤工作流中，不同环节对模型能力要求不同。生成代码阶段使用强逻辑模型（如 `qwen3-max`），而视觉反思阶段必须使用强多模态模型（如 `qwen-vl-plus`），“术业有专攻”能显著提升整体效果。 | **1. 异构模型协作 (Heterogeneous Collaboration)**<br>未来的 Agent 系统往往是异构的。学会组合不同厂商、不同特性的模型（如用 Qwen 写代码，用 GLM 看图），利用各自的长板构建更强大的智能体，是进阶开发者的必备技能。 |
| **2. 防御性解析逻辑**<br>LLM 的输出格式极不稳定（如 JSON 中嵌套代码、Markdown 格式缺失）。必须编写鲁棒的正则解析代码（Regex Parsing）和兜底机制（Fallback），不能假设模型总是完美遵循指令。 | **2. 永远不要信任模型的输出**<br>在工程实现中，要把 LLM 当作一个“不可靠的组件”。通过多层 `try-except`、灵活的正则匹配甚至重试机制，来消化模型输出的随机性，保证 Agent 运行时的稳定性。 |
| **3. 统一客户端封装**<br>通过自定义 `OpenAICompatibleClient` 类，抹平了不同模型厂商（阿里、智谱）在 API 调用上的细微差异。这使得在代码中切换模型就像修改配置字符串一样简单。 | **3. 基础设施解耦**<br>将模型调用层与业务逻辑层分离。当需要测试新模型或切换供应商时，无需修改核心业务代码。这种低耦合的架构设计对于快速迭代和降低迁移成本至关重要。 |

## Agent 前沿

**核心结论：**  
MAS 的不同架构与模式可以分为 **Workflow、Agent、Claude Skill、Claude Deep Research、LangGraph Deep Agent** 等几类。它们分别解决了 **稳定性 vs 灵活性** 的矛盾，演进路径清晰。以下报告基于官方与 GitHub 仓库文档重新整理。

---

🧩 MAS 架构模式详解

### 1. **Workflow 模式**
- **结构**：任务逻辑由开发者显式编排成有向图（DAG）。  
- **优点**：稳定、可控，适合固定流程。  
- **缺点**：灵活性不足。  
- **应用场景**：报表生成、数据清洗。  

---

### 2. **Agent 模式**
- **结构**：由大模型驱动，运行工具循环以达成目标。  
- **优点**：灵活、上限高，可处理复杂任务。  
- **缺点**：稳定性差，可能出现幻觉。  
- **应用场景**：探索性任务、跨领域问题。  

---

### 3. **Claude Skill 模式**
- **结构**：Skill 是文件夹，包含 `SKILL.md`、脚本和资源，用于封装业务知识。  
- **特点**：  
  - 模块化、可复用  
  - 渐进式披露（progressive disclosure），按需加载上下文  
- **应用场景**：文档处理、行业知识封装、API 调用。  
- **参考文档**：  
  - [Claude Skills 官方 GitHub 仓库](https://github.com/Claude-Skills-Org/skills-main)  

---

### 4. **Claude Deep Research 模式**
- **结构**：主代理自动拆解复杂问题，生成子任务；子代理并行执行，最后汇总为研究报告。  
- **特点**：  
  - 自动化研究，跨领域信息整合  
  - 输出结构化、带引用  
- **应用场景**：学术研究、市场调研、战略分析。  
- **参考文档**：  
  - [Claude Deep Research GitHub 仓库](https://github.com/mcherukara/Claude-Deep-Research)  
  - [Anthropic 官方开发指南](https://www.anthropic.com/learn/build-with-claude)  

---

### 5. **LangGraph Deep Agent 主次代理模式**
- **结构**：  
  - **Main Agent**：负责全局规划与调度  
  - **Sub Agents**：负责上下文隔离、并行执行、专业分工  
  - 支持文件系统、长期记忆、上下文压缩  
- **特点**：  
  - 长时间运行稳定  
  - 复杂任务可分解、并行处理  
- **应用场景**：长周期任务（如旅行规划、跨平台数据整合）、多工具调用场景。  
- **参考文档**：  
  - [LangChain Deep Agents GitHub 仓库](https://github.com/langchain-ai/deepagents)  
  - [LangChain Deep Agents Quickstarts](https://github.com/langchain-ai/deepagents-quickstarts)  
  - [LangChain 官方文档](https://docs.langchain.com/oss/python/deepagents/overview)  

---

### 📊 对比总结

| 模式 | 核心结构 | 优势 | 局限 | 典型场景 |
|------|----------|------|------|----------|
| **Workflow** | 有向图流程 | 稳定、可控 | 灵活性不足 | 固定流程任务 |
| **Agent** | LLM + 工具循环 | 灵活、上限高 | 稳定性差 | 探索性任务 |
| **Claude Skill** | 模块化技能文件 | 可复用、上下文管理优雅 | 依赖触发准确率 | 行业知识封装 |
| **Claude Deep Research** | 主代理 + 并行子任务 | 自动化研究、结构化报告 | 耗时长、依赖模型能力 | 学术/市场研究 |
| **LangGraph Deep Agent** | 主次代理架构 | 长期运行稳定、上下文隔离 | 架构复杂、开发成本高 | 长周期复杂任务 |

---