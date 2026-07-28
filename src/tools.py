"""
Tool registry cho ReAct Agent định hướng sự nghiệp.

Các tool trong module này dùng dữ liệu cục bộ, không có side effect và luôn trả
về JSON string để Agent có thể đọc Observation theo một định dạng nhất quán.
"""

from __future__ import annotations

import json
import unicodedata
from typing import Any


CAREER_CATALOG = {
    "data analyst": {
        "display_name": "Data Analyst",
        "aliases": ["data analyst", "chuyen vien phan tich du lieu"],
        "description": "Thu thập, làm sạch và phân tích dữ liệu để hỗ trợ quyết định.",
        "interest_keywords": ["du lieu", "phan tich", "so lieu", "logic", "bieu do"],
        "goal_keywords": ["data", "phan tich", "bao cao", "kinh doanh"],
        "required_skills": [
            "Excel",
            "SQL",
            "Python",
            "Thống kê",
            "Trực quan hóa dữ liệu",
        ],
        "common_tasks": [
            "Làm sạch và kiểm tra chất lượng dữ liệu",
            "Viết truy vấn SQL",
            "Xây dựng dashboard và báo cáo",
            "Trình bày insight cho các bên liên quan",
        ],
    },
    "backend developer": {
        "display_name": "Backend Developer",
        "aliases": ["backend developer", "backend", "lap trinh vien backend"],
        "description": "Xây dựng API, xử lý nghiệp vụ và quản lý dữ liệu phía máy chủ.",
        "interest_keywords": ["lap trinh", "he thong", "logic", "api", "server"],
        "goal_keywords": ["backend", "phan mem", "web", "he thong"],
        "required_skills": [
            "Python",
            "Cơ sở dữ liệu",
            "REST API",
            "Git",
            "Kiểm thử phần mềm",
        ],
        "common_tasks": [
            "Thiết kế và triển khai API",
            "Xây dựng logic nghiệp vụ",
            "Làm việc với cơ sở dữ liệu",
            "Kiểm thử và tối ưu hiệu năng hệ thống",
        ],
    },
    "ui ux designer": {
        "display_name": "UI/UX Designer",
        "aliases": ["ui ux designer", "ui/ux designer", "ux designer", "ui designer"],
        "description": "Nghiên cứu người dùng và thiết kế trải nghiệm cho sản phẩm số.",
        "interest_keywords": ["thiet ke", "sang tao", "nguoi dung", "my thuat", "trai nghiem"],
        "goal_keywords": ["ui", "ux", "thiet ke", "san pham"],
        "required_skills": [
            "Figma",
            "User Research",
            "Wireframing",
            "Prototyping",
            "Thiết kế giao diện",
        ],
        "common_tasks": [
            "Nghiên cứu nhu cầu người dùng",
            "Xây dựng user flow và wireframe",
            "Thiết kế prototype",
            "Kiểm thử khả năng sử dụng",
        ],
    },
    "product manager": {
        "display_name": "Product Manager",
        "aliases": ["product manager", "quan ly san pham", "pm"],
        "description": "Xác định vấn đề sản phẩm, ưu tiên tính năng và phối hợp các nhóm.",
        "interest_keywords": ["san pham", "kinh doanh", "giao tiep", "chien luoc", "nguoi dung"],
        "goal_keywords": ["product", "quan ly", "san pham", "chien luoc"],
        "required_skills": [
            "Product Discovery",
            "Phân tích dữ liệu",
            "Giao tiếp",
            "Ưu tiên công việc",
            "Agile",
        ],
        "common_tasks": [
            "Nghiên cứu vấn đề của người dùng",
            "Xây dựng product roadmap",
            "Ưu tiên yêu cầu sản phẩm",
            "Phối hợp với thiết kế và kỹ thuật",
        ],
    },
}


