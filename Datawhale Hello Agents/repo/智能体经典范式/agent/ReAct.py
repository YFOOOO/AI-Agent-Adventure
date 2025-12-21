import json
import re
import sys
import os

# 将上级目录加入路径以导入 llm_client 和 tools
sys.path.append(os.path.abspath(".."))

from typing import Dict, Any, Tuple, Optional
from llm_client import HelloAgentsLLM
from tools import ToolExecutor, search
from ui_utils import print_html  # 导入 UI 工具

# 1. 优化后的 Prompt 模板，使用 JSON 格式输出
REACT_JSON_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

# 可用工具
{tools}

# 输出格式要求
- 请**严格**按照以下 JSON 格式输出你的思考和行动。不要输出任何非 JSON 内容。
{{
    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",
    "action": "你决定采取的行动，必须是以下格式之一："
    {{
        "name": "工具名称 (例如 Search, 或 Finish)",
        "args": {{
            "arg_name": "arg_value"
        }}
    }}
}}

- 当你收集到足够的信息，能够回答用户的最终问题时，你必须将 action 的 name 设置为 "Finish"，并在 args 中使用 "answer" 字段提供最终答案。
- 例如: {{ "thought": "我已找到答案...", "action": {{ "name": "Finish", "args": {{ "answer": "这是最终答案" }} }} }}

# 当前任务
现在，请开始解决以下问题：
Question: {question}
History: {history}
"""

class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        self.history = []
        current_step = 0

        # 使用 print_html 渲染开始状态
        print_html(f"🚀 开始任务: {question}", title="System Start")

        while current_step < self.max_steps:
            current_step += 1
            
            # 1. 构建上下文
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_JSON_PROMPT_TEMPLATE.format(
                tools=tools_desc, 
                question=question, 
                history=history_str
            )

            # 2. LLM 思考
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)
            
            if not response_text:
                print_html("LLM未能返回有效响应。", title="❌ Error")
                break

            # 3. 解析 JSON 输出
            thought, tool_name, tool_args = self._parse_json_output(response_text)
            
            # 渲染思考过程 (无论解析是否成功，先展示思考)
            if thought:
                print_html(thought, title=f"Step {current_step}: 🤔 Thought")
            
            if not tool_name:
                print_html(f"未能解析出有效的 Action。\n原始响应: {response_text}", title="⚠️ Warning")
                self.history.append(f"System Observation: 上一步输出格式错误，请严格输出合法的 JSON。")
                continue

            # 4. 处理结束指令
            if tool_name.lower() == "finish":
                final_answer = tool_args.get("answer", str(tool_args))
                print_html(final_answer, title="🎉 Final Answer")
                return final_answer

            # 5. 执行工具
            # 渲染即将执行的动作
            action_display = f"Tool: {tool_name}\nArgs: {json.dumps(tool_args, ensure_ascii=False, indent=2)}"
            print_html(action_display, title=f"Step {current_step}: 🎬 Action")
            
            tool_function = self.tool_executor.getTool(tool_name)
            
            if tool_function:
                try:
                    if isinstance(tool_args, dict):
                        observation = tool_function(**tool_args)
                    else:
                        observation = tool_function(tool_args)
                except TypeError as e:
                     # 捕获参数错误，并给出具体引导
                     sig = inspect.signature(tool_function)
                     observation = f"Tool Execution Error: 参数错误。工具 '{tool_name}' 需要参数 {sig}。你的输入: {tool_args}。错误详情: {str(e)}"
                except Exception as e:
                    observation = f"Tool Execution Error: {str(e)}"
            else:
                observation = f"Error: 未找到名为 '{tool_name}' 的工具。请检查拼写，可用工具列表请参考 System Prompt。"

            # 渲染观察结果
            print_html(observation, title=f"Step {current_step}: 👀 Observation")

            # 6. 更新历史
            action_record = json.dumps({"name": tool_name, "args": tool_args}, ensure_ascii=False)
            self.history.append(f"Action: {action_record}")
            self.history.append(f"Observation: {observation}")

        print_html("已达到最大步数，流程终止。", title="🛑 Stop")
        return None

    def _parse_json_output(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        try:
            clean_text = text.strip()
            if "```" in clean_text:
                match = re.search(r"```(?:json)?\s*(.*?)\s*```", clean_text, re.DOTALL)
                if match:
                    clean_text = match.group(1)
            
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = clean_text[start_idx : end_idx + 1]
                data = json.loads(json_str)
                
                thought = data.get("thought")
                action = data.get("action", {})
                
                if isinstance(action, dict):
                    tool_name = action.get("name")
                    tool_args = action.get("args", {})
                else:
                    tool_name = None
                    tool_args = {}
                    
                return thought, tool_name, tool_args
            return None, None, None

        except json.JSONDecodeError:
            return None, None, None

# --- 运行演示 ---
if __name__ == '__main__':
    # 初始化组件
    try:
        llm = HelloAgentsLLM()
        tool_executor = ToolExecutor()
        
        # 注册工具
        search_desc = "一个网页搜索引擎。输入参数应为 {'query': '搜索关键词'}。"
        # search_desc = "一个网页搜索引擎。输入参数应为 {'query': '搜索关键词'}。"
        tool_executor.registerTool("Search", search_desc, search)
        
        # 实例化并运行
        agent = ReActAgentJSON(llm_client=llm, tool_executor=tool_executor)
        question = "小米SU7 Ultra 原型车的纽北圈速是多少？"
        
        agent.run(question)
        
    except Exception as e:
        print(f"初始化或运行时出错: {e}")
        print("请确保 .env 文件配置正确且已安装所有依赖。")