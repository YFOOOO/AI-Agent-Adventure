# Chart Generation Agent Specification

## 1. System Prompts & Role Definitions

### 1.1 Chart Generator (V1)
负责根据用户指令和数据结构生成初始的 Matplotlib 绘图代码。

**Role:** Data Visualization Expert
**Input:** 
- User Instruction
- Data Schema (Columns & Types)
**Output Format:** Python code wrapped in `<execute_python>` tags.

**Prompt Template:**
```text
You are a data visualization expert.

Return your answer *strictly* in this format:

<execute_python>
# valid python code here
</execute_python>

Do not add explanations, only the tags and the code.

The code should create a visualization from a DataFrame 'df' with these columns:
[Column List...]

User instruction: {instruction}

Requirements for the code:
1. Assume the DataFrame is already loaded as 'df'.
2. Use matplotlib for plotting.
3. Add clear title, axis labels, and legend if needed.
4. Save the figure as '{out_path_v1}' with dpi=300.
5. Do not call plt.show().
6. Close all plots with plt.close().
7. Add all necessary import python statements

Return ONLY the code wrapped in <execute_python> tags.
```

### 1.2 Chart Reflector & Refiner (V2)
负责审查 V1 图表（图片）和代码，提供改进意见并生成修正后的代码。

**Role:** Data Visualization Expert (Critic & Refiner)
**Model Requirement:** Vision-Language Model (VLM) capable of image analysis (e.g., `glm-4v`, `qwen-vl-plus`).
**Input:** 
- Chart Image (V1)
- Original Code (V1)
- User Instruction
**Output Format:** JSON object with feedback + Python code wrapped in `<execute_python>` tags.

**Prompt Template:**
```text
You are a data visualization expert.
Your task: critique the attached chart and the original code against the given instruction,
then return improved matplotlib code.

Original code (for context):
{code_v1}

OUTPUT FORMAT (STRICT!):
1) First line: a valid JSON object with ONLY the "feedback" field.
Example: {{"feedback": "The legend is unclear and the axis labels overlap."}}

2) After a newline, output ONLY the refined Python code wrapped in:
<execute_python>
...
</execute_python>

3) Import all necessary libraries in the code. Don't assume any imports from the original code.

HARD CONSTRAINTS:
- Do NOT include Markdown, backticks, or any extra prose outside the two parts above.
- Use pandas/matplotlib only (no seaborn).
- Assume df already exists; do not read from files.
- Save to '{out_path_v2}' with dpi=300.
- Always call plt.close() at the end (no plt.show()).
- Include all necessary import statements.

Schema (columns available in df):
[Column List...]

Instruction:
{instruction}
```

## 2. Tools & Functions Interface

### 2.1 `generate_chart_code` ✅ 已实现
生成初始图表代码。

**状态**: ✅ 已在 `utils.py` 中完整实现

**函数签名**:
```python
def generate_chart_code(
    instruction: str,
    schema_text: str,
    model: str,
    out_path: str,
    temperature: float = 0
) -> str
```

**Args**:
- `instruction` (str): 用户绘图指令
- `schema_text` (str): 数据 Schema（通过 `make_schema_text()` 生成）
- `model` (str): 使用的模型名称（如 "qwen3-max", "gpt-4o"）
- `out_path` (str): 图片保存路径
- `temperature` (float): 温度参数，默认 0（更确定性）

**Returns**: 
- `str`: 包含 `<execute_python>` 标签的完整回复

**特性**:
- 内置优化的 Prompt 模板
- 自动通过 `get_response()` 路由到正确的 API 客户端
- 支持所有兼容 OpenAI API 的模型

**使用示例**:
```python
response = generate_chart_code(
    instruction="Create a bar chart of sales by coffee type",
    schema_text=make_schema_text(df),
    model="qwen3-max",
    out_path="chart_v1.png"
)
```

### 2.2 `reflect_on_image_and_regenerate` ✅ 已实现
基于图片反思并重新生成代码。

