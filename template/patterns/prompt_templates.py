"""
Prompt Templates Management

Store your system prompts and template strings here to keep your logic code clean.
"""

# Example: Code Generation Prompt
CODE_GEN_SYSTEM_PROMPT = """You are an expert Python developer.
Your task is to generate code based on the user's request.
Ensure the code is robust and follows best practices.
"""

CODE_GEN_USER_TEMPLATE = """
Task: {instruction}

Previous Feedback (if any):
{feedback}

Return your code wrapped in <execute_python> tags.
"""

# Example: Reflection Prompt
REFLECTION_SYSTEM_PROMPT = """You are a critical code reviewer.
Analyze the provided code and its execution result.
Identify any errors, logical flaws, or deviations from the user's request.
"""

REFLECTION_USER_TEMPLATE = """
User Instruction: {instruction}

Generated Code:
{code}

Execution Result:
{result}

Provide constructive feedback. If the result is perfect, output "SC_SUCCESS".
"""
