# 智能旅行助手 (Travel Agent) - v2.0 Refactored

基于 **Core-Logic Separation (基建与业务分离)** 架构重构的 ReAct 智能体。

## 📂 项目结构
- **core/**: 通用基础设施（LLM 客户端、UI 工具、安全解析），可直接复用到其他项目。
- **agent_logic.py**: 业务核心，包含 System Prompt 和工具函数（天气查询、景点搜索）。
- **travel_agent_demo.ipynb**: 交互式运行入口。
- **.env**: 配置文件（需自行创建）。

## 🚀 快速开始

1. **环境配置**:
   复制 `.env.example` 为 `.env` 并填入 API Key：
   ```ini
   ZHIPU_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   ```

2. **安装依赖**:
   ```bash
   pip install requests tavily-python openai python-dotenv pandas matplotlib
   ```

3. **运行**:
   打开 `travel_agent_demo.ipynb`，依次运行单元格即可体验。

## 🧠 架构亮点
- **解耦**: 业务逻辑与底层调用完全分离，修改 Prompt 不需要触碰 LLM 调用代码。
- **可视化**: 集成卡片式 UI，清晰展示 Thought -> Action -> Observation 全过程。