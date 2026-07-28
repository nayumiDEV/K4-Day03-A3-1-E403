"""
WEB APP - Career Guidance Chatbot (Flask + Neo-brutalism UI)
Single flow: MBTI test -> Agent-led Q&A -> Career recommendation via tools.py
"""

import json
import os
import sys
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from tools import AVAILABLE_TOOLS, recommend_career_paths, get_career_requirements, analyze_skill_gap, build_learning_roadmap, compare_career_paths, get_mbti_profile, analyze_career_profile
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "neo-brutalism-career-dev")
app.config['TEMPLATE_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

MBTI_QUESTIONS = [
    {"id": 1, "question": "Bạn cảm thấy tràn đầy năng lượng sau khi?", "option_a": "Gặp gỡ và trò chuyện với nhiều người", "option_b": "Có thời gian yên tĩnh một mình", "trait": "E-I"},
    {"id": 2, "question": "Khi học điều mới, bạn thích?", "option_a": "Thực hành, làm thử ngay", "option_b": "Suy nghĩ, đọc lý thuyết trước", "trait": "S-N"},
    {"id": 3, "question": "Điều gì thuyết phục bạn hơn khi đưa ra quyết định?", "option_a": "Số liệu, logic và phân tích", "option_b": "Cảm nhận, giá trị và tác động đến con người", "trait": "T-F"},
    {"id": 4, "question": "Bạn thích công việc được tổ chức theo kiểu?", "option_a": "Có kế hoạch, lịch trình rõ ràng", "option_b": "Linh hoạt, tùy hứng theo tình huống", "trait": "J-P"},
    {"id": 5, "question": "Trong nhóm, bạn thường?", "option_a": "Chủ động nói ý kiến và kết nối mọi người", "option_b": "Lắng nghe và đóng góp khi được hỏi", "trait": "E-I"},
    {"id": 6, "question": "Bạn chú ý đến điều gì trước tiên?", "option_a": "Chi tiết cụ thể, thực tế trước mắt", "option_b": "Bức tranh tổng thể, ý nghĩa sâu xa", "trait": "S-N"},
    {"id": 7, "question": "Bạn đánh giá thành công dựa trên?", "option_a": "Kết quả đo lường được, mục tiêu đạt được", "option_b": "Sự hài lòng, mối quan hệ và ý nghĩa công việc", "trait": "T-F"},
    {"id": 8, "question": "Khi đối mặt với deadline, bạn?", "option_a": "Lên kế hoạch và hoàn thành sớm", "option_b": "Làm dần và thường hoàn thành sát giờ", "trait": "J-P"},
    {"id": 9, "question": "Môi trường làm việc lý tưởng của bạn là?", "option_a": "Năng động, nhiều người, trao đổi liên tục", "option_b": "Yên tĩnh, tập trung, ít bị làm phiền", "trait": "E-I"},
    {"id": 10, "question": "Bạn tin tưởng vào điều gì hơn?", "option_a": "Kinh nghiệm thực tế và những gì đã kiểm chứng", "option_b": "Trực giác và những khả năng tiềm ẩn", "trait": "S-N"},
    {"id": 11, "question": "Bạn thường giải quyết xung đột bằng cách?", "option_a": "Phân tích khách quan, tìm giải pháp công bằng", "option_b": "Thấu hiểu cảm xúc, tìm sự đồng thuận", "trait": "T-F"},
    {"id": 12, "question": "Bạn mô tả bản thân là người?", "option_a": "Có tổ chức, thích sự ổn định", "option_b": "Linh hoạt, thích khám phá", "trait": "J-P"},
    {"id": 13, "question": "Sau một tuần làm việc, bạn muốn?", "option_a": "Đi chơi, gặp bạn bè, tham gia sự kiện", "option_b": "Ở nhà đọc sách, xem phim hoặc sở thích cá nhân", "trait": "E-I"},
    {"id": 14, "question": "Khi đọc hướng dẫn, bạn?", "option_a": "Đọc kỹ từng bước trước khi làm", "option_b": "Đọc lướt và bắt tay vào làm luôn", "trait": "S-N"},
    {"id": 15, "question": "Phong cách giao tiếp của bạn?", "option_a": "Thẳng thắn, đi thẳng vào vấn đề", "option_b": "Tế nhị, khéo léo, chú ý cảm xúc", "trait": "T-F"},
    {"id": 16, "question": "Bạn cảm thấy thế nào về thay đổi?", "option_a": "Thích sự ổn định, thay đổi có kế hoạch", "option_b": "Hào hứng với sự mới mẻ, bất ngờ", "trait": "J-P"},
    {"id": 17, "question": "Bạn thích giải quyết vấn đề bằng cách?", "option_a": "Thảo luận nhóm, brainstorming", "option_b": "Suy nghĩ độc lập, tự tìm giải pháp", "trait": "E-I"},
    {"id": 18, "question": "Bạn thích làm việc với?", "option_a": "Số liệu, quy trình, công cụ cụ thể", "option_b": "Ý tưởng, khái niệm, mô hình trừu tượng", "trait": "S-N"},
    {"id": 19, "question": "Lời khen nào có ý nghĩa nhất với bạn?", "option_a": "Bạn thật thông minh và lý trí", "option_b": "Bạn thật ấm áp và quan tâm", "trait": "T-F"},
    {"id": 20, "question": "Bạn thích cuối tuần của mình?", "option_a": "Được lên lịch trước với các hoạt động cụ thể", "option_b": "Tự do làm theo cảm hứng không kế hoạch", "trait": "J-P"},
]


AGENT_QUESTIONS = [
    {"id": "interests", "question": "Bạn có sở thích gì liên quan đến công việc? Hãy kể ra một vài lĩnh vực bạn thấy hứng thú (ví dụ: phân tích dữ liệu, lập trình, thiết kế, viết lách, kinh doanh...).", "placeholder": "Nhập sở thích, cách nhau bằng dấu phẩy"},
    {"id": "skills", "question": "Bạn đang có những kỹ năng gì? Hãy liệt kê các kỹ năng bạn đã học được hoặc có kinh nghiệm (ví dụ: Python, Excel, Figma, SQL, Giao tiếp, Quản lý...).", "placeholder": "Nhập kỹ năng, cách nhau bằng dấu phẩy"},
    {"id": "goals", "question": "Mục tiêu nghề nghiệp của bạn trong 1-3 năm tới là gì? Bạn muốn làm công việc như thế nào?", "placeholder": "Ví dụ: muốn làm việc với dữ liệu, phát triển web, quản lý dự án..."},
    {"id": "education", "question": "Bạn đang học ngành gì hoặc đã tốt nghiệp ngành nào? Điều này giúp tôi đề xuất hướng đi phù hợp hơn.", "placeholder": "Ví dụ: Công nghệ thông tin, Kinh tế, Thiết kế..."},
    {"id": "experience", "question": "Bạn đã có kinh nghiệm làm việc gì chưa? Có thể là thực tập, làm thêm, hay dự án cá nhân.", "placeholder": "Ví dụ: 1 năm thực tập IT, từng làm freelance thiết kế..."},
    {"id": "workstyle", "question": "Bạn thích làm việc theo nhóm hay độc lập? Môi trường văn phòng hay làm từ xa?", "placeholder": "Ví dụ: thích làm nhóm, linh hoạt, văn phòng..."},
]

AGENT_SESSIONS = {}


def _get_question_for_mbti(mbti_type, dim1, dim2):
    mbti_questions = {
        "E": "Bạn là người hướng ngoại, thích giao tiếp. Bạn có muốn công việc liên quan nhiều đến gặp gỡ đối tác, thuyết trình hay làm việc nhóm không?",
        "I": "Bạn là người hướng nội, thích làm việc độc lập. Bạn có muốn công việc thiên về nghiên cứu, phân tích hay phát triển sản phẩm không?",
        "S": "Bạn thuộc nhóm thực tế, thích chi tiết cụ thể. Bạn có hứng thú với các công việc có quy trình rõ ràng, xử lý số liệu hay vận hành hệ thống?",
        "N": "Bạn thuộc nhóm trực giác, thích nhìn bức tranh lớn. Bạn có muốn công việc thiên về chiến lược, sáng tạo ý tưởng hay nghiên cứu xu hướng?",
        "T": "Bạn thuộc nhóm lý trí, thích quyết định dựa trên dữ liệu. Bạn có phù hợp với các công việc phân tích, kỹ thuật hay tối ưu quy trình?",
        "F": "Bạn thuộc nhóm cảm xúc, thấu hiểu và quan tâm đến người khác. Bạn có muốn công việc liên quan đến hỗ trợ, tư vấn, đào tạo hay chăm sóc khách hàng?",
        "J": "Bạn thuộc nhóm nguyên tắc, thích có kế hoạch. Bạn có hứng thú với quản lý dự án, điều phối công việc hay vận hành theo quy trình?",
        "P": "Bạn thuộc nhóm linh hoạt, thích thích nghi nhanh. Bạn có phù hợp với môi trường startup, công việc sáng tạo hay giải quyết vấn đề đa dạng?",
    }
    result = []
    for letter in [dim1, dim2]:
        if letter in mbti_questions:
            result.append(mbti_questions[letter])
    return result


def _generate_next_question(session):
    step = session.get("step", 0)
    fixed_count = len(AGENT_QUESTIONS)

    if step < fixed_count:
        q = AGENT_QUESTIONS[step]
        session["current_context"] = q["id"]
        is_last = step == fixed_count - 1
        return {
            "type": "question",
            "id": q["id"],
            "question": q["question"],
            "placeholder": q["placeholder"],
            "step": step,
            "total": fixed_count,
            "is_last": is_last,
        }

    session["current_context"] = "finalize"
    return {"type": "finalize", "step": step, "total": fixed_count, "is_last": True}


@app.route("/api/agent/start", methods=["POST"])
def agent_start():
    data = request.get_json()
    mbti_type = data.get("mbti_type", "").strip().upper()
    session_id = len(AGENT_SESSIONS) + 1

    dim1 = mbti_type[0] if len(mbti_type) > 0 else "E"
    dim2 = mbti_type[1] if len(mbti_type) > 1 else "S"
    mbti_qs = _get_question_for_mbti(mbti_type, dim1, dim2)

    session = {
        "id": session_id,
        "mbti_type": mbti_type,
        "step": 0,
        "answers": {},
        "current_context": "",
    }
    AGENT_SESSIONS[session_id] = session
    next_q = _generate_next_question(session)
    return jsonify({
        "session_id": session_id,
        "messages": mbti_qs,
        "next": next_q,
    })


@app.route("/api/agent/answer", methods=["POST"])
def agent_answer():
    data = request.get_json()
    session_id = data.get("session_id")
    answer = data.get("answer", "").strip()

    session = AGENT_SESSIONS.get(session_id)
    if not session:
        return jsonify({"error": "Phiên làm việc không tồn tại"}), 400

    context = session.get("current_context", "")
    question_ids = [q["id"] for q in AGENT_QUESTIONS]
    if context in question_ids:
        session["answers"][context] = answer

    session["step"] = session.get("step", 0) + 1
    next_q = _generate_next_question(session)

    if next_q["type"] == "finalize":
        answers = session["answers"]
        mbti_type = session["mbti_type"]
        try:
            result = json.loads(
                analyze_career_profile(
                    mbti_type,
                    answers.get("interests", ""),
                    answers.get("skills", ""),
                    answers.get("goals", ""),
                )
            )
        except Exception as e:
            result = {"status": "error", "error": {"message": str(e)}}

        del AGENT_SESSIONS[session_id]
        return jsonify({"type": "result", "result": result})

    return jsonify({"next": next_q})


def _parse_mbti_result(answers):
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    first_letter_map = {1: "E", 2: "S", 3: "T", 4: "J", 5: "E", 6: "S", 7: "T", 8: "J", 9: "E", 10: "S", 11: "T", 12: "J", 13: "E", 14: "S", 15: "T", 16: "J", 17: "E", 18: "S", 19: "T", 20: "J"}
    second_letter_map = {1: "I", 2: "N", 3: "F", 4: "P", 5: "I", 6: "N", 7: "F", 8: "P", 9: "I", 10: "N", 11: "F", 12: "P", 13: "I", 14: "N", 15: "F", 16: "P", 17: "I", 18: "N", 19: "F", 20: "P"}

    for qid_str, choice in answers.items():
        if not qid_str.isdigit():
            continue
        qid = int(qid_str)
        if choice == "a":
            scores[first_letter_map[qid]] += 1
        else:
            scores[second_letter_map[qid]] += 1

    mbti = ""
    mbti += "E" if scores["E"] >= scores["I"] else "I"
    mbti += "S" if scores["S"] >= scores["N"] else "N"
    mbti += "T" if scores["T"] >= scores["F"] else "F"
    mbti += "J" if scores["J"] >= scores["P"] else "P"

    return mbti, scores


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mbti")
def mbti():
    return render_template("mbti.html", questions=MBTI_QUESTIONS)


@app.route("/mbti/result", methods=["POST"])
def mbti_result():
    form = request.form.to_dict()
    mbti_type, scores = _parse_mbti_result(form)
    mbti_data = json.loads(get_mbti_profile(mbti_type))

    interests = form.get("interests", "").strip()
    skills = form.get("skills", "").strip()
    goals = form.get("goals", "").strip()

    profile_result = None
    profile_error = None

    if interests or skills or goals:
        try:
            profile_result = json.loads(
                analyze_career_profile(mbti_type, interests, skills, goals)
            )
        except Exception as e:
            profile_error = str(e)

    details = {
        "E": {"label": "Hướng ngoại (E)", "score": scores["E"], "max": scores["E"] + scores["I"]},
        "I": {"label": "Hướng nội (I)", "score": scores["I"], "max": scores["E"] + scores["I"]},
        "S": {"label": "Thực tế (S)", "score": scores["S"], "max": scores["S"] + scores["N"]},
        "N": {"label": "Trực giác (N)", "score": scores["N"], "max": scores["S"] + scores["N"]},
        "T": {"label": "Lý trí (T)", "score": scores["T"], "max": scores["T"] + scores["F"]},
        "F": {"label": "Cảm xúc (F)", "score": scores["F"], "max": scores["T"] + scores["F"]},
        "J": {"label": "Nguyên tắc (J)", "score": scores["J"], "max": scores["J"] + scores["P"]},
        "P": {"label": "Linh hoạt (P)", "score": scores["P"], "max": scores["J"] + scores["P"]},
    }

    mbti_info = mbti_data.get("data", {})

    return render_template(
        "mbti_result.html",
        mbti_type=mbti_type,
        mbti_info=mbti_info,
        details=details,
        profile_result=profile_result,
        profile_error=profile_error,
        user_interests=interests,
        user_skills=skills,
        user_goals=goals,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("CAREER GUIDANCE CHATBOT - GIAO DIEN WEB")
    print("=" * 60)
    print("Đang khởi động Flask server...")
    print("Mở: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
