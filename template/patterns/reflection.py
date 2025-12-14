"""
Reflection Pattern Template

This module implements the Reflection Pattern (Generate -> Execute -> Reflect -> Regenerate).
It serves as a skeleton for building agents that can self-correct based on feedback.
"""

from typing import Callable, Any, Dict, List, Optional
from core import print_html

def run_reflection_loop(
    user_instruction: str,
    generator_func: Callable[[str, Optional[str]], str],
    executor_func: Callable[[str], Any],
    reflector_func: Callable[[str, Any, str], str],
    max_iterations: int = 3,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Executes a generic Reflection Pattern loop.
    
    Args:
        user_instruction: The initial task for the agent.
        generator_func: Function(instruction, feedback) -> code/plan
            - Should take the instruction and optional feedback history.
            - Should return the generated content (e.g., code).
        executor_func: Function(code) -> execution_result
            - Should execute the generated content.
            - Should return the result (e.g., output, error, image path).
        reflector_func: Function(code, result, instruction) -> feedback
            - Should analyze the code and result against the instruction.
            - Should return text feedback.
        max_iterations: Maximum number of retry attempts.
        verbose: Whether to print UI cards for each step.
        
    Returns:
        Dictionary containing the final result and history.
    """
    
    history = []
    current_feedback = None
    
    for i in range(max_iterations + 1):
        step_label = f"Iteration {i+1}/{max_iterations + 1}"
        if verbose:
            print_html(f"Starting {step_label}...", title="🔄 Workflow Step")
            
        # 1. Generate (or Regenerate)
        try:
            generated_content = generator_func(user_instruction, current_feedback)
            if verbose:
                print_html(generated_content, title=f"📝 Generated Content ({step_label})")
        except Exception as e:
            return {"status": "error", "message": f"Generation failed: {str(e)}", "history": history}

        # 2. Execute
        try:
            execution_result = executor_func(generated_content)
            # Note: executor_func should handle its own UI output if needed, 
            # or return something printable.
        except Exception as e:
            execution_result = f"Execution Error: {str(e)}"
            if verbose:
                print_html(execution_result, title=f"⚠️ Execution Failed ({step_label})")

        # 3. Reflect (Skip if it's the last iteration)
        if i < max_iterations:
            try:
                feedback = reflector_func(generated_content, execution_result, user_instruction)
                if verbose:
                    print_html(feedback, title=f"🤔 Reflection Feedback ({step_label})")
                
                # If feedback indicates success, stop early
                if "SC_SUCCESS" in feedback or "NO_ISSUES" in feedback: # Define your own success signal
                    if verbose:
                        print_html("Success signal received. Stopping loop.", title="✅ Complete")
                    return {
                        "status": "success",
                        "final_content": generated_content,
                        "final_result": execution_result,
                        "history": history
                    }
                
                current_feedback = feedback
                history.append({
                    "step": i,
                    "content": generated_content,
                    "result": execution_result,
                    "feedback": feedback
                })
                
            except Exception as e:
                print_html(f"Reflection failed: {str(e)}", title="⚠️ Reflection Error")
                # If reflection fails, maybe just continue or stop?
                break
        else:
            # Final iteration done
            return {
                "status": "max_iterations_reached",
                "final_content": generated_content,
                "final_result": execution_result,
                "history": history
            }
            
    return {"status": "finished", "history": history}
