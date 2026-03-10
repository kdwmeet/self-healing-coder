import streamlit as st
from app.graph import app_graph

st.set_page_config(page_title="Self-Healing Coding Agent", layout="wide")

st.title("자가 치유형 코딩 에이전트")
st.caption("목표를 지시하면 AI가 코드를 작성하고, 실제 실행한 뒤 에러가 나면 스스로 원인을 분석하여 코드를 고칩니다.")
st.divider()

task_input = st.text_area(
    "AI가 작성하고 실행할 파이썬 스크립트의 목표를 입력하십시오.",
    placeholder="예: 1부터 100까지의 숫자 중 소수만 찾아내서 리스트로 출력하는 코드를 작성해.",
    height=100
)

if st.button("코드 작성 및 자가 테스트 시작", type="primary"):
    if task_input.strip():
        initial_state = {
            "task": task_input,
            "code": "",
            "error": "",
            "output": "",
            "iterations": 0
        }

        st.subheader("에이전트 작업 로그")
        log_container = st.container(border=True)

        final_state = None

        with st.spinner("AI가 코딩 및 테스트를 진행하고 있습니다."):
            # 그래프 실행 및 상태 스트리밍
            for output in app_graph.stream(initial_state):
                for node_name, state_update in output.items():
                    with log_container:
                        if node_name == "coder":
                            st.info(f"[coder] 파이썬 코드 작성을 완료했습니다.")
                            with st.expander("작성된 코드 보기"):
                                st.code(state_update.get("code", ""), language="python")
                            
                        elif node_name == "executor":
                            current_iter = state_update.get("iterations", 1)
                            error_msg = state_update.get("error", "")

                            if error_msg:
                                st.error(f"[Executor] 시도 {current_iter}: 코드 실행 중 에러가 발생했습니다. Coder에게 수정을 요청합니다.")
                                with st.expander("에러 로그 (Traceback)"):
                                    st.code(error_msg, language="bash")
                            else:
                                st.success(f"[Executor] 시도 {current_iter}: 코드 실행 성공! (에러 없음)")
                    
                    final_state = state_update # 마지막 상태 업데이트 저장
        
        st.divider()
        st.subheader("최종 결과")

        if final_state:
            # 최종 코드 출력
            st.markdown("### 확정된 코드")
            st.code(final_state.get("code", ""), language="python")

            # 최종 실행 결과 (표준 출력)
            st.markdown("### 콘솔 출력 결과")
            if final_state.get("output"):
                st.code(final_state.get("output", ""), language="bash")
            else:
                st.write("출력된 결과가 없습니다.")
            
            # 실패 처리 확인
            if final_state.get("error") and final_state.get("iterations", 0) >= 5:
                st.warning("최대 재시도 횟수(5회)에 도달하여 워크플로우가 강제 종료되었습니다. 최종 에러를 확인하십시오.")