**状态**: ✅ 已在 `utils.py` 中完整实现

**函数签名**:
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

**Args**:
- `chart_path` (str): V1 图片路径
- `instruction` (str): 原始用户指令
- `schema_text` (str): 数据 Schema
- `model_name` (str): 用于反思的模型名称（需支持多模态，如 "glm-4v", "qwen-vl-plus"）
- `out_path_v2` (str): V2 图片保存路径
- `code_v1` (str): 原始代码上下文

**Returns**: 
- `tuple[str, str]`: (feedback, refined_code)
  - `feedback`: 反思反馈文本
  - `refined_code`: 改进后的代码

**特性**:
- 自动编码图片为 Base64
- 智能识别 Claude 或 OpenAI 兼容 API
- 鲁棒的 JSON 解析（容错处理）
- 自动清洗和规范化代码格式

**使用示例**:
```python
feedback, improved_code = reflect_on_image_and_regenerate(
    chart_path="chart_v1.png",
    instruction="Create a bar chart...",
    schema_text=schema,
    model_name="glm-4v",
    out_path_v2="chart_v2.png",
    code_v1=original_code
)
```

### 2.3 `run_workflow` ✅ 已实现（增强版）
端到端执行完整的 Reflection Pattern 工作流。

**状态**: ✅ 已在 `utils.py` 中完整实现（超出规范要求）

**函数签名**:
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

**Args**:
- `dataset_path` (str): CSV 数据文件路径
- `user_instruction` (str): 用户指令
- `generation_model` (str): 生成模型（如 "qwen3-max"）
- `reflection_model` (str): 反思模型（如 "glm-4v"）
- `image_basename` (str): 图片文件名前缀，默认 "chart"
- `verbose` (bool): 是否显示详细输出，默认 True

**Returns**: 
- `dict`: 包含所有产物的字典
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

**工作流程（6 步）**:
1. 加载数据并生成 Schema
2. 生成初始代码 (V1)
3. 执行代码并生成图表 V1
4. 多模态反思
5. 生成改进代码 (V2)
6. 执行代码并生成图表 V2（含对比展示）

**高级特性**:
- ✅ 每步都有完整的错误捕获
- ✅ 详细的日志输出（可通过 verbose 控制）
- ✅ 自动化的 V1/V2 对比展示
- ✅ 结构化的返回值便于后续处理
- ✅ 失败时返回错误列表和部分成功的结果

**使用示例**:
```python
result = run_workflow(
    dataset_path="coffee_sales.csv",
    user_instruction="Create a bar chart of top 5 coffee types",
    generation_model="qwen3-max",
    reflection_model="glm-4v",
    verbose=True
)

if result["success"]:
    print(f"✅ 生成的图表: {result['chart_v2']}")
else:
    print(f"❌ 错误: {result['errors']}")
```

## 3. Utility Functions (`utils.py`)

本节列出 `utils.py` 中的所有核心函数。函数按功能分为以下几类：

### 3.0 环境与配置
- ✅ `load_dotenv()`: 加载 .env 文件中的环境变量
- ✅ 客户端初始化: `openai_client`, `anthropic_client`, `qwen_client`, `zhipu_client`, `deepseek_client`, `moonshot_client`

### 3.1 API 客户端管理

#### `get_client_for_model(model: str) -> OpenAI | None` ✅
根据模型名称返回对应的 API 客户端。
- **逻辑:**
  - `"qwen"` → `qwen_client`
  - `"glm"` → `zhipu_client`
  - `"deepseek"` → `deepseek_client`
  - `"kimi"` 或 `"moonshot"` → `moonshot_client`
  - 其他 → `openai_client`
- **容错:** 若对应 API Key 缺失，返回 `None`。

