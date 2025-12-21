import ast
import json
import os
import sys
from typing import List, Optional

from dotenv import load_dotenv

from llm_client import HelloAgentsLLM
from ui_utils import print_html

# --- 1. 规划器 (Planner) 定义 ---
PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划，```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

class Planner:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    def _parse_plan(self, response_text: str) -> List[str]:
        """从 LLM 响应中解析计划列表"""
        try:
            # 尝试提取 markdown 代码块中的内容
            if "```python" in response_text:
                plan_str = response_text.split("```python")[1].split("```")[0].strip()
            elif "```" in response_text:
                plan_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                plan_str = response_text.strip()
            
            # 使用 ast.literal_eval 安全地解析 Python 列表
            plan = ast.literal_eval(plan_str)
            
            if isinstance(plan, list):
                return plan
            return []
        except (ValueError, SyntaxError, IndexError):
            return []

    def plan(self, question: str) -> List[str]:
        """
        根据用户问题生成一个行动计划。
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]
        
        print_html("正在生成计划...", title="🧠 Planner Thinking")
        response_text = self.llm_client.think(messages=messages) or ""
        
        # 解析计划
        plan = self._parse_plan(response_text)
        
        if plan:
            print_html(plan, title="✅ Plan Generated")
            return plan
        else:
            print_html(f"无法解析计划或生成格式错误。\n原始响应: {response_text}", title="❌ Plan Error")
            return []

# --- 2. 执行器 (Executor) 定义 ---
EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对“当前步骤”的回答:
"""

class Executor:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    def execute(self, question: str, plan: List[str]) -> str:
        history = ""
        final_answer = ""
        
        print_html("开始执行计划...", title="🚀 Execution Start")
        
        for i, step in enumerate(plan, 1):
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question, 
                plan=plan, 
                history=history if history else "无", 
                current_step=step
            )
            messages = [{"role": "user", "content": prompt}]
            
            response_text = self.llm_client.think(messages=messages) or ""
            
            # 渲染结果
            print_html(f"**Step**: {step}\n**Result**: {response_text}", title=f"Step {i}/{len(plan)} Result")
            
            history += f"步骤 {i}: {step}\n结果: {response_text}\n\n"
            final_answer = response_text
            
        return final_answer

# --- 3. 智能体 (Agent) 整合 ---
class PlanAndSolveAgent:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str):
        print_html(question, title="🏁 Task Start")
        
        # 1. 规划
        plan = self.planner.plan(question)
        if not plan:
            print_html("无法生成有效的行动计划，任务终止。", title="🛑 Task Aborted")
            return
            
        # 2. 执行
        final_answer = self.executor.execute(question, plan)
        
        print_html(final_answer, title="🎉 Final Answer")

# --- 4. 主函数入口 ---
if __name__ == '__main__':
    try:
        # 确保环境变量已加载
        load_dotenv()
        
        llm_client = HelloAgentsLLM()
        agent = PlanAndSolveAgent(llm_client)
        
        question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
        agent.run(question)
        
    except Exception as e:
        print_html(f"运行出错: {e}", title="❌ System Error")
