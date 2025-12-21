import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

# 加载 .env 文件 (确保能读取到根目录的 .env)
# 假设当前运行目录在项目根目录，或者显式指定 .env 路径
load_dotenv() 

class HelloAgentsLLM:
    """
    适配 Datawhale Hello Agents 教程的 LLM 客户端。
    支持自动加载 .env 中的通用配置，也支持传入特定参数。
    """
    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        # 1. 尝试使用传入参数
        # 2. 尝试读取教程标准的通用环境变量 (LLM_*)
        # 3. 兜底：尝试读取项目中已有的特定厂商环境变量 (如 QWEN_*) 以方便直接使用
        
        self.model = model or os.getenv("LLM_MODEL_ID") or "qwen-turbo" # 默认示例
        
        # 自动适配 Key 和 BaseURL
        self.api_key = apiKey or os.getenv("LLM_API_KEY")
        self.base_url = baseUrl or os.getenv("LLM_BASE_URL")
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        
        # 如果没有通用的 LLM_API_KEY，尝试自动通过模型名匹配已有的 Key (可选优化)
        if not self.api_key:
            if "qwen" in self.model.lower():
                self.api_key = os.getenv("QWEN_API_KEY")
                self.base_url = os.getenv("QWEN_BASE_URL")
            elif "deepseek" in self.model.lower():
                self.api_key = os.getenv("DEEPSEEK_API_KEY")
                self.base_url = os.getenv("DEEPSEEK_BASE_URL")
            # ... 其他模型适配
            
        if not self.api_key:
            raise ValueError("未找到 API Key。请在 .env 中配置 LLM_API_KEY 或特定的模型 Key。")

        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    def think(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        核心方法：发送消息历史并获取回复
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=False # 教程示例通常先用非流式，便于理解
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {str(e)}"