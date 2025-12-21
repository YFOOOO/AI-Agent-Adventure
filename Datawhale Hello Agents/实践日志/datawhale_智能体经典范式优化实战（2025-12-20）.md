# 学习日志：Datawhale Hello Agents - 智能体经典范式优化实战

**日期**: 2025-12-20
**来源**: [Datawhale Hello Agents - 第四章 智能体经典范式构建](https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/%E7%AC%AC%E5%9B%9B%E7%AB%A0%20%E6%99%BA%E8%83%BD%E4%BD%93%E7%BB%8F%E5%85%B8%E8%8C%83%E5%BC%8F%E6%9E%84%E5%BB%BA.md)

## 1. 项目概述
今天的实战聚焦于 **ReAct (Reasoning and Acting)** 智能体范式的工程化优化。在初步掌握 ReAct 原理的基础上，我们将原本脆弱的“正则表达式解析”方案升级为更稳健的 **“结构化 JSON 输出”** 方案，并引入了可视化组件来增强智能体思考过程的可观测性。

## 2. 核心技术点
- **结构化输出 (Structured Output)**: 
    - 摒弃了基于 Regex 的文本匹配（如 `Action: Search[...]`），转而强制 LLM 输出标准的 JSON 格式。
    - 优势：极大降低了因模型输出格式微小差异（如空格、标点）导致的解析失败率，且天然支持复杂的工具参数传递。
- **Prompt Engineering**: 
    - 设计了 `REACT_JSON_PROMPT_TEMPLATE`，在 System Prompt 中通过 Few-Shot 或明确指令限制模型只能输出包含 `thought` 和 `action` 字段的 JSON 对象。
- **鲁棒性解析策略**: 
    - 实现了 `_parse_json_output` 方法，能够自动处理 LLM 常见的输出噪音（如被 \`\`\`json 代码块包裹的内容），利用 `json.loads` 进行安全解析。
- **交互可视化**: 
    - 使用 HTML/CSS (`ui_utils.print_html`) 将智能体的“内心独白”、“工具调用”和“观察结果”渲染为不同颜色的卡片，显著提升了调试体验。

## 3. 实践过程 (Engineering-Driven)

### 3.1 环境与工具准备
- 复用了 `HelloAgentsLLM` 客户端与 `ToolExecutor` 执行器。
- 注册了 `Search` 工具，模拟（或实际调用）搜索引擎以获取外部信息。

### 3.2 核心代码重构 (`ReActAgentJSON`)
在 `优化-demo.ipynb` 中，我完成了一个名为 `ReActAgentJSON` 的新类：

1.  **Prompt 设计**:
    ```python
    # 强制模型输出 JSON
    REACT_JSON_PROMPT_TEMPLATE = """
    ...
    - 请**严格**按照以下 JSON 格式输出你的思考和行动...
    {{
        "thought": "你的思考过程...",
        "action": {{ "name": "工具名", "args": {{ ... }} }}
    }}
    ...
    """
    ```

2.  **解析逻辑升级**:
    - 增加了对 Markdown 代码块的清洗逻辑。
    - 增加了 `try-except` 块捕获 `json.JSONDecodeError`，防止程序因单次生成错误而崩溃。

3.  **主循环优化**:
    - 在 `run` 方法中，将 `Thought` -> `Action` -> `Observation` 的每一步都通过富文本形式打印。
    - 增加了 `Finish` 动作的检测，使智能体能够自主判断何时结束任务并输出最终答案。

### 3.3 交互验证
- **测试用例**: "华为最新的手机是哪一款？它的主要卖点是什么？"
- **执行流程**:
    1.  **Step 1 Thought**: 模型分析需要查询华为最新手机信息。
    2.  **Step 1 Action**: 生成 JSON `{"name": "Search", "args": {"query": "华为最新手机"}}`。
    3.  **Step 1 Observation**: 获取搜索结果（如 Pura 70 系列等）。
    4.  **Step 2 Thought**: 模型根据搜索结果提炼卖点。
    5.  **Final Answer**: 输出最终总结。
- **结果**: 智能体成功完成任务，且中间过程清晰可见，验证了 JSON 方案的稳定性。

### 3.4 工具调试与鲁棒性验证 (Calculator Tool Debugging)
在完成基础框架后，我新增了一个 `Calculator` 工具来测试 Agent 的数值计算能力，并记录了以下调试经验：

1.  **动态调试技巧**:
    - 在 Jupyter Notebook 中调试外部模块（如 `tools.py`）时，直接修改代码不会立即生效。必须使用 `importlib.reload()` 重新加载模块，避免了频繁重启 Kernel 的低效操作。

2.  **作用域陷阱**:
    - 在实现 `calculator` 工具时遇到了 `name 'math' is not defined` 错误。原因是 `eval()` 函数在受限环境中执行，无法自动获取外部作用域的模块。
    - **修复**: 在函数内部显式 `import math` 并将其作为 `globals` 参数传递给 `eval`。

3.  **鲁棒性测试 (Robustness)**:
    - **测试用例**: `agent.run("搜索 (123 + 456) × 789 / 12 的结果，结果保留两位小数")`
    - **挑战**:
        - 动词误导（"搜索" vs 实际需要的 "计算"）。
        - 参数噪音（"保留两位小数" 不在工具签名中）。
    - **结果**: Agent 展现了极强的意图识别能力：
        - 忽略了 "搜索" 字面指令，基于任务本质选择了 `Calculator` 工具。
        - 自动过滤了无效参数，仅传递了合法的 `expression` 参数。
        - 这证明了 ReAct 范式配合 JSON 输出在处理模糊指令时的稳定性。

## 4. 学习心得
- **JSON 是 AI 的“通用语”**: 相比于自然语言或自定义的正则规则，JSON 是连接 LLM 与 传统软件工程（函数调用）最可靠的桥梁。
- **可观测性即生产力**: 在 Agent 开发中，能够直观看到模型“想了什么”和“看到了什么”是调试幻觉和逻辑错误的关键。
- **容错设计**: 即使使用了 JSON Prompt，模型仍可能偶尔犯错（如生成不合法的 JSON）。在工程实现中，必须做好解析失败的兜底处理（如提示模型重试或记录错误日志）。

## 5. 下一步计划
- 探索 **Plan-and-Solve** 范式，解决 ReAct 容易陷入局部最优的问题。
- 尝试将今天的优化方案应用到更复杂的工具链中（如包含代码解释器）。
- 对比不同参数规模的模型（如 7B vs 70B）在遵循 JSON 指令上的能力差异。
