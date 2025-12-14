# Chart Generation Agent Documentation

## 1. 项目概述
本项目实现了一个基于 **Reflection Pattern (反思模式)** 的数据可视化智能体。该智能体能够根据用户指令生成初始图表代码，执行并生成图表，然后利用多模态大模型对生成的图表进行视觉反思与代码审查，最终生成更完善的图表。

## 2. 核心依赖
- **Python Libraries:**
  - `pandas`: 数据处理与分析
  - `matplotlib`: 数据可视化绘图
  - `openai`: OpenAI API 客户端
  - `anthropic`: Anthropic Claude API 客户端
  - `python-dotenv`: 环境变量管理
  - `Pillow` (PIL): 图像处理
  - `re`, `json`, `base64`: 基础工具库

## 3. 环境变量配置

为了安全地管理 API Key，推荐使用环境变量。请在项目根目录下创建一个名为 `.env` 的文件，填入你的 API Key。

本项目支持 OpenAI 原生接口及兼容接口（如通义千问、智谱AI），配置示例如下：

```bash
# OpenAI (Optional)
OPENAI_API_KEY=sk-...

# Anthropic (Optional)
ANTHROPIC_API_KEY=sk-...

# Qwen (通义千问 - qwen3-max, qwen-vl-plus)
QWEN_API_KEY=sk-...
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# ZhipuAI (智谱AI - glm-4, glm-4v)
ZHIPU_API_KEY=...
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# DeepSeek (Optional)
DEEPSEEK_API_KEY=...
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Moonshot (月之暗面 - moonshot-v1-*, 也支持 kimi 关键词)
MOONSHOT_API_KEY=...
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
```

在代码中，使用 `python-dotenv` 加载：
```python
import os
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件
```

## 4. 关键技术原理

### 4.1 Reflection Pattern (反思模式)
智能体工作流遵循 "Generate -> Execute -> Reflect -> Regenerate" 的闭环：
1. **Generate (生成)**: 根据用户指令和数据 Schema 生成初始绘图代码 (V1)。通常使用代码生成能力强的模型（如 `qwen3-max`）。
2. **Execute (执行)**: 提取并执行代码，生成第一版图表图片 (V1)。
3. **Reflect (反思)**: 将 V1 图表图片与原始代码回传给多模态模型（如 `glm-4v` 或 `qwen-vl-plus`），要求其从视觉美观度、数据准确性等方面进行批评 (Critique)。
4. **Regenerate (改进)**: 根据反思意见生成改进后的代码 (V2) 并再次执行。

### 4.2 Code Execution (代码执行沙盒)
- **Tag-based Isolation**: 模型生成的代码被包裹在 `<execute_python>` 标签中，便于正则提取。
- **Execution Context**: 使用 Python 的 `exec()` 函数在预定义的全局上下文 (如包含 `df` 变量) 中运行代码。

### 4.3 Multi-modal Feedback (多模态反馈)
- 利用具备视觉能力的模型 (如 GPT-4o, Claude 3.5 Sonnet, GLM-4V, Qwen-VL-Plus) 直接"看"图表，发现标签重叠、颜色不协调等仅靠代码难以发现的问题。
- 通过 `image_anthropic_call` 和 `image_openai_call` 函数统一处理不同供应商的多模态 API 调用。

### 4.4 简易沙盒输出机制 (Simple Sandbox UI)
**核心设计亮点**: `print_html` 函数通过 HTML/CSS 注入，将 Notebook 输出转化为美观的卡片式 UI。

**关键特性:**
1. **多模态智能渲染**:
   - `DataFrame/Series`: 自动转换为 HTML 表格（`.to_html()`）
   - 图片路径: Base64 编码后嵌入 `<img>` 标签
   - 代码/文本: 包裹在 `<pre><code>` 中，保留格式

2. **样式隔离** (CSS Scoping):
   ```python
   .pretty-card pre, .pretty-card code { ... }  # 仅影响卡片内部
   ```
   使用 `.pretty-card` 前缀避免污染 Notebook 全局样式。

