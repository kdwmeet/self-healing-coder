import os
import re
import subprocess
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

load_dotenv()

# 작업 공간 폴더 생성
WORKSPACE_DIR = "workspace"
os.makedirs(WORKSPACE_DIR, exist_ok=True)
FILE_PATH = os.path.join(WORKSPACE_DIR, "generated_script.py")

class AgentState(TypedDict):
    task: str
    code: str
    error: str
    output: str
    iterations: int

def coder_node(state: AgentState):
    """요구사항이나 이전 에러를 바탕으로 파이썬 코드를 작성합니다."""
    llm = ChatOpenAI(model="gpt-5-mini", reasoning_effort="low")

    system_instructions = """당신은 뛰어난 파이썬 시니어 개발자입니다. 
주어진 목표를 달성하는 완벽한 파이썬 코드를 작성하십시오.
반드시 실행 가능한 형태여야 하며, 마크다운 코드 블록(```python ... ```) 안에 코드만 작성하십시오.
이전에 발생한 에러 메시지가 있다면, 그 원인을 분석하고 코드를 수정하여 다시 작성하십시오."""

    prompt =ChatPromptTemplate.from_messages([
        ("system", system_instructions),
        ("user", "목표: {task}\n\n이전 실행 에러:\n{error}")
    ])

    chain = prompt | llm
    response = chain.invoke({
        "task": state["task"],
        "error": state.get("error", "에러 없음. 최초 작성.")            
    }).content

    # 정규표현식을 사용하여 마크다운 코드 블록에서 순수 파이썬 코드만 추출
    code_match = re.search(r"```python\n(.*?)\n```", response, re.DOTALL)
    if code_match:
        clean_code = code_match.group(1)
    else:
        # 마크다운 블록이 없을 경우 전체를 코드로 간주
        clean_code = response.replace("```python", "").replace("```", "").strip()

    return {"code": clean_code}

def executor_node(state: AgentState):
    """작성된 코드를 파일로 저장하고 실제 실행하여 결과를 확인합니다."""
    code = state.get("code", "")
    current_iterations = state.get("iterations", 0)

    # 코드 파일 저징
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    
    # 서브프로세스로 파이썬 스크립트 실행
    try:
        # 보안을 위해 타임아웃 10초 설정
        result = subprocess.run(
            ["python", FILE_PATH],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # 실행 성공
            return {
                "error": "",
                "output": result.stdout,
                "iterations": current_iterations + 1
            }
        else:
            # 실행 실패 (에러 발생)
            return {
                "error": result.stderr,
                "output": result.stdout,
                "iterations": current_iterations + 1
            }
    except subprocess.TimeoutExpired:
        return {
            "error": "실행 시간 초과 (10초). 무한 루프에 빠졌거나 연산이너무 오래 걸립니다.",
            "output": "",
            "iterations": current_iterations + 1
        }
    except Exception as e:
        return {
            "error": f"시스템 에러 발생: {str(e)}",
            "output": "",
            "iterations": current_iterations + 1
        }

def route_evaluation(state: AgentState):
    """실행 결과에 따라 워크플로우를 종료하거나 다시 코더 노드로 보냅니다."""
    # 최대 5번까지만 재시도 (무한 루프 방지)
    if state.get("iterations", 0) >= 5:
        return END
    
    # 에러가 없다면 성공적으로 완료된 것이므로 종료
    if not state.get("error"):
        return END
    
    # 에어가 존재한다면 다시 코드를 수정하도록 코더 노드로 회귀
    return "coder"

# 그래프 조립
workflow = StateGraph(AgentState)

workflow.add_node("coder", coder_node)
workflow.add_node("executor", executor_node)

workflow.add_edge(START, "coder")
workflow.add_edge("coder", "executor")
workflow.add_conditional_edges("executor", route_evaluation)

app_graph = workflow.compile()