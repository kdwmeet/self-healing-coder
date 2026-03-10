# Self-Healing Coding Agent (자가 치유형 코딩 에이전트)

## 1. 프로젝트 개요

Self-Healing Coding Agent는 사용자의 요구사항에 맞춰 코드를 작성하는 것을 넘어, 작성된 코드를 실제 환경에서 실행하고 디버깅까지 스스로 수행하는 능동형 AI 에이전트입니다.

기존의 코드 생성 AI는 문법적 오류나 실행 환경의 차이로 인해 한 번에 작동하지 않는 코드를 생성하는 경우가 많습니다. 본 프로젝트는 LangGraph의 순환(Cyclic) 아키텍처를 활용하여, 코드가 성공적으로 실행될 때까지 에러 로그(Traceback)를 분석하고 스스로 코드를 수정(Self-Healing)하는 피드백 루프를 구현했습니다.

## 2. 시스템 아키텍처



본 시스템은 두 개의 핵심 노드(Node)와 실행 결과에 따른 조건부 라우팅(Conditional Routing)으로 구성됩니다.

1.  **Coder Node:** 사용자의 목표와 이전 단계의 에러 메시지(존재할 경우)를 분석하여 파이썬 코드를 생성합니다.
2.  **Executor Node:** 파이썬 내장 `subprocess` 모듈을 사용하여 격리된 워크스페이스(`workspace/`) 내에서 생성된 코드를 파일로 저장하고 실제 실행합니다.
3.  **Conditional Edge (라우팅):** * 실행 결과가 정상(Exit Code 0)이면 워크플로우를 종료합니다.
    * 에러가 발생하면 에러 내용을 상태(State)에 저장하고 다시 Coder Node로 되돌려 코드를 수정하게 합니다.
    * 무한 루프 방지를 위해 최대 재시도 횟수(예: 5회)를 초과하면 프로세스를 강제 종료합니다.

## 3. 기술 스택

* **Language:** Python 3.10+
* **Package Manager:** uv
* **LLM:** OpenAI gpt-4o (복잡한 로직 및 에러 분석을 위해 추론 능력이 뛰어난 모델 사용)
* **Orchestration:** LangGraph, LangChain (`langchain_core`)
* **Execution Environment:** Python `subprocess`
* **Web Framework:** Streamlit

## 4. 프로젝트 구조

```text
self-healing-coder/
├── .env                  # OpenAI API 키 설정
├── requirements.txt      # 의존성 패키지 목록
├── main.py               # 스트림릿 기반 실시간 작업 로그 및 UI 대시보드
├── workspace/            # AI가 작성한 스크립트가 저장되고 실행되는 디렉토리
└── app/
    ├── __init__.py
    └── graph.py          # 상태 정의, 노드 구현, 순환 그래프 컴파일
```

## 5. 설치 및 실행 가이드
본 프로젝트는 의존성 관리를 위해 uv 패키지 매니저를 사용합니다.

### 5.1. 사전 준비
저장소를 복제하고 프로젝트 디렉토리로 이동합니다.

```Bash
git clone [레포지토리 주소]
cd self-healing-coder
```
### 5.2. 환경 변수 설정
프로젝트 루트 경로에 .env 파일을 생성하고 OpenAI API 키를 입력하십시오.

```Ini, TOML
OPENAI_API_KEY=sk-your-api-key-here
```
### 5.3. 가상환경 생성 및 패키지 설치
독립된 가상환경을 구성하고 패키지를 설치합니다.

```Bash
uv venv
uv pip install -r requirements.txt
```
### 5.4. 시스템 실행
Streamlit 애플리케이션을 구동합니다.

```Bash
uv run streamlit run main.py
```
## 6. 테스트 시나리오
애플리케이션 구동 후, 에이전트의 디버깅 능력을 확인하기 위해 의도적으로 에러를 유발하는 프롬프트를 입력해 보십시오.

* **테스트 입력 예시**: "1부터 50까지의 피보나치 수열을 출력하는 파이썬 코드를 작성해. 단, 첫 번째 코드 작성 시 의도적으로 print 함수를 prnt로 잘못 타이핑해서 NameError가 발생하도록 만들고, 두 번째 시도에서 그 에러를 읽고 스스로 고쳐서 정상 작동하게 만들어."

* **기대 결과**: 로그 화면에서 Coder가 오타가 포함된 코드를 작성하고, Executor가 NameError를 반환하며, 다시 Coder가 이를 수정하여 완벽한 최종 코드를 도출하는 과정을 확인할 수 있습니다.

## 7. 보안 및 주의 사항 (Security Warning)
* **코드 실행 권한**: 현재 아키텍처는 로컬 환경의 subprocess를 통해 AI가 작성한 코드를 직접 실행합니다. 파일 삭제(os.remove) 등 악의적이거나 치명적인 시스템 명령어가 포함된 코드가 생성될 위험이 있습니다.

* **프로덕션 환경 적용 시 권장 사항**: 실제 서비스에 배포하거나 권한이 높은 서버에서 구동할 경우, 반드시 Docker 컨테이너와 같은 엄격하게 격리된 샌드박스 환경 내부에서 Executor Node가 동작하도록 아키텍처를 수정해야 합니다.

## 8. 실행 화면
<img width="1314" height="843" alt="스크린샷 2026-03-10 103034" src="https://github.com/user-attachments/assets/df65010e-835e-4c70-9e04-b61744c5c680" />

