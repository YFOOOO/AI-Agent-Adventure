# Chart Generation Agent v2.0 (Refactored)

基于 **Core-Logic Separation** 架构重构的图表生成智能体。

## 📂 项目结构

```text
agent_refactor/
├── core/                   # [基建] 通用基础设施 (LLM Client, UI, Parsing)
├── agent_logic.py          # [业务] 核心逻辑 (Prompt, Tools)
├── chart_gen_v2.ipynb      # [入口] 流程编排 (Generate -> Execute -> Reflect)
└── coffee_sales.csv        # [数据] 示例数据
```

## 🚀 快速开始

1. **配置环境**:
   确保目录下有 `.env` 文件，并配置好 API Key：
   ```ini
   QWEN_API_KEY=...
   ZHIPU_API_KEY=...
   ```

2. **运行**:
   打开 `chart_gen_v2.ipynb`，运行所有单元格。

## ✨ 架构亮点

- **模块化**: 业务逻辑与底层调用完全解耦。
- **可视化**: 使用 `core.ui_utils` 实现全流程可视化调试。
- **可复用**: `core` 目录可直接复制到其他 Agent 项目中。