#### `get_response(model: str, prompt: str, temperature: float = 0) -> str` ✅
统一的文本生成接口。
- **支持模型:**
  - Anthropic: `claude-*` 系列
  - OpenAI: `gpt-*`, `o1-*`, `o3-*` 系列
  - Qwen: `qwen*` 系列 (通过兼容接口)
  - Zhipu: `glm-*` 系列 (通过兼容接口)
  - DeepSeek: `deepseek-*` 系列
  - Moonshot: `moonshot-*` 系列 (也支持 `kimi` 关键词)
- **返回:** 模型生成的文本内容。

### 3.2 多模态图像调用

#### `encode_image_b64(path: str) -> tuple[str, str]` ✅
将图片文件编码为 Base64。
- **返回:** `(media_type, base64_string)`
- **MIME 类型:** 自动通过 `mimetypes.guess_type()` 推断。

#### `image_anthropic_call(model_name: str, prompt: str, media_type: str, b64: str) -> str` ✅
调用 Anthropic 的多模态 API。
- **特性:**
  - 添加 System Prompt 强制返回 JSON 格式
  - 拼接所有 `text` 类型的 content blocks
- **返回:** 模型的完整文本响应。

#### `image_openai_call(model_name: str, prompt: str, media_type: str, b64: str) -> str` ✅
调用 OpenAI 兼容的多模态 API (支持 Qwen-VL, GLM-4V 等)。
- **输入:** Base64 编码的图片 (`data:image/png;base64,...`)
- **返回:** 模型的文本响应。

### 3.3 数据处理

#### `load_and_prepare_data(csv_path: str) -> pd.DataFrame` ✅
加载 CSV 并自动扩展日期列。
- **自动派生:**
  - `quarter`: 季度 (1-4)
  - `month`: 月份 (1-12)
  - `year`: 年份
- **容错:** 使用 `errors="coerce"` 处理无效日期。

#### `make_schema_text(df: pd.DataFrame) -> str` ✅
生成 LLM 可读的数据 Schema。
- **格式:** `- {column_name}: {dtype}`
- **用途:** 嵌入 Prompt 中帮助模型理解数据结构。

### 3.4 代码处理

#### `ensure_execute_python_tags(text: str) -> str` ✅
规范化 LLM 生成的代码。
- **处理步骤:**
  1. 移除 Markdown code fences (` ```python ... ``` `)
  2. 若缺失 `<execute_python>` 标签则自动添加
- **目的:** 统一代码格式，便于正则提取和执行。

#### `extract_code_from_tags(text: str) -> Optional[str]` ✅
从 `<execute_python>` 标签中提取代码。
- **返回:** 提取的代码，若未找到则返回 `None`。

### 3.5 可视化输出

#### `print_html(content: Any, title: str | None = None, is_image: bool = False)` ✅
在 Jupyter Notebook 中美观地显示内容。

**参数:**
- `content`: 要显示的内容
  - `str` + `is_image=True`: 图片路径 (Base64 嵌入)
  - `pd.DataFrame/Series`: HTML 表格
  - 其他: 代码块 (`<pre><code>`)
- `title`: 卡片标题 (可选)
- `is_image`: 是否为图片路径

**样式特性:**
- 渐变边框卡片设计
- CSS 作用域隔离 (`.pretty-card` 前缀)
- 响应式布局

**使用场景:**
- 展示 Agent 生成的代码
- 显示中间产物图表
- 输出反思反馈
- 预览数据表

### 3.6 调试辅助

#### `check_api_keys()` ✅
检查已配置的 API Keys。
- **用途:** 调试环境配置问题
- **输出:** 显示各供应商 API Key 的配置状态（✅/❌）

### 3.7 高层工作流 API（新增）

#### `generate_chart_code()` ✅
详见 [2.1 节](#21-generate_chart_code--已实现)

#### `reflect_on_image_and_regenerate()` ✅
详见 [2.2 节](#22-reflect_on_image_and_regenerate--已实现)

#### `run_workflow()` ✅
详见 [2.3 节](#23-run_workflow--已实现增强版)

---
*规范更新日期: 2025-12-14 (v2.0 - 所有函数已实现并测试通过)*
