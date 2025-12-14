"""
Chart Generation Agent - Core Utility Functions

本模块提供了 Chart Generation Agent 的核心辅助功能：
- 统一的 API 客户端管理（支持 OpenAI、Qwen、GLM、DeepSeek、Kimi）
- 数据加载与预处理
- 多模态图像调用
- 代码执行与格式化
- Jupyter Notebook 美化输出

Design Philosophy:
1. 透明代理 (Transparent Proxy): 统一接口，屏蔽不同供应商差异
2. 防御性编程: 鲁棒的错误处理和格式清洗
3. 可观测性: 美观的输出增强调试体验
"""

# === Standard Library ===
import os
import re
import json
import base64
import mimetypes
from pathlib import Path
from typing import Any, Tuple, Optional

# === Third-Party ===
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from IPython.display import HTML, display
from html import escape

# ============================================================================
# 1. 环境变量与客户端初始化
# ============================================================================

load_dotenv()

# API Keys
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
qwen_api_key = os.getenv("QWEN_API_KEY")
zhipu_api_key = os.getenv("ZHIPU_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
moonshot_api_key = os.getenv("MOONSHOT_API_KEY")

# Base URLs
qwen_base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
zhipu_base_url = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
moonshot_base_url = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")

# 客户端初始化（容错设计：缺失 Key 时返回 None）
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
qwen_client = OpenAI(api_key=qwen_api_key, base_url=qwen_base_url) if qwen_api_key else None
zhipu_client = OpenAI(api_key=zhipu_api_key, base_url=zhipu_base_url) if zhipu_api_key else None
deepseek_client = OpenAI(api_key=deepseek_api_key, base_url=deepseek_base_url) if deepseek_api_key else None
kimi_client = OpenAI(api_key=moonshot_api_key, base_url=moonshot_base_url) if moonshot_api_key else None


# ============================================================================
# 2. API 客户端管理（透明代理模式）
# ============================================================================

def get_client_for_model(model: str) -> Optional[OpenAI]:
    """
    根据模型名称返回对应的 API 客户端（透明代理）
    
    Args:
        model: 模型名称（如 "qwen3-max", "glm-4v", "deepseek-chat"）
    
    Returns:
        对应的 OpenAI 兼容客户端，若未配置则返回 None
    """
    model_lower = model.lower()
    
    if "qwen" in model_lower:
        return qwen_client
    elif "glm" in model_lower:
        return zhipu_client
    elif "deepseek" in model_lower:
        return deepseek_client
    elif "kimi" in model_lower or "moonshot" in model_lower:
        return kimi_client
    else:
        return openai_client


def get_response(model: str, prompt: str, temperature: float = 0) -> str:
    """
    统一的文本生成接口
    
    支持模型：
    - Anthropic: claude-* 系列
    - OpenAI: gpt-*, o1-*, o3-* 系列
    - Qwen: qwen* 系列
    - Zhipu: glm-* 系列
    - DeepSeek: deepseek-* 系列
    - Moonshot: moonshot-*, kimi 系列
    
    Args:
        model: 模型名称
        prompt: 用户提示词
        temperature: 温度参数（0-1）
    
    Returns:
        模型生成的文本内容
    """
    if "claude" in model.lower() or "anthropic" in model.lower():
        # Anthropic Claude API
        if not anthropic_client:
            return f"Error: Anthropic client not initialized. Check ANTHROPIC_API_KEY."
        
        message = anthropic_client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=temperature,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
        return message.content[0].text
    
    else:
        # OpenAI 兼容 API（支持所有其他模型）
        client = get_client_for_model(model)
        if not client:
            return f"Error: Client for model '{model}' not initialized. Check API keys in .env file."
        
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


# ============================================================================
# 3. 多模态图像调用
# ============================================================================

def encode_image_b64(path: str) -> Tuple[str, str]:
    """
    将图片文件编码为 Base64
    
    Args:
        path: 图片文件路径
    
    Returns:
        (media_type, base64_string)
    """
    mime, _ = mimetypes.guess_type(path)
    media_type = mime or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return media_type, b64


def image_anthropic_call(model_name: str, prompt: str, media_type: str, b64: str) -> str:
    """
    调用 Anthropic 的多模态 API
    
    特性：
    - 添加 System Prompt 强制返回 JSON 格式
    - 拼接所有 text 类型的 content blocks
    
    Args:
        model_name: 模型名称（如 "claude-3-5-sonnet-20241022"）
        prompt: 文本提示词
        media_type: 图片 MIME 类型
        b64: 图片 Base64 编码
    
    Returns:
        模型的完整文本响应
    """
    if not anthropic_client:
        return "Error: Anthropic client not initialized."
    
    msg = anthropic_client.messages.create(
        model=model_name,
        max_tokens=2000,
        temperature=0,
        system=(
            "You are a careful assistant. Respond with a single valid JSON object only. "
            "Do not include markdown, code fences, or commentary outside JSON."
        ),
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            ],
        }],
    )
    
    # 拼接所有文本块
    parts = []
    for block in (msg.content or []):
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts).strip()


