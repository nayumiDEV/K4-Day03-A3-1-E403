"""
Role 5 Interface (LLM-enabled)

File này dành cho Role 5: Trace Analyst / Observability. Nó cung cấp một
giao diện CLI nhẹ để chạy "baseline chatbot" và "ReAct agent" dùng LLM
thông qua adapter `providers.get_llm_provider()`.

Không làm thay đổi `src/app.py` (Role 4) — app.py vẫn là Flask app chính.
"""

import ast
import json
import os
import re
import sys
from dotenv import load_dotenv

# đảm bảo import modules trong src/ hoạt động
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from providers import get_llm_provider
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from tools import (
    recommend_career_paths,
    get_career_requirements,
    analyze_skill_gap,
    build_learning_roadmap,
    compare_career_paths,
)

load_dotenv()

TOOL_REGISTRY = {
    "recommend_career_paths": recommend_career_paths,
    "get_career_requirements": get_career_requirements,
    "analyze_skill_gap": analyze_skill_gap,
    "build_learning_roadmap": build_learning_roadmap,
    "compare_career_paths": compare_career_paths,
}


def _parse_tool_action(response: str):
    match = re.search(r"Action\s*:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\[(.*)\]", response)
    if not match:
        return None, []

    tool_name = match.group(1)
    arg_text = match.group(2).strip()
    if not arg_text:
        return tool_name, []

    try:
        parsed = ast.literal_eval(f"({arg_text},)")
        if isinstance(parsed, tuple) and len(parsed) == 1 and isinstance(parsed[0], tuple):
            parsed = parsed[0]
        return tool_name, list(parsed)
    except Exception:
        # Fallback: split top-level commas only.
        parts = []
        current = []
        depth = 0
        quote = None
        for char in arg_text:
            if quote:
                current.append(char)
                if char == quote:
                    quote = None
                continue
            if char in ('"', "'"):
                quote = char
                current.append(char)
                continue
            if char in '[{(':
                depth += 1
            elif char in ']})':
                depth -= 1
            if char == ',' and depth == 0:
                part = ''.join(current).strip()
                if part:
                    parts.append(part)
                current = []
            else:
                current.append(char)
        last = ''.join(current).strip()
        if last:
            parts.append(last)
        return tool_name, [part.strip().strip('"\'') for part in parts if part.strip()]


def _run_tool(tool_name: str, args):
    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        return f"[Tool Error] Tool '{tool_name}' không tồn tại."
    try:
        return tool(*args)
    except Exception as exc:
        return f"[Tool Exception] {exc}"


def load_test_cases():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_cases.json")
    if not os.path.exists(config_path):
        return []
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """Chạy Chatbot baseline (không gọi tools)."""
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print("⚙️ System Prompt: (CHATBOT_BASELINE_PROMPT)\n")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")


def run_react_agent(user_query: str, provider):
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    history = []

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")
        prompt = user_query
        if history:
            prompt += "\n\n" + "\n".join(history)

        response = provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT)
        print(f"\n🧠 LLM Response:\n{response}")

        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:", 1)[1].strip()
            print(f"\n🏁 Final Answer:\n{final_answer}")
            return

        tool_name, args = _parse_tool_action(response)
        if not tool_name:
            print("\n❌ LLM không xuất Action hợp lệ, dừng vòng lặp.")
            print("🏁 Final Answer: Vui lòng cung cấp thêm thông tin hoặc chỉnh lại yêu cầu.")
            return

        print(f"\n🛠️ Action: {tool_name}[{', '.join(repr(a) for a in args)}]")
        observation = _run_tool(tool_name, args)
        print(f"\n👁️ Observation:\n{observation}")

        history.append("Thought: Đã phân tích và chuẩn bị gọi tool")
        history.append(f"Action: {tool_name}[{', '.join(repr(a) for a in args)}]")
        history.append(f"Observation: {observation}")

    print(f"\n⚠️ Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước.")
    print("🏁 Final Answer: Tôi cần thêm dữ liệu để tư vấn chính xác hơn.")


def run_tool_demo():
    print("\n--- TOOL DEMO: Career Guidance Tools ---")
    print("1) recommend_career_paths(...)\n")
    print(recommend_career_paths(
        interests="AI, dữ liệu",
        current_skills={"Python": 3, "SQL": 3},
        goals="Trở thành AI Engineer hoặc Data Analyst",
        riasec_profile="I",
        work_preferences=["nghiên cứu", "phân tích"],
    ))

    print("\n2) get_career_requirements('AI Engineer')\n")
    print(get_career_requirements("AI Engineer"))

    print("\n3) analyze_skill_gap('AI Engineer', {\"Python\": 3, \"SQL\": 3})\n")
    print(analyze_skill_gap("AI Engineer", {"Python": 3, "SQL": 3}))

    print("\n4) build_learning_roadmap('AI Engineer', ['Python', 'Machine Learning'], 8, duration_weeks=12)\n")
    print(build_learning_roadmap("AI Engineer", ["Python", "Machine Learning"], 8, duration_weeks=12))

    print("\n5) compare_career_paths('Data Analyst', 'AI Engineer', current_skills={\"Python\": 3, \"SQL\": 3}, interests='AI, dữ liệu', goals='Làm việc với AI')\n")
    print(compare_career_paths(
        "Data Analyst",
        "AI Engineer",
        current_skills={"Python": 3, "SQL": 3},
        interests="AI, dữ liệu",
        goals="Làm việc với AI",
    ))


def demo_run():
    provider = get_llm_provider()
    print(f"🔌 LLM Provider: {provider.__class__.__name__} (Model: {getattr(provider, 'model_name', 'N/A')})")

    tests = load_test_cases()
    if not tests:
        print("⚠️ Không tìm thấy test cases trong config/test_cases.json — vui lòng kiểm tra.")
        sample_query = "Tôi là sinh viên năm cuối ngành Hệ thống Thông tin, biết Python và SQL, thích AI. Tôi nên theo Data Analyst hay AI Engineer?"
    else:
        print(f"✅ Đã tải {len(tests)} test case(s)")
        sample_query = tests[2]["question"] if len(tests) >= 3 else tests[0]["question"]

    print("\n--- DEMO: CHATBOT BASELINE ---")
    run_baseline_chatbot(sample_query, provider)

    print("\n--- DEMO: REACT AGENT ---")
    run_react_agent(sample_query, provider)

    run_tool_demo()


if __name__ == "__main__":
    demo_run()
