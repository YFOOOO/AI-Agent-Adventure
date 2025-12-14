"""
Chart Generation Agent Logic

This module contains the business logic for the Chart Generation Agent, including:
1. System Prompts
2. Data Processing Tools
3. Code Generation & Reflection Logic
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Any
from core import (
    get_response, 
    image_anthropic_call, 
    image_openai_call, 
    encode_image_b64,
    ensure_execute_python_tags,
    extract_code_from_tags
)

# ============================================================================
# 1. System Prompts
# ============================================================================

GENERATOR_PROMPT_TEMPLATE = """You are a data visualization expert.

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

REFLECTOR_PROMPT_TEMPLATE = """You are a data visualization expert.
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

# ============================================================================
# 2. Data Tools
# ============================================================================

def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """
    加载 CSV 并自动扩展日期列
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
    """
    return "\n".join(f"- {c}: {dt}" for c, dt in df.dtypes.items())

# ============================================================================
# 3. Agent Logic Functions
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
    """
    prompt = GENERATOR_PROMPT_TEMPLATE.format(
        schema_text=schema_text,
        instruction=instruction,
        out_path=out_path
    )
    
    return get_response(model, prompt, temperature=temperature)


def reflect_on_image_and_regenerate(
    chart_path: str,
    instruction: str,
    schema_text: str,
    model_name: str,
    out_path_v2: str,
    code_v1: str
) -> Tuple[str, str]:
    """
    基于图片反思并重新生成代码
    """
    # 编码图片
    media_type, b64 = encode_image_b64(chart_path)
    
    # 构建 Prompt
    prompt = REFLECTOR_PROMPT_TEMPLATE.format(
        code_v1=code_v1,
        out_path_v2=out_path_v2,
        schema_text=schema_text,
        instruction=instruction
    )
    
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

def execute_chart_code(code: str, df: pd.DataFrame) -> None:
    """
    安全执行绘图代码
    """
    # 提供必要的上下文
    exec_globals = {"df": df, "pd": pd, "plt": plt}
    exec(code, exec_globals)
