# 增加模型选择功能，默认使用 Mimo-V2-flash
# 为流式响应增加了安全检查逻辑，避免 `choices` 为空导致的空响应；增加非流式响应支持，默认关闭

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
        
        self.model = model or os.getenv("LLM_MODEL_ID") or "Mimo-V2-flash" # 默认示例
        
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

    def think(self, messages: List[Dict[str, str]], temperature: float = 0.7, stream: bool = False) -> str:
        """
        核心方法：发送消息历史并获取回复
        :param stream: 是否开启流式输出 (打印到控制台)
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=stream 
            )
            
            if not stream:
                # 非流式：直接返回
                print("✅ 大语言模型响应成功!", flush=True)
                return response.choices[0].message.content
            else:
                # 流式处理逻辑
                collected_content = []
                print("✅ 大语言模型响应成功!", flush=True)
                
                for chunk in response:
                    # 1. 安全检查：如果 choices 为空，直接跳过
                    if not chunk.choices:
                        continue
                    # 2. 获取内容：如果 delta 为空，直接跳过
                    content = chunk.choices[0].delta.content
                    # 3. 安全检查：如果 content 是 None（有时可能是空字符串或 None），也跳过
                    if content:
                        print(content, end="", flush=True)
                        collected_content.append(content)
                print()  # 在流式输出结束后换行
                return "".join(collected_content)

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return f"Error calling LLM: {str(e)}"

# --- 客户端使用示例 ---
if __name__ == '__main__':
    try:
        llmClient = HelloAgentsLLM()
        
        exampleMessages = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"}
        ]
        
        print("--- 调用LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print("\n\n--- 完整模型响应 ---")
            print(responseText)

    except ValueError as e:
        print(e)