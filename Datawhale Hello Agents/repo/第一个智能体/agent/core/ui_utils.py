"""
UI Utilities for Jupyter Notebooks

This module provides tools for creating beautiful, card-style UIs in Jupyter Notebooks.
It supports multimodal content rendering (images, dataframes, code) with scoped CSS.
"""

import base64
import pandas as pd
from typing import Any, Optional
from IPython.display import HTML, display
from html import escape

def print_html(content: Any, title: Optional[str] = None, is_image: bool = False):
    """
    Renders content in a beautiful card-style UI within Jupyter Notebooks.
    
    Features:
    - Multimodal rendering (Images, DataFrames, Code)
    - Scoped CSS (prevents global style pollution)
    - Visual hierarchy with titles
    
    Args:
        content: The content to display.
            - str + is_image=True: Path to image file (embedded as Base64)
            - pd.DataFrame/Series: Rendered as HTML table
            - Other: Rendered as code block (<pre><code>)
        title: Optional title for the card.
        is_image: Set to True if content is an image file path.
    
    Examples:
        >>> print_html(code, title="📝 Generated Code")
        >>> print_html("chart.png", title="📊 Visualization", is_image=True)
        >>> print_html(df.head(), title="📋 Data Preview")
    """
    def image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    
    # Render content based on type
    if is_image and isinstance(content, str):
        try:
            b64 = image_to_base64(content)
            rendered = f'<img src="data:image/png;base64,{b64}" alt="Image" style="max-width:100%; height:auto; border-radius:8px;">'
        except Exception as e:
            rendered = f"<pre><code>Error loading image: {escape(str(e))}</code></pre>"
    elif isinstance(content, pd.DataFrame):
        rendered = content.to_html(classes="pretty-table", index=False, border=0, escape=False)
    elif isinstance(content, pd.Series):
        rendered = content.to_frame().to_html(classes="pretty-table", border=0, escape=False)
    elif isinstance(content, str):
        rendered = f"<pre><code>{escape(content)}</code></pre>"
    else:
        rendered = f"<pre><code>{escape(str(content))}</code></pre>"
    
    # Scoped CSS
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
    /* 🔒 Scoped styles */
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