def _json_response(data: dict[str, Any]) -> str:
    """Chuyển dữ liệu tool thành JSON string có thể đọc được bằng tiếng Việt."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def _normalize_text(value: Any) -> str:
    """Chuẩn hóa chữ thường và bỏ dấu để so khớp dữ liệu ổn định."""
    text = unicodedata.normalize("NFD", str(value).strip().lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def _normalize_items(value: Any) -> list[str]:
    """Chuyển chuỗi hoặc collection thành danh sách các giá trị không rỗng."""
    if isinstance(value, str):
        values = value.replace(";", ",").split(",")
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _find_career(target_role: Any) -> tuple[str, dict[str, Any]] | None:
    """Tìm một nghề trong catalog bằng tên chuẩn hoặc bí danh."""
    normalized_role = _normalize_text(target_role)
    if not normalized_role:
        return None

    for key, career in CAREER_CATALOG.items():
        aliases = {_normalize_text(key), *map(_normalize_text, career["aliases"])}
        if normalized_role in aliases:
            return key, career
    return None


def _error(message: str, **details: Any) -> str:
    """Tạo Observation lỗi có cấu trúc mà không làm Agent bị crash."""
    return _json_response({"status": "error", "error": f"LỖI: {message}", **details})


def recommend_career_paths(
    interests: list[str] | str,
    current_skills: list[str] | str,
    goals: str,
) -> str:
    """
    Đề xuất tối đa ba hướng nghề nghiệp phù hợp với hồ sơ người dùng.

    Purpose:
        Dùng khi người dùng chưa xác định nghề mục tiêu và muốn nhận gợi ý dựa
        trên sở thích, kỹ năng hiện tại và mục tiêu cá nhân.
    Args:
        interests: Danh sách hoặc chuỗi sở thích, phân tách bằng dấu phẩy.
        current_skills: Danh sách hoặc chuỗi kỹ năng hiện có.
        goals: Mục tiêu nghề nghiệp hoặc loại công việc mong muốn.
    Returns:
        JSON string gồm ``status`` và ``recommendations``. Mỗi đề xuất có tên
        nghề, điểm phù hợp 0-100 và các tín hiệu đã khớp.
    Error semantics:
        Trả JSON có ``status="error"`` nếu cả ba nhóm thông tin đều rỗng.
        Hàm không ném lỗi nghiệp vụ ra ngoài.
    Side effects:
        Không có; chỉ đọc ``CAREER_CATALOG`` cục bộ.
    Example:
        ``recommend_career_paths(["phân tích dữ liệu"], ["Excel"], "làm báo cáo")``
        đề xuất Data Analyst cùng điểm và lý do phù hợp.
    Safety:
        Kết quả chỉ là gợi ý tham khảo, không bảo đảm thành công nghề nghiệp.
    """
    interest_items = _normalize_items(interests)
    skill_items = _normalize_items(current_skills)
    goal_text = str(goals).strip() if goals is not None else ""

    if not interest_items and not skill_items and not goal_text:
        return _error(
            "Cần ít nhất một sở thích, kỹ năng hoặc mục tiêu để đề xuất nghề."
        )

    normalized_interests = " ".join(map(_normalize_text, interest_items))
    normalized_skills = {_normalize_text(skill) for skill in skill_items}
    normalized_goal = _normalize_text(goal_text)
    recommendations = []

    for career in CAREER_CATALOG.values():
        interest_matches = [
            keyword
            for keyword in career["interest_keywords"]
            if _normalize_text(keyword) in normalized_interests
        ]
        skill_matches = [
            skill
            for skill in career["required_skills"]
            if _normalize_text(skill) in normalized_skills
            or any(
                _normalize_text(skill) in submitted
                or submitted in _normalize_text(skill)
                for submitted in normalized_skills
            )
        ]
        goal_matches = [
            keyword
            for keyword in career["goal_keywords"]
            if _normalize_text(keyword) in normalized_goal
        ]

        score = min(
            100,
            20
            + min(35, len(interest_matches) * 15)
            + min(30, len(skill_matches) * 10)
            + min(15, len(goal_matches) * 15),
        )
        recommendations.append(
            {
                "role": career["display_name"],
                "match_score": score,
                "matched_interests": interest_matches,
                "matched_skills": skill_matches,
                "matched_goals": goal_matches,
            }
        )

    recommendations.sort(key=lambda item: (-item["match_score"], item["role"]))
    return _json_response(
        {
            "status": "success",
            "recommendations": recommendations[:3],
            "disclaimer": "Điểm phù hợp chỉ mang tính tham khảo từ dữ liệu đã cung cấp.",
        }
    )


def get_career_requirements(target_role: str) -> str:
    """
    Tra cứu mô tả, nhiệm vụ và kỹ năng cần thiết của một nghề.

    Purpose:
        Dùng khi người dùng đã nêu một nghề cụ thể và cần dữ liệu có căn cứ về
        nghề đó; không dùng để đánh giá mức độ phù hợp cá nhân.
    Args:
        target_role: Tên nghề hoặc bí danh, ví dụ ``"Data Analyst"``.
    Returns:
        JSON string chứa tên nghề, mô tả, kỹ năng bắt buộc và nhiệm vụ phổ biến.
    Error semantics:
        Trả JSON lỗi và danh sách nghề được hỗ trợ nếu tên nghề rỗng hoặc không
        tồn tại trong catalog.
    Side effects:
        Không có; chỉ đọc ``CAREER_CATALOG`` cục bộ.
    Example:
        ``get_career_requirements("Data Analyst")`` trả yêu cầu về SQL, Excel,
        Python, thống kê và trực quan hóa dữ liệu.
    Safety:
        Không suy diễn mức lương, cơ hội việc làm hoặc dữ liệu ngoài catalog.
    """
    result = _find_career(target_role)
    if result is None:
        return _error(
            f"Không tìm thấy nghề '{target_role}'.",
            supported_roles=[
                career["display_name"] for career in CAREER_CATALOG.values()
            ],
        )

    _, career = result
    return _json_response(
        {
            "status": "success",
            "role": career["display_name"],
            "description": career["description"],
            "required_skills": career["required_skills"],
            "common_tasks": career["common_tasks"],
        }
    )


def analyze_skill_gap(
    target_role: str,
    current_skills: list[str] | str,
) -> str:
    """
    So sánh kỹ năng hiện tại với yêu cầu của nghề mục tiêu.

    Purpose:
        Dùng sau khi đã xác định nghề mục tiêu để tìm kỹ năng đã có, kỹ năng
        còn thiếu và dữ liệu đầu vào cho tool tạo learning roadmap.
    Args:
        target_role: Nghề cần phân tích.
        current_skills: Danh sách hoặc chuỗi kỹ năng hiện tại.
    Returns:
        JSON string gồm ``existing_skills``, ``missing_skills`` và
        ``readiness_score`` từ 0 đến 100.
    Error semantics:
        Trả JSON lỗi nếu nghề không tồn tại hoặc danh sách kỹ năng rỗng.
    Side effects:
        Không có; phép so sánh là deterministic trên catalog cục bộ.
    Example:
        ``analyze_skill_gap("Data Analyst", ["Excel", "Python"])`` xác định SQL,
        thống kê và trực quan hóa dữ liệu là các kỹ năng còn thiếu.
    Safety:
        Điểm sẵn sàng chỉ phản ánh độ phủ kỹ năng trong catalog, không phải kết
        luận tuyển dụng hay đánh giá năng lực toàn diện.
    """
    result = _find_career(target_role)
    if result is None:
        return _error(
            f"Không tìm thấy nghề '{target_role}'.",
            supported_roles=[
                career["display_name"] for career in CAREER_CATALOG.values()
            ],
        )

    skill_items = _normalize_items(current_skills)
    if not skill_items:
        return _error("Cần cung cấp ít nhất một kỹ năng hiện tại.")

    _, career = result
    normalized_current = {_normalize_text(skill) for skill in skill_items}
    existing_skills = []
    missing_skills = []

    for required_skill in career["required_skills"]:
        normalized_required = _normalize_text(required_skill)
        has_skill = any(
            normalized_required in current or current in normalized_required
            for current in normalized_current
        )
        if has_skill:
            existing_skills.append(required_skill)
        else:
            missing_skills.append(required_skill)

    readiness_score = round(
        len(existing_skills) / len(career["required_skills"]) * 100
    )
    return _json_response(
        {
            "status": "success",
            "role": career["display_name"],
            "existing_skills": existing_skills,
            "missing_skills": missing_skills,
            "readiness_score": readiness_score,
            "disclaimer": "Điểm sẵn sàng chỉ dựa trên danh sách kỹ năng đã khai báo.",
        }
    )


def build_learning_roadmap(
    target_role: str,
    missing_skills: list[str] | str,
    weekly_hours: int,
    duration_weeks: int = 8,
) -> str:
    """
    Tạo lộ trình học theo nghề mục tiêu và các kỹ năng còn thiếu.

    Purpose:
        Dùng sau ``analyze_skill_gap`` khi Agent đã có nghề mục tiêu, danh sách
        kỹ năng cần học và quỹ thời gian của người dùng.
    Args:
        target_role: Nghề mục tiêu.
        missing_skills: Danh sách hoặc chuỗi kỹ năng còn thiếu.
        weekly_hours: Số giờ người dùng có thể học mỗi tuần, từ 1 đến 40.
        duration_weeks: Số tuần của lộ trình, từ 1 đến 52; mặc định là 8.
    Returns:
        JSON string gồm kế hoạch theo tuần, chủ đề, thời lượng và đầu ra kỳ vọng.
    Error semantics:
        Trả JSON lỗi nếu nghề không tồn tại, kỹ năng rỗng, thời gian không phải
        số nguyên hoặc nằm ngoài giới hạn. Hàm không crash với input nghiệp vụ.
    Side effects:
        Không có; lộ trình được tạo deterministic và không ghi file.
    Example:
        ``build_learning_roadmap("Data Analyst", ["SQL", "Thống kê"], 6, 4)``
        tạo bốn tuần học với sáu giờ mỗi tuần.
    Safety:
        Lộ trình là gợi ý học tập, không bảo đảm kết quả tuyển dụng.
    """
    result = _find_career(target_role)
    if result is None:
        return _error(
            f"Không tìm thấy nghề '{target_role}'.",
            supported_roles=[
                career["display_name"] for career in CAREER_CATALOG.values()
            ],
        )

    skill_items = _normalize_items(missing_skills)
    if not skill_items:
        return _error("Cần ít nhất một kỹ năng còn thiếu để tạo lộ trình.")

    try:
        hours = int(weekly_hours)
        weeks = int(duration_weeks)
    except (TypeError, ValueError):
        return _error("weekly_hours và duration_weeks phải là số nguyên.")

    if not 1 <= hours <= 40:
        return _error("weekly_hours phải nằm trong khoảng từ 1 đến 40.")
    if not 1 <= weeks <= 52:
        return _error("duration_weeks phải nằm trong khoảng từ 1 đến 52.")

    _, career = result
    roadmap = []
    for week in range(1, weeks + 1):
        skill_index = min((week - 1) * len(skill_items) // weeks, len(skill_items) - 1)
        skill = skill_items[skill_index]
        roadmap.append(
            {
                "week": week,
                "focus_skill": skill,
                "study_hours": hours,
                "expected_output": f"Hoàn thành một bài thực hành về {skill}.",
            }
        )

    return _json_response(
        {
            "status": "success",
            "role": career["display_name"],
            "duration_weeks": weeks,
            "weekly_hours": hours,
            "roadmap": roadmap,
            "disclaimer": "Có thể điều chỉnh lộ trình theo tiến độ thực tế.",
        }
    )


def compare_career_paths(
    career_a: str,
    career_b: str,
    current_skills: list[str] | str = (),
) -> str:
    """
    So sánh hai hướng nghề nghiệp bằng dữ liệu trong career catalog.

    Purpose:
        Dùng khi người dùng đang phân vân giữa hai nghề và cần thấy điểm giống,
        điểm khác cùng mức độ khớp với các kỹ năng hiện tại.
    Args:
        career_a: Tên nghề thứ nhất.
        career_b: Tên nghề thứ hai.
        current_skills: Danh sách hoặc chuỗi kỹ năng hiện tại; có thể để trống
            nếu người dùng chỉ muốn so sánh yêu cầu chung.
    Returns:
        JSON string gồm mô tả từng nghề, kỹ năng chung, kỹ năng riêng và tỷ lệ
        kỹ năng hiện tại khớp với yêu cầu của mỗi nghề.
    Error semantics:
        Trả JSON lỗi nếu một nghề không tồn tại hoặc hai đầu vào chỉ cùng một
        nghề. Hàm không ném lỗi nghiệp vụ ra ngoài.
    Side effects:
        Không có; chỉ đọc ``CAREER_CATALOG`` cục bộ.
    Example:
        ``compare_career_paths("Data Analyst", "Backend Developer",
        ["Python", "Excel"])`` trả các yêu cầu chung, yêu cầu riêng và điểm khớp.
    Safety:
        Tool không so sánh lương, nhu cầu tuyển dụng hoặc cơ hội thị trường vì
        catalog hiện không chứa dữ liệu có nguồn cho các thông tin đó.
    """
    result_a = _find_career(career_a)
    result_b = _find_career(career_b)
    supported_roles = [
        career["display_name"] for career in CAREER_CATALOG.values()
    ]

    if result_a is None:
        return _error(
            f"Không tìm thấy nghề thứ nhất '{career_a}'.",
            supported_roles=supported_roles,
        )
    if result_b is None:
        return _error(
            f"Không tìm thấy nghề thứ hai '{career_b}'.",
            supported_roles=supported_roles,
        )

    key_a, data_a = result_a
    key_b, data_b = result_b
    if key_a == key_b:
        return _error("Cần cung cấp hai nghề khác nhau để so sánh.")

    skills_a = {
        _normalize_text(skill): skill for skill in data_a["required_skills"]
    }
    skills_b = {
        _normalize_text(skill): skill for skill in data_b["required_skills"]
    }
    common_keys = set(skills_a) & set(skills_b)
    current = {
        _normalize_text(skill) for skill in _normalize_items(current_skills)
    }

    def matched_skills(career_skills: dict[str, str]) -> list[str]:
        return [
            display_name
            for normalized, display_name in career_skills.items()
            if any(
                normalized in submitted or submitted in normalized
                for submitted in current
            )
        ]

    matched_a = matched_skills(skills_a)
    matched_b = matched_skills(skills_b)
    score_a = round(len(matched_a) / len(skills_a) * 100) if current else None
    score_b = round(len(matched_b) / len(skills_b) * 100) if current else None

    return _json_response(
        {
            "status": "success",
            "common_required_skills": sorted(
                (skills_a[key] for key in common_keys),
                key=_normalize_text,
            ),
            "careers": [
                {
                    "role": data_a["display_name"],
                    "description": data_a["description"],
                    "unique_required_skills": [
                        skill
                        for key, skill in skills_a.items()
                        if key not in common_keys
                    ],
                    "matched_current_skills": matched_a,
                    "skill_match_score": score_a,
                },
                {
                    "role": data_b["display_name"],
                    "description": data_b["description"],
                    "unique_required_skills": [
                        skill
                        for key, skill in skills_b.items()
                        if key not in common_keys
                    ],
                    "matched_current_skills": matched_b,
                    "skill_match_score": score_b,
                },
            ],
            "disclaimer": (
                "So sánh chỉ dựa trên yêu cầu kỹ năng trong catalog, "
                "không phản ánh toàn bộ cơ hội nghề nghiệp."
            ),
        }
    )


# Registry duy nhất để Agent kiểm tra và thực thi Action hợp lệ.
AVAILABLE_TOOLS = {
    "recommend_career_paths": recommend_career_paths,
    "get_career_requirements": get_career_requirements,
    "analyze_skill_gap": analyze_skill_gap,
    "build_learning_roadmap": build_learning_roadmap,
    "compare_career_paths": compare_career_paths,
}