def image_openai_call(model_name: str, prompt: str, media_type: str, b64: str) -> str:
    """
    调用 OpenAI 兼容的多模态 API
    
    支持模型：
    - GPT-4o, GPT-4V (OpenAI)
    - Qwen3-VL-Plus (Qwen)
    - GLM-4V (智谱AI)
    
    Args:
        model_name: 模型名称
        prompt: 文本提示词
        media_type: 图片 MIME 类型
        b64: 图片 Base64 编码
    
    Returns:
        模型的文本响应
    """
    client = get_client_for_model(model_name)
    if not client:
        return f"Error: Client for model '{model_name}' not initialized."
    
    data_url = f"data:{media_type};base64,{b64}"
    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    )
    content = resp.choices[0].message.content
    return (content or "").strip()


# ============================================================================
# 4. 数据处理
# ============================================================================

def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """
    加载 CSV 并自动扩展日期列
    
    自动派生字段：
    - quarter: 季度 (1-4)
    - month: 月份 (1-12)
    - year: 年份
    
    Args:
        csv_path: CSV 文件路径
    
    Returns:
        处理后的 DataFrame
    """
    df = pd.read_csv(csv_path)
    
    # 容错处理日期列
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["quarter"] = df["date"].dt.quarter
        df["month"] = df["date"].dt.month
        df["year"] = df["date"].dt.year
    
    return df


def make_schema_text(df: pd.DataFrame) -> str:
    """
    生成 LLM 可读的数据 Schema
    
    格式: `- {column_name}: {dtype}`
    
    Args:
        df: 输入 DataFrame
    
    Returns:
        格式化的 Schema 文本
    """
    return "\n".join(f"- {c}: {dt}" for c, dt in df.dtypes.items())


# ============================================================================
# 5. 代码处理
# ============================================================================

