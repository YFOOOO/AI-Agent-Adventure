# 智能旅行助手 - 技术实现文档 (docs.md)

## 1. 项目简介
本项目旨在通过 Python 从零构建一个基于 ReAct 范式的智能旅行助手。该智能体能够根据用户指令，自主规划任务，调用天气查询和景点搜索工具，最终给出建议。

本项目采用 **"Core-Logic Separation" (基建与业务分离)** 架构，复用了通用的 Agent 基础设施。

## 2. 工程结构

```text
agent/
├── core/                   # [通用基建] 统一模型客户端与UI工具
│   ├── llm_client.py       
│   ├── ui_utils.py         
│   └── safe_parsing.py     
├── .env                    # [配置] API Key 配置
├── agent_logic.py          # [业务核心] 定义 Prompt 和特定工具函数
└── travel_agent_demo.ipynb # [入口] 流程编排与交互调试
```

## 3. 环境准备

### 依赖安装
需要安装 `requests` (HTTP请求), `tavily-python` (搜索工具), `openai` (LLM SDK) 以及 `python-dotenv` (环境变量管理)。

```bash
pip install requests tavily-python openai python-dotenv
```

### API Key 配置
请在 `agent/.env` 文件中配置以下 Key：

```env
# 基础模型服务
ZHIPU_API_KEY=...
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# 工具服务
TAVILY_API_KEY=tvly-...
```

## 4. 核心组件

### 4.1 基础设施 (Core)
- **`llm_client.py`**: 提供 `get_response(model, prompt)` 统一接口，屏蔽底层 API 差异。
- **`ui_utils.py`**: 提供 `print_html(content)`，在 Notebook 中输出美观的卡片式 UI。

### 4.2 业务逻辑 (Logic)
- **工具函数**:
    - `get_weather(city)`: 调用 wttr.in 获取天气。
    - `get_attraction(city, weather)`: 调用 Tavily 搜索景点。
- **Prompt**: 定义了 ReAct 范式的 System Prompt。
