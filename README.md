# AI Agent Adventure 🚀

> 一个系统化的 AI 智能体学习与实践工作空间，基于工程化驱动的开发方法论

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 📚 项目概述

本项目记录了从零开始构建生产级 AI 智能体的完整学习历程。不同于简单的脚本堆砌，本项目采用 **"工程化驱动 (Engineering-Driven)"** 的理念，将智能体开发拆解为设计、文档与实现三个标准化阶段。

### 🌟 核心特色

- **🏗️ Core-Logic 分离**：基础设施与业务逻辑完全解耦，拒绝面条式代码
- **📐 模式驱动开发**：沉淀 ReAct、Reflection 等通用设计模式
- **🔧 统一工具链**：LLM 客户端、UI 工具、鲁棒解析器开箱即用
- **📝 文档先行**：每个项目都包含完整的 `docs.md` 和 `spec.md`
- **🎨 交互式开发**：基于 Jupyter Notebook 的可视化调试环境

## 🗂️ 智能体案例

| 项目名称 | 核心模式 | 简介 | 路径 |
| :--- | :--- | :--- | :--- |
| **旅行智能助手** | **ReAct** | 理解自然语言，调用搜索与天气工具规划行程 | [`Datawhale Hello Agents/...`](Datawhale%20Hello%20Agents/repo/1.3%20动手体验/) |
| **数据可视化智能体** | **Reflection** | 自动生成代码绘图，并利用多模态模型进行视觉反思与优化 | [`Agentic AI/...`](Agentic%20AI（DeepLearning）/repo/M2_UGL_1/) |

## 📂 项目结构

```text
AI Agent Adventure/
├── Agentic AI（DeepLearning）/      # DeepLearning.AI 课程实践
│   ├── 实践日志/                    # 每日学习记录
│   └── repo/                        # 项目代码
│       └── M2_UGL_1/                # 图表生成智能体 (Reflection Pattern)
│           ├── agent/               # 第一版实现
│           └── agent_refactor/      # 重构版 (Core-Logic 分离)
│
├── Datawhale Hello Agents/          # Datawhale 开源教程实践
│   ├── 实践日志/                    # 学习笔记
│   └── repo/                        
│       └── 1.3 动手体验/            # 旅行智能助手 (ReAct Pattern)
│           ├── travel_agent_demo.ipynb
│           └── agent/               # 重构版实现
│
├── template/                        # 🌟 通用智能体脚手架
│   ├── core/                        # 可复用基础设施
│   │   ├── llm_client.py           # 统一 LLM 客户端 (支持多厂商)
│   │   ├── ui_utils.py             # Notebook UI 工具
│   │   └── safe_parsing.py         # 防御性解析工具
│   ├── patterns/                    # 设计模式库
│   │   ├── react.py                # ReAct 循环控制器
│   │   ├── reflection.py           # 反思模式骨架
│   │   └── prompt_templates.py     # Prompt 模板库
│   ├── notebooks/                   # 开发工作台
│   │   └── debug_workbench.ipynb   
│   └── config/                      
│       └── .env.example            # 环境变量模板
│
└── docs/                            # 📖 知识库
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 克隆仓库
git clone https://github.com/YFOOOO/AI-Agent-Adventure.git
cd AI-Agent-Adventure

# 配置环境变量 (支持 OpenAI, 阿里云, 智谱AI 等)
cp template/config/.env.example .env
# 编辑 .env 填入你的 API Keys
```

### 2. 创建新智能体

```bash
# 使用脚手架快速初始化
mkdir my_agent
cp -r template/core my_agent/
cp template/config/.env.example my_agent/.env

# 启动 Jupyter 开发环境
cd my_agent
jupyter notebook
```

## 🛠️ 基础设施

本项目提供了一套经过生产验证的基础设施（位于 `template/core`），旨在让开发者专注于 Agent 逻辑本身：

*   **统一 LLM 客户端**：透明代理模式，一行代码切换 OpenAI、通义千问、智谱 AI 等模型。
*   **可视化 UI 工具**：在 Notebook 中渲染美观的思维链（Thought-Action）卡片与多模态内容。
*   **鲁棒解析器**：防御性处理 LLM 的 JSON/Code 输出，提升系统稳定性。

## 🧪 工程化方法论

本项目采用三阶段开发流程：

1️⃣ **知识内化 (`docs.md`)**
记录技术依赖、API 配置、核心原理（如 ReAct 范式）

2️⃣ **架构设计 (`spec.md`)**
- System Prompt 定义
- Tools Interface 规范
- 数据流设计

3️⃣ **原型验证 (`.ipynb`)**
- 交互式开发
- 逐步验证工具调用
- 可视化 Agent 思考链

4️⃣ **架构重构 (v2.0)**
- 采用 Core-Logic 分离
- 提取可复用基础设施
- 标准化代码结构

## 📖 学习资源

*   [Datawhale - Hello Agents](https://datawhalechina.github.io/hello-agents/)
*   [DeepLearning.AI - Agentic AI](https://www.deeplearning.ai/short-courses/agentic-ai/)
*   [Microsoft - AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners)
*   [Hugging Face Agents Course](https://hf.co/learn/agents-course)

## 🔮 未来计划

- [ ] 实现 Planning Pattern (规划模式)
- [ ] Multi-Agent 协作系统
- [ ] 工具函数自动注册机制

## 📄 License

本项目采用 [MIT License](LICENSE) 开源协议。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎通过 [GitHub Issues](https://github.com/YFOOOO/AI-Agent-Adventure/issues) 联系我。

---

⭐ 如果这个项目对你有帮助，欢迎 Star！

**Happy Agent Building!** 🎉