3. **视觉层级**:
   - 卡片容器 (`.pretty-card`): 渐变边框 + 阴影
   - 标题 (`.pretty-title`): 加粗，区分不同 Agent 步骤
   - 示例: "Step 1: Generating Code...", "Step 3: Reflecting..."

**代码示例:**
```python
from utils import print_html

# 显示代码
print_html(code_v1, title="📝 Generated Code (V1)")

# 显示图片
print_html("chart_v1.png", title="📊 Chart V1", is_image=True)

# 显示数据
print_html(df.head(), title="📋 Data Preview")
```

**可观测性提升**: 这种设计使得在 Notebook 中进行 Agent 开发时，能够清晰地追踪每个步骤的输入输出，极大增强了调试效率和用户体验。

### 4.5 统一 API 客户端封装
**设计模式**: 透明代理 (Transparent Proxy)

**核心函数:**
```python
def get_client_for_model(model: str):
    if "qwen" in model.lower():
        return qwen_client
    elif "glm" in model.lower():
        return zhipu_client
    else:
        return openai_client
```

**优势:**
- **供应商无关**: 上层业务逻辑无需关心使用的是 OpenAI、Qwen 还是 GLM
- **容错初始化**: 使用 `if api_key else None` 防止因缺少某个厂商 Key 而导致导入失败
- **统一接口**: `get_response()` 和多模态调用函数自动路由到正确的客户端

### 4.6 鲁棒的数据与代码处理
1. **Schema 自动生成** (`make_schema_text`):
   - 将 DataFrame 列名和类型转换为 LLM 可读的 Prompt
   - 这是 Data Agent 的标准范式

2. **代码格式清洗** (`ensure_execute_python_tags`):
   - 处理 LLM 输出中的格式噪音（如 Markdown code fences）
   - 确保代码被正确包裹在 `<execute_python>` 标签中
   - 提高 `exec()` 执行的成功率

3. **日期列自动扩展** (`load_and_prepare_data`):
   - 自动从 `date` 列派生 `quarter`, `month`, `year` 列
   - 便于时间序列分析和可视化

### 4.7 高层工作流 API（Production-Ready）
为了提升易用性，项目提供了三个高层封装函数，实现了从手动拼装到一键运行的跨越。

#### `generate_chart_code()`
封装了完整的代码生成 Prompt 和 API 调用流程。

**函数签名:**
```python
def generate_chart_code(
    instruction: str,
    schema_text: str,
    model: str,
    out_path: str,
    temperature: float = 0
) -> str
```

**核心特性:**
- 内置优化过的 Prompt 模板
- 支持温度参数调节创造性
- 返回规范化的代码响应（包含 `<execute_python>` 标签）

#### `reflect_on_image_and_regenerate()`
封装了多模态反思的完整流程。

**函数签名:**
```python
def reflect_on_image_and_regenerate(
    chart_path: str,
    instruction: str,
    schema_text: str,
    model_name: str,
    out_path_v2: str,
    code_v1: str
) -> tuple[str, str]
```

**核心特性:**
- 自动处理图片编码（Base64）
- 智能路由到 Claude 或 OpenAI 兼容 API
- 鲁棒的 JSON 解析（容错处理）
- 返回结构化的反馈和改进代码

#### `run_workflow()` - 端到端工作流
**这是项目的核心函数**，实现了完整的 Reflection Pattern。

**函数签名:**
```python
def run_workflow(
    dataset_path: str,
    user_instruction: str,
    generation_model: str,
    reflection_model: str,
    image_basename: str = "chart",
    verbose: bool = True
) -> dict
```

**工作流程（6 步）:**
1. **加载数据**: 自动扩展日期列，生成 Schema
2. **生成代码 V1**: 调用生成模型创建初始代码
3. **执行并生成图表 V1**: 在安全上下文中执行代码
4. **多模态反思**: VLM 审查图表并提供改进建议
5. **生成代码 V2**: 根据反馈生成改进代码
6. **执行并生成图表 V2**: 执行改进代码并对比展示

