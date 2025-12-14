import re
from typing import Dict, Callable, List
from core import get_client_for_model, print_html

def run_react_loop(
    user_query: str, 
    system_prompt: str,
    tools: Dict[str, Callable],
    model_name: str = "glm-4-flash", 
    max_steps: int = 5
):
    """
    通用的 ReAct (Reasoning + Acting) 循环控制器。
    
    Args:
        user_query: 用户的原始问题
        system_prompt: 定义 Agent 角色和工具使用规范的 Prompt
        tools: 工具字典 {func_name: func_object}
        model_name: 模型名称
        max_steps: 最大思考步数
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    
    print_html(f"🚀 开始任务: {user_query}", title="System Start")
    
    for step in range(max_steps):
        # 1. LLM 思考
        client = get_client_for_model(model_name)
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.1
        )
        content = response.choices[0].message.content
        
        print_html(content, title=f"Step {step + 1}: Thought & Action")
        messages.append({"role": "assistant", "content": content})
        
        # 2. 解析 Action (这里使用简单的正则，未来可替换为 Function Calling)
        action_match = re.search(r"Action:\s*(\w+)\((.*)\)", content)
        
        if not action_match:
            if "finish" in content.lower():
                break
            continue
            
        func_name = action_match.group(1)
        args_str = action_match.group(2)
        
        # 3. 执行工具
        if func_name == "finish":
            answer_match = re.search(r'answer="(.*)"', args_str)
            final_answer = answer_match.group(1) if answer_match else args_str
            print_html(final_answer, title="✅ Final Answer")
            return final_answer
            
        elif func_name in tools:
            try:
                # 简易参数解析
                kwargs = {}
                for arg in args_str.split(','):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        kwargs[k.strip()] = v.strip().strip('"').strip("'")
                
                observation = tools[func_name](**kwargs)
            except Exception as e:
                observation = f"Error: {str(e)}"
                
            print_html(observation, title=f"👁️ Observation ({func_name})")
            messages.append({"role": "user", "content": f"Observation: {observation}"})
        else:
            error_msg = f"Error: Tool '{func_name}' not found."
            print_html(error_msg, title="❌ Error")
            messages.append({"role": "user", "content": f"Observation: {error_msg}"})
            
    return "Max steps reached."