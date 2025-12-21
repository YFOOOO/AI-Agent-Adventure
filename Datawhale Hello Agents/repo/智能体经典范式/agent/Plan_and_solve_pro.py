import ast
import json
import os
import sys
from typing import List, Tuple

from dotenv import load_dotenv

from llm_client import HelloAgentsLLM
from ui_utils import print_html

# --- Prompts ---
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

REPLAN_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。智能体在执行某个计划时遇到了阻碍，需要你协助进行动态重规划。

# 原始问题:
{question}

# 已完成的历史步骤与结果:
{history}

# 遇到的问题/阻碍:
{failure_reason}

你的任务是：基于目前的状况，为**剩余未完成的目标**生成一个新的行动计划。
请不要包含已经完成的步骤，只输出接下来的步骤。

请严格按照以下格式输出你的新计划，```python与```作为前后缀是必要的:
```python
["新步骤1", "新步骤2", ...]
```
"""

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

EVAL_PROMPT_TEMPLATE = """
你是一个客观的裁判。请判断以下任务步骤的执行结果是否成功。

任务步骤: {step}
执行结果: {result}

判断标准：
1. 如果结果是一个明确的答案（即使答案是"无解"、"不存在"，只要是基于事实的合理结论），视为【成功】。
2. 如果结果表明发生了系统错误、工具调用失败、或者回答"我不知道"且没有给出理由，视为【失败】。
3. 特别注意：如果结果解释了为什么无法计算，这属于成功的回答。

请只输出 JSON 格式，格式如下：
```json
{{
    "success": true/false,
    "reason": "简短的理由"
}}
```
"""

# --- Classes ---

class ReplanningPlanner:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    def _parse_plan(self, response_text: str) -> list[str]:
        try:
            if "```python" in response_text:
                plan_str = response_text.split("```python")[1].split("```")[0].strip()
            elif "```" in response_text:
                plan_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                plan_str = response_text.strip()
            
            plan = ast.literal_eval(plan_str)
            if isinstance(plan, list):
                return plan
            return []
        except Exception:
            return []

    def plan(self, question: str) -> list[str]:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]
        
        print_html("正在生成初始计划...", title="🧠 Planner Thinking")
        response = self.llm_client.think(messages=messages) or ""
        
        plan = self._parse_plan(response)
        if plan:
            print_html(plan, title="✅ Plan Generated")
        else:
            print_html(f"无法生成计划。响应: {response}", title="❌ Plan Error")
            
        return plan

    def replan(self, question: str, history: str, failure_reason: str) -> list[str]:
        prompt = REPLAN_PROMPT_TEMPLATE.format(
            question=question,
            history=history,
            failure_reason=failure_reason
        )
        messages = [{"role": "user", "content": prompt}]
        
        print_html("正在进行动态重规划...", title="🔄 Replanning Thinking")
        response = self.llm_client.think(messages=messages) or ""
        
        plan = self._parse_plan(response)
        return plan

class ReplanningExecutor:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    def execute_step(self, question: str, plan: list[str], history: str, current_step: str) -> str:
        prompt = EXECUTOR_PROMPT_TEMPLATE.format(
            question=question, 
            plan=plan, 
            history=history if history else "无", 
            current_step=current_step
        )
        messages = [{"role": "user", "content": prompt}]
        return self.llm_client.think(messages=messages) or ""

    def evaluate_result(self, step: str, result: str) -> Tuple[bool, str]:
        """
        使用 LLM (Critic) 进行语义评估
        """
        prompt = EVAL_PROMPT_TEMPLATE.format(step=step, result=result)
        messages = [{"role": "user", "content": prompt}]
        
        # print_html("正在评估执行结果...", title="⚖️ Critic Evaluating") 
        response = self.llm_client.think(messages=messages) or "{}"
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
                
            eval_result = json.loads(json_str)
            return eval_result.get("success", False), eval_result.get("reason", "Unknown reason")
        except Exception as e:
            print(f"Critic parse error: {e}")
            return True, "Critic failed to parse, assuming success."

class ReplanningAgent:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        self.planner = ReplanningPlanner(self.llm_client)
        self.executor = ReplanningExecutor(self.llm_client)

    def run(self, question: str):
        print_html(question, title="🏁 Task Start (Pro Agent)")
        
        plan = self.planner.plan(question)
        if not plan:
            return

        history_str = ""
        final_answer = ""
        
        while plan:
            current_step = plan.pop(0)
            
            result = self.executor.execute_step(question, plan, history_str, current_step)
            print_html(f"**Step**: {current_step}\n**Result**: {result}", title="🎬 Executing Step")

            success, message = self.executor.evaluate_result(current_step, result)
            
            if success:
                history_str += f"步骤: {current_step}\n结果: {result}\n\n"
                final_answer = result
            else:
                print_html(f"Critic 判定失败: {message}", title="⚠️ Execution Rejected")
                
                new_remaining_plan = self.planner.replan(question, history_str, failure_reason=message)
                
                if new_remaining_plan:
                    plan = new_remaining_plan 
                    print_html(f"已更新后续计划: {plan}", title="🔄 Plan Updated")
                else:
                    print_html("重规划失败，任务终止。", title="🛑 Stop")
                    return

        print_html(final_answer, title="🎉 Final Answer")

if __name__ == "__main__":
    load_dotenv()
    
    llmClient = HelloAgentsLLM()
    agent = ReplanningAgent(llmClient)
    
    # Test case: 10/0
    agent.run("计算 10 除以 0 的结果，然后将结果加上 5。")