**返回值结构:**
```python
{
    "success": bool,              # 是否成功完成
    "df": pd.DataFrame,           # 加载的数据
    "schema_text": str,           # 数据 Schema
    "code_v1": str,               # 初始代码
    "chart_v1": str,              # V1 图片路径
    "feedback": str,              # 反思反馈
    "code_v2": str,               # 改进代码
    "chart_v2": str,              # V2 图片路径
    "errors": List[str]           # 错误信息列表
}
```

**高级特性:**
- ✅ 完整的错误捕获和恢复机制
- ✅ 每步都有详细日志输出（可通过 `verbose` 控制）
- ✅ 自动化的 V1/V2 对比展示（HTML 格式）
- ✅ 结构化的返回值便于后续处理

**使用示例:**
```python
from utils import run_workflow

result = run_workflow(
    dataset_path="coffee_sales.csv",
    user_instruction="Create a bar chart of top 5 coffee types by sales",
    generation_model="qwen3-max",
    reflection_model="glm-4v",
    verbose=True
)

if result["success"]:
    print(f"✅ 成功生成图表: {result['chart_v2']}")
else:
    print(f"❌ 失败: {result['errors']}")
```

## 5. 最佳实践与设计理念

### 5.1 三层 API 架构
项目采用分层设计，适配不同的使用场景：

**第 1 层：底层工具函数**
- `get_response()`, `encode_image_b64()`, `extract_code_from_tags()` 等
- 适合：需要完全自定义流程的高级用户
- 特点：最大灵活性，需要手动管理数据流

**第 2 层：中层封装函数**
- `generate_chart_code()`, `reflect_on_image_and_regenerate()`
- 适合：需要在某些步骤插入自定义逻辑的开发者
- 特点：平衡灵活性和易用性

**第 3 层：高层工作流函数**
- `run_workflow()`
- 适合：快速验证想法、批量处理、生产环境
- 特点：一行代码完成全流程，内置错误处理

### 5.2 UI 即调试
不要只打印纯文本日志。在 Notebook 中投入少量精力编写 HTML/CSS 渲染函数，能让调试过程变得赏心悦目，更容易发现逻辑漏洞。

### 5.3 防御性编程
在 `utils` 层处理掉大部分脏数据（如格式错误的 JSON、多余的空格），让上层 Agent 逻辑保持干净。

### 5.4 配置与代码分离
坚持使用 `.env` 管理敏感信息，并在 `utils` 中集中处理加载逻辑。

## 6. 快速开始

### 方式 1：逐步学习（推荐初学者）
打开 `chart_generation_demo.ipynb`，从"步骤 0"开始，逐个单元格执行，理解每个环节。

### 方式 2：一键运行（推荐快速验证）
```python
from utils import run_workflow

result = run_workflow(
    dataset_path="coffee_sales.csv",
    user_instruction="你的可视化需求",
    generation_model="qwen3-max",
    reflection_model="glm-4v"
)
```

### 方式 3：灵活定制（推荐高级用户）
```python
from utils import generate_chart_code, reflect_on_image_and_regenerate

# 自定义中间步骤
code = generate_chart_code(...)
# 插入你的自定义逻辑
feedback, improved = reflect_on_image_and_regenerate(...)
```

## 7. 支持的模型

### 代码生成模型（推荐）
- **qwen3-max** ⭐ - 通义千问（代码能力强，推荐）
- **gpt-4o** - OpenAI GPT-4o（综合能力强）
- **deepseek-chat** - DeepSeek（开源替代）
- **glm-4** - 智谱 GLM-4（中文友好）
- **moonshot-v1-32k** - Moonshot（长上下文）

### 多模态反思模型（推荐）
- **glm-4v** ⭐ - 智谱 GLM-4V（中文友好，推荐）
- **qwen-vl-plus** - 通义千问 VL Plus（视觉能力强）
- **gpt-4o** - OpenAI GPT-4o（多模态先驱）
- **claude-3-5-sonnet-20241022** - Anthropic Claude（严谨）

---
*文档更新日期: 2025-12-14 (v2.0 - 添加工作流函数说明)*