def ensure_execute_python_tags(text: str) -> str:
    """
    规范化 LLM 生成的代码
    
    处理步骤：
    1. 移除 Markdown code fences (```python ... ```)
    2. 若缺失 <execute_python> 标签则自动添加
    
    Args:
        text: LLM 生成的原始文本
    
    Returns:
        包含 <execute_python> 标签的规范化代码
    """
    text = text.strip()
    
    # 移除 Markdown code fences
    text = re.sub(r"^```(?:python)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    
    # 添加标签（如果缺失）
    if "<execute_python>" not in text:
        text = f"<execute_python>\n{text}\n</execute_python>"
    
    return text


def extract_code_from_tags(text: str) -> Optional[str]:
    """
    从 <execute_python> 标签中提取代码
    
    Args:
        text: 包含标签的文本
    
    Returns:
        提取的代码，若未找到则返回 None
    """
    match = re.search(r"<execute_python>(.*?)</execute_python>", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


# ============================================================================
# 6. Jupyter Notebook 美化输出（简易沙盒 UI）
# ============================================================================

def print_html(content: Any, title: Optional[str] = None, is_image: bool = False):
    """
    在 Jupyter Notebook 中美观地显示内容
    
    核心设计亮点：
    1. 多模态智能渲染
    2. CSS 样式隔离（.pretty-card 前缀）
    3. 视觉层级清晰
    
    Args:
        content: 要显示的内容
            - str + is_image=True: 图片路径（Base64 嵌入）
            - pd.DataFrame/Series: HTML 表格
            - 其他: 代码块 (<pre><code>)
        title: 卡片标题（可选）
        is_image: 是否为图片路径
    
    Examples:
        >>> print_html(code, title="📝 Generated Code (V1)")
        >>> print_html("chart_v1.png", title="📊 Chart V1", is_image=True)
        >>> print_html(df.head(), title="📋 Data Preview")
    """
    def image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    
    # 渲染内容
    if is_image and isinstance(content, str):
        b64 = image_to_base64(content)
        rendered = f'<img src="data:image/png;base64,{b64}" alt="Image" style="max-width:100%; height:auto; border-radius:8px;">'
    elif isinstance(content, pd.DataFrame):
        rendered = content.to_html(classes="pretty-table", index=False, border=0, escape=False)
    elif isinstance(content, pd.Series):
        rendered = content.to_frame().to_html(classes="pretty-table", border=0, escape=False)
    elif isinstance(content, str):
        rendered = f"<pre><code>{escape(content)}</code></pre>"
    else:
        rendered = f"<pre><code>{escape(str(content))}</code></pre>"
    
    # CSS 样式（作用域隔离）
    css = """
    <style>
    .pretty-card {
        font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
        border: 2px solid transparent;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0;
        background: linear-gradient(#fff, #fff) padding-box,
                    linear-gradient(135deg, #3b82f6, #9333ea) border-box;
        color: #111;
        box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }
    .pretty-title {
        font-weight: 700;
        margin-bottom: 8px;
        font-size: 14px;
        color: #111;
    }
    /* 🔒 仅影响卡片内部 */
    .pretty-card pre, 
    .pretty-card code {
        background: #f3f4f6;
        color: #111;
        padding: 8px;
        border-radius: 8px;
        display: block;
        overflow-x: auto;
        font-size: 13px;
        white-space: pre-wrap;
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    }
    .pretty-card img { 
        max-width: 100%; 
        height: auto; 
        border-radius: 8px; 
    }
    .pretty-card table.pretty-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
        color: #111;
    }
    .pretty-card table.pretty-table th, 
    .pretty-card table.pretty-table td {
        border: 1px solid #e5e7eb;
        padding: 6px 8px;
        text-align: left;
    }
    .pretty-card table.pretty-table th { 
        background: #f9fafb; 
        font-weight: 600; 
    }
    </style>
    """
    
    title_html = f'<div class="pretty-title">{title}</div>' if title else ""
    card = f'<div class="pretty-card">{title_html}{rendered}</div>'
    display(HTML(css + card))


# ============================================================================
# 7. 调试辅助函数
# ============================================================================

def check_api_keys():
    """
    检查已配置的 API Keys
    
    用于调试环境配置问题
    """
    keys_status = {
        "OpenAI": "✅" if openai_api_key else "❌",
        "Anthropic": "✅" if anthropic_api_key else "❌",
        "Qwen": "✅" if qwen_api_key else "❌",
        "Zhipu": "✅" if zhipu_api_key else "❌",
        "DeepSeek": "✅" if deepseek_api_key else "❌",
        "Moonshot": "✅" if moonshot_api_key else "❌",
    }
    
    print("🔑 API Keys Configuration Status:")
    for provider, status in keys_status.items():
        print(f"  {status} {provider}")
    print()


# ============================================================================
# 8. 高层工作流 API（封装完整流程）
# ============================================================================

def generate_chart_code(
    instruction: str,
    schema_text: str,
    model: str,
    out_path: str,
    temperature: float = 0
) -> str:
    """
    生成初始图表代码
    
    Args:
        instruction: 用户绘图指令
        schema_text: 数据 Schema
        model: 模型名称（如 "qwen3-max", "gpt-4o"）
        out_path: 图片保存路径
        temperature: 温度参数
    
    Returns:
        包含 <execute_python> 标签的完整响应
    """
    prompt = f"""You are a data visualization expert.

Return your answer *strictly* in this format:

<execute_python>
# valid python code here
</execute_python>

Do not add explanations, only the tags and the code.

The code should create a visualization from a DataFrame 'df' with these columns:
{schema_text}

User instruction: {instruction}

Requirements for the code:
1. Assume the DataFrame is already loaded as 'df'.
2. Use matplotlib for plotting.
3. Add clear title, axis labels, and legend if needed.
4. Save the figure as '{out_path}' with dpi=300.
5. Do not call plt.show().
6. Close all plots with plt.close().
7. Add all necessary import python statements

Return ONLY the code wrapped in <execute_python> tags.
"""
    
    return get_response(model, prompt, temperature=temperature)


def reflect_on_image_and_regenerate(
    chart_path: str,
    instruction: str,
    schema_text: str,
    model_name: str,
    out_path_v2: str,
    code_v1: str
) -> tuple[str, str]:
    """
    基于图片反思并重新生成代码
    
    Args:
        chart_path: V1 图片路径
        instruction: 原始用户指令
        schema_text: 数据 Schema
        model_name: 反思模型名称（如 "glm-4v", "qwen-vl-plus"）
        out_path_v2: V2 图片保存路径
        code_v1: 原始代码上下文
    
    Returns:
        (feedback, refined_code) 元组
    """
    # 编码图片
    media_type, b64 = encode_image_b64(chart_path)
    
    # 构建 Prompt
    prompt = f"""You are a data visualization expert.
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
{schema_text}

Instruction:
{instruction}
"""
    
    # 调用多模态 API
    if "claude" in model_name.lower():
        response = image_anthropic_call(model_name, prompt, media_type, b64)
    else:
        response = image_openai_call(model_name, prompt, media_type, b64)
    
    # 解析响应
    lines = response.strip().split('\n', 1)
    feedback_line = lines[0].strip()
    
    try:
        feedback_json = json.loads(feedback_line)
        feedback = feedback_json.get("feedback", "No feedback provided")
    except:
        feedback = feedback_line
    
    remaining_text = lines[1] if len(lines) > 1 else response
    remaining_text = ensure_execute_python_tags(remaining_text)
    refined_code = extract_code_from_tags(remaining_text)
    
    return feedback, refined_code


def run_workflow(
    dataset_path: str,
    user_instruction: str,
    generation_model: str,
    reflection_model: str,
    image_basename: str = "chart",
    verbose: bool = True
) -> dict:
    """
    端到端执行完整的 Reflection Pattern 工作流
    
    工作流程：
    1. 加载数据并生成 Schema
    2. 使用生成模型创建初始代码 (V1)
    3. 执行代码生成图表 V1
    4. 使用多模态模型反思图表质量
    5. 根据反馈生成改进代码 (V2)
    6. 执行改进代码生成图表 V2
    
    Args:
        dataset_path: CSV 数据文件路径
        user_instruction: 用户绘图指令
        generation_model: 代码生成模型（如 "qwen3-max", "gpt-4o"）
        reflection_model: 多模态反思模型（如 "glm-4v", "qwen-vl-plus"）
        image_basename: 图片文件名前缀（默认 "chart"）
        verbose: 是否显示详细输出（默认 True）
    
    Returns:
        包含所有产物的字典：
        - df: DataFrame
        - schema_text: 数据 Schema
        - code_v1: 初始代码
        - chart_v1: V1 图片路径
        - feedback: 反思反馈
        - code_v2: 改进代码
        - chart_v2: V2 图片路径
        - success: 是否成功执行
        - errors: 错误信息列表
    """
    errors = []
    result = {
        "success": False,
        "errors": []
    }
    
    try:
        # 1. 加载数据
        if verbose:
            print("📊 步骤 1/6: 加载数据...")
        df = load_and_prepare_data(dataset_path)
        schema_text = make_schema_text(df)
        result["df"] = df
        result["schema_text"] = schema_text
        if verbose:
            print(f"   ✅ 数据已加载: {len(df)} 行 x {len(df.columns)} 列")
        
        # 2. 生成初始代码 (V1)
        if verbose:
            print(f"\n🤖 步骤 2/6: 使用 {generation_model} 生成初始代码...")
        out_path_v1 = f"{image_basename}_v1.png"
        response_v1 = generate_chart_code(
            user_instruction, schema_text, generation_model, out_path_v1
        )
        response_v1 = ensure_execute_python_tags(response_v1)
        code_v1 = extract_code_from_tags(response_v1)
        result["code_v1"] = code_v1
        result["chart_v1"] = out_path_v1
        
        if not code_v1:
            errors.append("未能从响应中提取代码 (V1)")
            result["errors"] = errors
            return result
        
        if verbose:
            print("   ✅ 代码生成成功")
            print_html(code_v1, title="📝 生成的代码 (V1)")
        
        # 3. 执行代码生成图表 V1
        if verbose:
            print("\n⚙️ 步骤 3/6: 执行代码生成图表 V1...")
        try:
            exec(code_v1, {"df": df, "pd": pd, "plt": plt})
            if verbose:
                print("   ✅ 图表 V1 生成成功")
                if Path(out_path_v1).exists():
                    print_html(out_path_v1, title="📊 图表 V1", is_image=True)
        except Exception as e:
            error_msg = f"执行代码 V1 失败: {str(e)}"
            errors.append(error_msg)
            if verbose:
                print(f"   ❌ {error_msg}")
            result["errors"] = errors
            return result
        
        # 4. 反思并改进
        if verbose:
            print(f"\n🔍 步骤 4/6: 使用 {reflection_model} 进行多模态反思...")
        out_path_v2 = f"{image_basename}_v2.png"
        
        try:
            feedback, code_v2 = reflect_on_image_and_regenerate(
                out_path_v1, user_instruction, schema_text,
                reflection_model, out_path_v2, code_v1
            )
            result["feedback"] = feedback
            result["code_v2"] = code_v2
            result["chart_v2"] = out_path_v2
            
            if verbose:
                print("   ✅ 反思完成")
                print_html(feedback, title="💬 模型反馈 (Reflection)")
                if code_v2:
                    print_html(code_v2, title="📝 改进后的代码 (V2)")
        except Exception as e:
            error_msg = f"反思过程失败: {str(e)}"
            errors.append(error_msg)
            if verbose:
                print(f"   ❌ {error_msg}")
            result["errors"] = errors
            return result
        
        # 5. 执行改进后的代码
        if verbose:
            print("\n⚙️ 步骤 5/6: 执行改进后的代码...")
        try:
            exec(code_v2, {"df": df, "pd": pd, "plt": plt})
            if verbose:
                print("   ✅ 图表 V2 生成成功")
                if Path(out_path_v2).exists():
                    print_html(out_path_v2, title="📊 图表 V2 (改进版)", is_image=True)
        except Exception as e:
            error_msg = f"执行代码 V2 失败: {str(e)}"
            errors.append(error_msg)
            if verbose:
                print(f"   ❌ {error_msg}")
            result["errors"] = errors
            return result
        
        # 6. 成功完成
        if verbose:
            print("\n🎉 步骤 6/6: 工作流完成！")
            print("\n" + "="*60)
            print("📊 对比展示")
            print("="*60)
            # 对比展示
            if Path(out_path_v1).exists() and Path(out_path_v2).exists():
                from IPython.display import HTML, display
                import base64
                
                def image_to_base64(path):
                    with open(path, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                
                b64_v1 = image_to_base64(out_path_v1)
                b64_v2 = image_to_base64(out_path_v2)
                
                html = f"""
                <div style="display: flex; gap: 20px; justify-content: center; align-items: flex-start;">
                    <div style="text-align: center;">
                        <h3 style="color: #3b82f6;">📊 V1 (初始版本)</h3>
                        <img src="data:image/png;base64,{b64_v1}" style="max-width: 100%; border: 2px solid #3b82f6; border-radius: 8px;">
                    </div>
                    <div style="text-align: center;">
                        <h3 style="color: #9333ea;">📊 V2 (改进版本)</h3>
                        <img src="data:image/png;base64,{b64_v2}" style="max-width: 100%; border: 2px solid #9333ea; border-radius: 8px;">
                    </div>
                </div>
                """
                display(HTML(html))
        
        result["success"] = True
        result["errors"] = errors
        return result
        
    except Exception as e:
        error_msg = f"工作流执行失败: {str(e)}"
        errors.append(error_msg)
        if verbose:
            print(f"\n❌ {error_msg}")
            import traceback
            print(traceback.format_exc())
        result["errors"] = errors
        return result


if __name__ == "__main__":
    # 测试 API Keys 配置
    check_api_keys()
